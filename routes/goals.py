from flask import Blueprint, request, jsonify, render_template
from models import db, SavingsGoal as Goal
from datetime import date

goals = Blueprint('goals', __name__, url_prefix='/goals')

@goals.route('/')
def goals_page():
    return render_template('goals.html')

@goals.route('/api/goals', methods=['GET'])
def get_goals():
    try:
        all_goals = Goal.query.all()
        return jsonify([{
            'id': g.id,
            'name': g.name,
            'target_amount': g.target_amount,
            'current_amount': g.current_amount,
            'target_date': g.target_date.isoformat() if getattr(g, 'target_date', None) else None,
            'color': getattr(g, 'color', None)
        } for g in all_goals])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@goals.route('/api/goals', methods=['POST'])
def create_goal():
    try:
        data = request.get_json()
        goal = Goal(
            name=data['name'],
            target_amount=float(data['target_amount']),
            current_amount=float(data.get('current_amount', 0)),
            target_date=date.fromisoformat(data['target_date']) if data.get('target_date') else None,
            color=data.get('color')
        )
        db.session.add(goal)
        db.session.commit()
        return jsonify({'message': 'Goal created', 'id': goal.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@goals.route('/api/goals/<int:id>', methods=['PUT'])
def update_goal(id):
    try:
        goal = Goal.query.get(id)
        if not goal:
            return jsonify({'error': 'Goal not found'}), 404
            
        data = request.get_json()
        if 'name' in data:
            goal.name = data['name']
        if 'target_amount' in data:
            goal.target_amount = float(data['target_amount'])
        if 'target_date' in data:
            goal.target_date = date.fromisoformat(data['target_date']) if data['target_date'] else None
        if 'color' in data:
            goal.color = data['color']
            
        db.session.commit()
        return jsonify({'message': 'Goal updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@goals.route('/api/goals/<int:id>/contribute', methods=['POST'])
def contribute_goal(id):
    try:
        goal = Goal.query.get(id)
        if not goal:
            return jsonify({'error': 'Goal not found'}), 404
            
        data = request.get_json()
        amount = float(data['amount'])
        goal.current_amount += amount
        
        db.session.commit()
        return jsonify({'message': 'Contribution added', 'current_amount': goal.current_amount})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@goals.route('/api/goals/<int:id>', methods=['DELETE'])
def delete_goal(id):
    try:
        goal = Goal.query.get(id)
        if not goal:
            return jsonify({'error': 'Goal not found'}), 404
            
        db.session.delete(goal)
        db.session.commit()
        return jsonify({'message': 'Goal deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
