from flask import Blueprint, request, jsonify, render_template
from models import db, EMI, Account, Expense, Category
from datetime import date

emi = Blueprint('emi', __name__, url_prefix='/emi')

@emi.route('/')
def emi_page():
    return render_template('emi.html')

@emi.route('/api/emi', methods=['GET'])
def get_emi():
    try:
        emis = EMI.query.all()
        return jsonify([{
            'id': e.id,
            'name': e.name,
            'amount': e.amount,
            'total_months': e.total_months,
            'completed_months': e.completed_months,
            'start_date': e.start_date.isoformat() if getattr(e, 'start_date', None) else None,
            'account_id': e.account_id,
            'category_id': getattr(e, 'category_id', None)
        } for e in emis])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@emi.route('/api/emi', methods=['POST'])
def create_emi():
    try:
        data = request.get_json()
        new_emi = EMI(
            name=data['name'],
            amount=float(data['amount']),
            total_months=int(data['total_months']),
            completed_months=int(data.get('completed_months', 0)),
            start_date=date.fromisoformat(data['start_date']) if data.get('start_date') else date.today(),
            account_id=data['account_id'],
            category_id=data.get('category_id')
        )
        db.session.add(new_emi)
        db.session.commit()
        return jsonify({'message': 'EMI created', 'id': new_emi.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@emi.route('/api/emi/<int:id>', methods=['PUT'])
def update_emi(id):
    try:
        e = EMI.query.get(id)
        if not e:
            return jsonify({'error': 'EMI not found'}), 404
            
        data = request.get_json()
        if 'name' in data:
            e.name = data['name']
        if 'amount' in data:
            e.amount = float(data['amount'])
        if 'total_months' in data:
            e.total_months = int(data['total_months'])
        if 'account_id' in data:
            e.account_id = data['account_id']
        if 'category_id' in data:
            e.category_id = data['category_id']
            
        db.session.commit()
        return jsonify({'message': 'EMI updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@emi.route('/api/emi/<int:id>/pay', methods=['POST'])
def pay_emi(id):
    try:
        e = EMI.query.get(id)
        if not e:
            return jsonify({'error': 'EMI not found'}), 404
            
        if e.completed_months >= e.total_months:
            return jsonify({'error': 'EMI already fully paid'}), 400
            
        account = Account.query.get(e.account_id)
        if not account:
            return jsonify({'error': 'Account not found'}), 404
            
        # Deduct from account
        account.balance -= e.amount
        
        # Increment completed months
        e.completed_months += 1
        
        # Create an expense record for the EMI payment
        expense = Expense(
            amount=e.amount,
            description=f'EMI Payment: {e.name}',
            date=date.today(),
            account_id=e.account_id,
            category_id=getattr(e, 'category_id', None)
        )
        db.session.add(expense)
        
        db.session.commit()
        return jsonify({'message': 'EMI payment successful', 'completed_months': e.completed_months})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@emi.route('/api/emi/<int:id>', methods=['DELETE'])
def delete_emi(id):
    try:
        e = EMI.query.get(id)
        if not e:
            return jsonify({'error': 'EMI not found'}), 404
            
        db.session.delete(e)
        db.session.commit()
        return jsonify({'message': 'EMI deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
