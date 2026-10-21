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
            'cycle': s.billing_cycle,
            'next_renewal': s.next_renewal.isoformat() if getattr(s, 'next_renewal', None) else None,
            'next_billing_date': s.next_renewal.isoformat() if getattr(s, 'next_renewal', None) else None,
            'nextRenewalDate': s.next_renewal.isoformat() if getattr(s, 'next_renewal', None) else None,
            'is_active': getattr(s, 'is_active', True),
            'account_id': getattr(s, 'account_id', None),
            'account_name': s.account.name if getattr(s, 'account', None) else 'Default Account',
            'category_id': getattr(s, 'category_id', None)
        } for s in subs])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscriptions.route('/api/subscriptions', methods=['POST'])
def create_subscription():
    try:
        data = request.get_json() or {}
        
        # Flexible account resolution
        account = None
        account_val = data.get('account_id') or data.get('account')
        if account_val:
            from models import Account
            try:
                account = Account.query.get(int(account_val))
            except (ValueError, TypeError):
                account = Account.query.filter(Account.name.ilike(str(account_val).strip())).first()
        if not account:
            from models import Account
            account = Account.query.first()

        next_date = date.today()
        date_str = data.get('next_renewal') or data.get('next_billing_date') or data.get('nextRenewalDate')
        if date_str:
            try:
                next_date = date.fromisoformat(str(date_str).split('T')[0])
            except Exception:
                next_date = date.today()

        sub = Subscription(
            name=data.get('name', 'Subscription'),
            amount=float(data.get('amount', 0)),
            billing_cycle=data.get('billing_cycle', data.get('cycle', 'monthly')),
            next_renewal=next_date,
            is_active=data.get('is_active', True),
            account_id=account.id if account else None,
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
            
        data = request.get_json() or {}
        if 'name' in data:
            sub.name = data['name']
        if 'amount' in data:
            sub.amount = float(data['amount'])
        if 'billing_cycle' in data or 'cycle' in data:
            sub.billing_cycle = data.get('billing_cycle') or data.get('cycle')
            
        date_str = data.get('next_renewal') or data.get('next_billing_date') or data.get('nextRenewalDate')
        if date_str:
            try:
                sub.next_renewal = date.fromisoformat(str(date_str).split('T')[0])
            except Exception:
                pass
                
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
