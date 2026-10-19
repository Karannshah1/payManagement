from flask import Blueprint, request, jsonify, render_template
from models import db, Account, Transfer, Expense, Income
from datetime import date

accounts = Blueprint('accounts', __name__, url_prefix='/accounts')

@accounts.route('/')
def accounts_page():
    all_accounts = Account.query.all()
    return render_template('accounts.html', accounts=all_accounts)

@accounts.route('/api/accounts', methods=['GET'])
def get_accounts():
    try:
        accs = Account.query.all()
        return jsonify([{
            'id': a.id,
            'name': a.name,
            'balance': a.balance,
            'is_active': getattr(a, 'is_active', True)
        } for a in accs])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@accounts.route('/api/accounts', methods=['POST'])
def create_account():
    try:
        data = request.get_json()
        account = Account(
            name=data['name'],
            account_type=data.get('type', 'bank'),
            balance=data.get('balance', 0)
        )
        if 'is_active' in data:
            account.is_active = data['is_active']
        if 'include_in_tax_report' in data:
            account.include_in_tax_report = data['include_in_tax_report']
            
        db.session.add(account)
        db.session.commit()
        return jsonify({'message': 'Account created', 'id': account.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@accounts.route('/api/accounts/<int:id>', methods=['PUT'])
def update_account(id):
    try:
        account = Account.query.get(id)
        if not account:
            return jsonify({'error': 'Account not found'}), 404
            
        data = request.get_json()
        if 'name' in data:
            account.name = data['name']
        if 'balance' in data:
            account.balance = data['balance']
        if 'is_active' in data:
            account.is_active = data['is_active']
        if 'include_in_tax_report' in data:
            account.include_in_tax_report = data['include_in_tax_report']
            
        db.session.commit()
        return jsonify({'message': 'Account updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@accounts.route('/api/accounts/<int:id>', methods=['DELETE'])
def delete_account(id):
    try:
        account = Account.query.get(id)
        if not account:
            return jsonify({'error': 'Account not found'}), 404
            
        account.is_active = False
        db.session.commit()
        return jsonify({'message': 'Account soft deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@accounts.route('/api/accounts/transfer', methods=['POST'])
def transfer():
    try:
        data = request.get_json()
        from_acc = Account.query.get(data['from_account_id'])
        to_acc = Account.query.get(data['to_account_id'])
        
        if not from_acc or not to_acc:
            return jsonify({'error': 'Account not found'}), 404
            
        amount = float(data['amount'])
        from_acc.balance -= amount
        to_acc.balance += amount
        
        transfer = Transfer(
            from_account_id=from_acc.id,
            to_account_id=to_acc.id,
            amount=amount,
            description=data.get('description'),
            date=date.fromisoformat(data['date']) if data.get('date') else date.today()
        )
        
        db.session.add(transfer)
        db.session.commit()
        return jsonify({'message': 'Transfer successful', 'id': transfer.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@accounts.route('/api/accounts/<int:id>/transactions', methods=['GET'])
def get_transactions(id):
    try:
        account = Account.query.get(id)
        if not account:
            return jsonify({'error': 'Account not found'}), 404
            
        expenses = Expense.query.filter_by(account_id=id).order_by(Expense.date.desc()).limit(50).all()
        incomes = Income.query.filter_by(account_id=id).order_by(Income.date.desc()).limit(50).all()
        
        transactions = []
        for e in expenses:
            transactions.append({
                'type': 'expense',
                'id': e.id,
                'amount': e.amount,
                'description': e.description,
                'date': e.date.isoformat()
            })
            
        for i in incomes:
            transactions.append({
                'type': 'income',
                'id': i.id,
                'amount': i.amount,
                'source': i.source,
                'description': getattr(i, 'description', None),
                'date': i.date.isoformat()
            })
            
        transactions.sort(key=lambda x: x['date'], reverse=True)
        return jsonify(transactions[:50])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
