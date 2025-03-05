from datetime import datetime
import asyncio
from flask import render_template, jsonify, current_app
from app.main import bp
from app.utils.async_utils import async_route

@bp.route('/')
@async_route
async def index():
    """Landing page."""
    return render_template('main/index.html')

@bp.route('/health')
@async_route
async def health_check():
    """Health check endpoint for Render"""
    from app import db
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        db.session.commit()
        
        # Check Redis connection if configured
        redis_status = "not_configured"
        if current_app.config.get('UPSTASH_REDIS_REST_URL'):
            try:
                redis_manager = current_app.redis
                if redis_manager:
                    ping_result = await redis_manager.ping()
                    redis_status = "connected" if ping_result else "error: ping failed"
            except Exception as e:
                redis_status = f"error: {str(e)}"
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'redis': redis_status,
            'env': current_app.config['FLASK_ENV'],
            'version': current_app.config.get('VERSION', '1.0.0')
        }), 200
    except Exception as e:
        current_app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
