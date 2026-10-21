"""
PayManagement - Personal Expense Management Application
========================================================
A feature-rich expense tracking app with dashboards, smart bill scanning,
UPI transaction parsing, budget management, and more.

Run with: python app.py
Open: http://localhost:5000
"""

import re
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db, seed_defaults


def create_app():
    app = Flask(__name__)
    allowed_origins = [
        re.compile(r'https://.*\.vercel\.app'),
        "https://pay-management-eight.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000"
    ]
    CORS(app, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)
    app.config.from_object(Config)

    # Health check endpoint for Render/hosting platforms
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "ok", "app": "PayManagement API"}), 200

    # Initialize database
    db.init_app(app)

    # Register blueprints
    from routes.dashboard import dashboard
    from routes.expenses import expenses
    from routes.income import income
    from routes.accounts import accounts
    from routes.categories import categories
    from routes.budgets import budgets
    from routes.goals import goals
    from routes.emi import emi
    from routes.splits import splits
    from routes.subscriptions import subscriptions
    from routes.reminders import reminders
    from routes.export_import import export_import
    from routes.reports import reports
    from routes.settings import settings_bp

    app.register_blueprint(dashboard)
    app.register_blueprint(expenses)
    app.register_blueprint(income)
    app.register_blueprint(accounts)
    app.register_blueprint(categories)
    app.register_blueprint(budgets)
    app.register_blueprint(goals)
    app.register_blueprint(emi)
    app.register_blueprint(splits)
    app.register_blueprint(subscriptions)
    app.register_blueprint(reminders)
    app.register_blueprint(export_import)
    app.register_blueprint(reports)
    app.register_blueprint(settings_bp)

    # Create tables and seed defaults
    with app.app_context():
        db.create_all()
        seed_defaults()

    return app


if __name__ == '__main__':
    app = create_app()
    print("=" * 60)
    print("  PayManagement - Personal Expense Tracker")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 60)
    app.run(debug=True, port=5000)
