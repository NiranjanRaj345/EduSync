import pickle
from uuid import uuid4
from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict

class RedisSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None, permanent=None):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        if permanent:
            self.permanent = permanent
        self.modified = False

class RedisSessionInterface(SessionInterface):
    def __init__(self, redis, prefix='session:'):
        self.redis = redis
        self.prefix = prefix

    def generate_sid(self):
        return str(uuid4())

    def get_redis_expiration_time(self, app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        return None

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self.generate_sid()
            return RedisSession(sid=sid)
        
        try:
            val = self.redis.get(self.prefix + sid)
            if val is None:
                return RedisSession(sid=sid)
            data = pickle.loads(val)
            return RedisSession(data, sid=sid)
        except:
            return RedisSession(sid=sid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        
        if not session:
            if session.modified:
                self.redis.delete(self.prefix + session.sid)
                response.delete_cookie(app.session_cookie_name,
                                    domain=domain, path=path)
            return

        # Set Redis expiration
        redis_exp = self.get_redis_expiration_time(app, session)
        cookie_exp = self.get_expiration_time(app, session)
        
        val = pickle.dumps(dict(session))
        self.redis.setex(name=self.prefix + session.sid,
                        time=int(redis_exp.total_seconds()),
                        value=val)

        response.set_cookie(app.session_cookie_name, session.sid,
                          expires=cookie_exp, httponly=True,
                          domain=domain, path=path, secure=True,
                          samesite='Lax')
