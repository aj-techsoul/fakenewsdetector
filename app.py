"""
app.py — Fake News AI Application Entry Point
==============================================
Main executable script that configures database models, Flask-Login,
security blueprints, server routes, static serving of file uploads,
and auto-generates the administrator profile if missing.
"""

import os
from flask import Flask, send_from_directory
from flask_login import LoginManager

from database_models import db
from database_models.user import User
from authentication.auth import auth_bp
from routes import main_bp
from ai.predictor import load_predictor
from authentication.security import hash_password

# Create standard directories on startup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for d in ['dataset', 'database', 'models', 'reports', 'uploads', 'exports', 'logs', 'backups']:
    os.makedirs(os.path.join(BASE_DIR, d), exist_ok=True)


def create_app():
    """Build and initialize Flask app configuration."""
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )

    # Configuration properties
    app.config['SECRET_KEY'] = 'fakeguard-ai-enterprise-secret-key-2026'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'predictions.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8MB max upload
    
    # SQLite Pool Optimizations
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 280,
        'pool_timeout': 20,
        'pool_pre_ping': True
    }

    # Bind extensions
    db.init_app(app)

    # Security Headers Middleware
    @app.after_request
    def apply_security_headers(response):
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    # Configure Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)

    # Serve uploads folder dynamically
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(os.path.join(app.root_path, 'uploads'), filename)

    # Initialize SQLite database and models
    with app.app_context():
        db.create_all()
        
        # Check if default admin account exists, otherwise generate one
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("👤 Auto-generating default Administrator account...")
            default_admin = User(
                username='admin',
                email='admin@fakeguard.ai',
                full_name='System Administrator',
                password_hash=hash_password('admin123'),
                role='admin',
                theme_preference='midnight-blue'
            )
            db.session.add(default_admin)
            db.session.commit()
            print("   ✅ Default admin account created -> User: admin | Pass: admin123")

    # Load ML models on initialization
    try:
        if load_predictor():
            print("✅ Pre-trained predictor models loaded successfully!")
        else:
            print("⚠️  Warning: ML model files not found. Run model training script first.")
    except Exception as e:
        print(f"⚠️  Error loading ML model prediction pipeline: {e}")

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "=" * 55)
    print("  🚀 FakeGuard AI Enterprise Platform is active")
    print("  🌐 Workspace URL: http://localhost:5000")
    print("=" * 55 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
