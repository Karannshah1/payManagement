from flask import Blueprint, request, jsonify, render_template
from models import db, Setting

settings_bp = Blueprint('settings_bp', __name__, url_prefix='/settings')

@settings_bp.route('/')
def settings_page():
    # Pass current settings to template if needed
    return render_template('settings.html')

@settings_bp.route('/api/settings', methods=['GET'])
def get_settings():
    try:
        all_settings = Setting.query.all()
        return jsonify({s.key: s.value for s in all_settings})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/api/settings', methods=['POST'])
def save_settings():
    try:
        data = request.get_json()
        for key, value in data.items():
            setting = Setting.query.filter_by(key=key).first()
            if setting:
                setting.value = str(value)
            else:
                setting = Setting(key=key, value=str(value))
                db.session.add(setting)
                
        db.session.commit()
        return jsonify({'message': 'Settings saved successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/api/settings/supabase-status', methods=['GET'])
def supabase_status():
    from services.supabase_client import test_supabase_connection
    from config import Config
    supabase_info = test_supabase_connection()
    is_postgres = Config.SQLALCHEMY_DATABASE_URI.startswith('postgresql')
    return jsonify({
        'supabase': supabase_info,
        'database_backend': 'PostgreSQL (Supabase/Cloud)' if is_postgres else 'SQLite (Local)',
        'database_uri_configured': bool(Config.SQLALCHEMY_DATABASE_URI)
    })
