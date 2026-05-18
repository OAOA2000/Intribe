from .ai import ai_bp
from .dashboard import dashboard_bp
from .events import events_bp
from .health import health_bp
from .messages import messages_bp
from .posts import comments_bp, posts_bp
from .profiles import profiles_bp
from .tribes import tribes_bp


def register_blueprints(app):
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(profiles_bp, url_prefix="/api/profile")
    app.register_blueprint(tribes_bp, url_prefix="/api/tribes")
    app.register_blueprint(events_bp, url_prefix="/api/events")
    app.register_blueprint(messages_bp, url_prefix="/api/messages")
    app.register_blueprint(posts_bp, url_prefix="/api/posts")
    app.register_blueprint(comments_bp, url_prefix="/api/comments")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")
