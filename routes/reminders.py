from flask import Blueprint, request, jsonify, render_template
from models import db, Reminder
from datetime import date

reminders = Blueprint('reminders', __name__, url_prefix='/reminders')

@reminders.route('/')
def reminders_page():
    return render_template('reminders.html')

@reminders.route('/api/reminders', methods=['GET'])
def get_reminders():
    try:
        query = Reminder.query
        upcoming_only = request.args.get('upcoming', type=bool)
        
        if upcoming_only:
            query = query.filter(Reminder.due_date >= date.today(), Reminder.is_completed == False)
            
        all_reminders = query.order_by(Reminder.due_date.asc()).all()
        
        return jsonify([{
            'id': r.id,
            'title': r.title,
            'description': getattr(r, 'description', None),
            'amount': getattr(r, 'amount', None),
            'due_date': r.due_date.isoformat(),
            'is_completed': r.is_completed
        } for r in all_reminders])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reminders.route('/api/reminders', methods=['POST'])
def create_reminder():
    try:
        data = request.get_json()
        reminder = Reminder(
            title=data['title'],
            description=data.get('description'),
            amount=data.get('amount') and float(data['amount']) or None,
            due_date=date.fromisoformat(data['due_date']),
            is_completed=False
        )
        db.session.add(reminder)
        db.session.commit()
        return jsonify({'message': 'Reminder created', 'id': reminder.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@reminders.route('/api/reminders/<int:id>/complete', methods=['PUT'])
def complete_reminder(id):
    try:
        reminder = Reminder.query.get(id)
        if not reminder:
            return jsonify({'error': 'Reminder not found'}), 404
            
        reminder.is_completed = True
        db.session.commit()
        return jsonify({'message': 'Reminder completed'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@reminders.route('/api/reminders/<int:id>', methods=['DELETE'])
def delete_reminder(id):
    try:
        reminder = Reminder.query.get(id)
        if not reminder:
            return jsonify({'error': 'Reminder not found'}), 404
            
        db.session.delete(reminder)
        db.session.commit()
        return jsonify({'message': 'Reminder deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
