import json
import logging
from datetime import datetime, timedelta
from uuid import uuid4
import asyncio
from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict
from itsdangerous import Signer, BadSignature, want_bytes

logger = logging.getLogger(__name__)

class RedisSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None, permanent=None):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        if permanent:
            self.permanent = permanent
        self.modified = False

class UpstashRedisSessionInterface(SessionInterface):
    serializer = json
    session_class = RedisSession

    def __init__(self, redis, app, key_prefix='session:', use_signer=True, permanent=True):
        self.redis_manager = redis  # This is now the RedisManager instance
        self.app = app
        self.key_prefix = key_prefix
        self.use_signer = use_signer
        self.permanent = permanent
        self._loop = None
        if not app.secret_key:
            raise RuntimeError('The session is unavailable because no secret '
                             'key was set. Set the secret_key on the '
                             'application to something unique and secret.')
        self.signer = Signer(app.secret_key, salt='flask-session', key_derivation='hmac')
        logger.debug(f"Initialized session interface with key_prefix={key_prefix}, use_signer={use_signer}")

    def _should_regenerate(self, session):
        """Check if session should be regenerated for security."""
        if not session:
            return False
        should_regen = session.get('_fresh', False) or session.get('_user_id', None) != session.get('_last_user_id', None)
        if should_regen:
            logger.debug(f"Session regeneration required for user_id={session.get('_user_id')}")
        return should_regen

    def _regenerate_sid(self, session):
        """Regenerate session ID to prevent session fixation."""
        old_sid = self.key_prefix + session.sid
        new_sid = self.key_prefix + self._generate_sid()
        session['_last_user_id'] = session.get('_user_id')
        
        logger.debug(f"Regenerating session - old_sid={old_sid}, new_sid={new_sid}")
        
        # Get current session data
        val = self.serializer.dumps(dict(session))
        
        # Atomically recreate session with new ID
        try:
            loop = self._get_or_create_event_loop()
            success = loop.run_until_complete(asyncio.ensure_future(
                self.redis_manager.recreate_session(old_sid, new_sid, val)
            ))
            logger.debug(f"Session regeneration {'succeeded' if success else 'failed'}")
        except Exception as e:
            logger.error(f"Session regeneration failed: {str(e)}")
            success = False
        
        if success:
            session.sid = new_sid.replace(self.key_prefix, '', 1)  # Remove prefix for cookie
        else:
            logger.warning(f"Failed to regenerate session ID for user {session.get('user_id')}")

    def _get_or_create_event_loop(self):
        """Get existing event loop or create a new one"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Event loop is closed")
            return loop
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    def open_session(self, app, request):
        """Open a Flask session."""
        sid = request.cookies.get(app.config['SESSION_COOKIE_NAME'])
        logger.debug(f"Opening session - cookie_sid={sid}")
        
        if not app.secret_key:
            return None

        if not sid:
            sid = self._generate_sid()
            logger.debug(f"New session created with sid={sid}")
            return self.session_class(sid=sid, permanent=self.permanent)

        if self.use_signer:
            try:
                sid_as_bytes = self.signer.unsign(sid)
                sid = sid_as_bytes.decode()
                logger.debug(f"Unsigned session ID: {sid}")
            except BadSignature:
                logger.warning("Invalid session signature, creating new session")
                sid = self._generate_sid()
                return self.session_class(sid=sid, permanent=self.permanent)

        loop = self._get_or_create_event_loop()
        try:
            logger.debug(f"Fetching session data for sid={sid}")
            coro = asyncio.ensure_future(self.redis_manager.get(self.key_prefix + sid))
            val = loop.run_until_complete(coro)
        except Exception as e:
            logger.error(f"Failed to get session data: {str(e)}")
            val = None
        
        if val is not None:
            try:
                data = self.serializer.loads(val)
                logger.debug(f"Loaded session data: user_id={data.get('user_id')}, fresh={data.get('_fresh')}")
                session = self.session_class(data, sid=sid)
                if self._should_regenerate(session):
                    self._regenerate_sid(session)
                return session
            except Exception as e:
                logger.error(f"Failed to load session data: {str(e)}")
                return self.session_class(sid=self._generate_sid(), permanent=self.permanent)
        return self.session_class(sid=self._generate_sid(), permanent=self.permanent)

    def save_session(self, app, session, response):
        domain = self._get_domain(app)
        path = self.get_cookie_path(app)

        # Don't save if permanent=False and we're not in a permanent session
        if not session.permanent and not self.permanent:
            logger.debug("Non-permanent session, deleting")
            return self.delete_session(app, session, response)
        
        if not session:
            if session.modified:
                logger.debug("Empty modified session, deleting")
                try:
                    loop = self._get_or_create_event_loop()
                    coro = asyncio.ensure_future(self.redis_manager.delete(self.key_prefix + session.sid))
                    loop.run_until_complete(coro)
                except Exception as e:
                    logger.error(f"Failed to delete null session: {str(e)}")
                finally:
                    response.delete_cookie(app.config['SESSION_COOKIE_NAME'], 
                                        domain=domain, 
                                        path=path,
                                        httponly=True,
                                        secure=self.get_cookie_secure(app),
                                        samesite=self.get_cookie_samesite(app))
            return

        # Avoid empty sessions
        if not session or not session.modified:
            logger.debug("Session not modified, skipping save")
            return

        # Set session expiry (minimum 5 minutes, maximum 30 days)
        lifetime = app.permanent_session_lifetime
        if isinstance(lifetime, timedelta):
            expiry = max(300, min(int(lifetime.total_seconds()), 2592000))
        else:
            expiry = 86400  # Default to 1 day
        
        val = self.serializer.dumps(dict(session))
        sid = session.sid
        logger.debug(f"Saving session - sid={sid}, expiry={expiry}s")

        if self.use_signer:
            sid = self.signer.sign(want_bytes(sid)).decode('utf-8')

        response.set_cookie(app.config['SESSION_COOKIE_NAME'], sid,
                          expires=self.get_expiration_time(app, session),
                          httponly=self.get_cookie_httponly(app),
                          domain=domain,
                          path=path,
                          secure=self.get_cookie_secure(app),
                          samesite=self.get_cookie_samesite(app))

        loop = self._get_or_create_event_loop()
        try:
            expiry = expiry or 86400  # Default to 1 day if not specified
            coro = asyncio.ensure_future(self.redis_manager.set(self.key_prefix + session.sid, val, ex=expiry))
            loop.run_until_complete(coro)
            logger.debug(f"Session saved successfully with expiry={expiry}s")
        except Exception as e:
            logger.error(f"Failed to save session data: {str(e)}")

    def _generate_sid(self):
        """Generate a unique session ID."""
        return str(uuid4())

    def _get_domain(self, app):
        """Get cookie domain."""
        rv = app.config.get('SESSION_COOKIE_DOMAIN')
        if rv is not None:
            return rv if rv else None
        rv = app.config.get('SERVER_NAME')
        if not rv:
            return None
        if ':' in rv:
            rv = rv.rsplit(':', 1)[0]
        return rv if rv else None

    def delete_session(self, app, session, response):
        """Delete the current session."""
        domain = self._get_domain(app)
        path = self.get_cookie_path(app)
        
        try:
            loop = self._get_or_create_event_loop()
            if session.sid:
                logger.debug(f"Deleting session - sid={session.sid}")
                coro = asyncio.ensure_future(self.redis_manager.delete(self.key_prefix + session.sid))
                loop.run_until_complete(coro)
                logger.debug("Session deleted successfully")
        except Exception as e:
            logger.error(f"Failed to delete session data: {str(e)}")
        
        response.delete_cookie(app.config['SESSION_COOKIE_NAME'],
                             domain=domain,
                             path=path,
                             httponly=True,
                             secure=self.get_cookie_secure(app),
                             samesite=self.get_cookie_samesite(app))
