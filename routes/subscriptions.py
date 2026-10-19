from flask import Blueprint, request, jsonify, render_template
from models import db, Subscription
from datetime import date

subscriptions = Blueprint('subscriptions', __name__, url_prefix='/subscriptions')

@subscriptions.route('/')
def subscriptions_page():
    return render_template('subscriptions.html')

@subscriptions.route('/api/subscriptions', methods=['GET'])
def get_subscriptions():
    try:
        subs = Subscription.query.all()
        return jsonify([{
            'id': s.id,
            'name': s.name,
            'amount': s.amount,
            'billing_cycle': s.billing_cycle,
            'next_billing_date': s.next_billing_date.isoformat() if getattr(s, 'next_billing_date', None) else None,
            'is_active': getattr(s, 'is_active', True),
            'account_id': getattr(s, 'account_id', None),
            'category_id': getattr(s, 'category_id', None)
        } for s in subs])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscriptions.route('/api/subscriptions', methods=['POST'])
def create_subscription():
    try:
        data = request.get_json()
        sub = Subscription(
            name=data['name'],
            amount=float(data['amount']),
            billing_cycle=data.get('billing_cycle', 'monthly'),
            next_billing_date=date.fromisoformat(data['next_billing_date']) if data.get('next_billing_date') else date.today(),
            is_active=data.get('is_active', True),
            account_id=data.get('account_id'),
            category_id=data.get('category_id')
        )
        db.session.add(sub)
        db.session.commit()
        return jsonify({'message': 'Subscription created', 'id': sub.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@subscriptions.route('/api/subscriptions/<int:id>', methods=['PUT'])
def update_subscription(id):
    try:
        sub = Subscription.query.get(id)
        if not sub:
            return jsonify({'error': 'Subscription not found'}), 404
            
        data = request.get_json()
        if 'name' in data:
            sub.name = data['name']
        if 'amount' in data:
            sub.amount = float(data['amount'])
        if 'billing_cycle' in data:
            sub.billing_cycle = data['billing_cycle']
        if 'next_billing_date' in data:
            sub.next_billing_date = date.fromisoformat(data['next_billing_date'])
        if 'account_id' in data:
            sub.account_id = data['account_id']
        if 'category_id' in data:
            sub.category_id = data['category_id']
            
        db.session.commit()
        return jsonify({'message': 'Subscription updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@subscriptions.route('/api/subscriptions/<int:id>/toggle', methods=['PUT'])
def toggle_subscription(id):
    try:
        sub = Subscription.query.get(id)
        if not sub:
            return jsonify({'error': 'Subscription not found'}), 404
            
        sub.is_active = not getattr(sub, 'is_active', True)
        db.session.commit()
        return jsonify({'message': 'Subscription toggled', 'is_active': sub.is_active})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@subscriptions.route('/api/subscriptions/<int:id>', methods=['DELETE'])
def delete_subscription(id):
    try:
        sub = Subscription.query.get(id)
        if not sub:
            return jsonify({'error': 'Subscription not found'}), 404
            
        db.session.delete(sub)
        db.session.commit()
        return jsonify({'message': 'Subscription deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
