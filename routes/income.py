from flask import Blueprint, request, jsonify, render_template
from models import db, Income, Account
from datetime import date

income = Blueprint('income', __name__, url_prefix='/income')

@income.route('/')
def income_page():
    accounts = Account.query.all()
    return render_template('income.html', accounts=accounts)

@income.route('/api/income', methods=['GET'])
def get_income():
    try:
        query = Income.query
        
        account_id = request.args.get('account_id')
        if account_id:
            query = query.filter(Income.account_id == account_id)
            
        source = request.args.get('source')
        if source:
            query = query.filter(Income.source.ilike(f'%{source}%'))
            
        date_from = request.args.get('date_from')
        if date_from:
            query = query.filter(Income.date >= date.fromisoformat(date_from))
            
        date_to = request.args.get('date_to')
        if date_to:
            query = query.filter(Income.date <= date.fromisoformat(date_to))
            
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        pagination = query.order_by(Income.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
        income_list = [{
            'id': i.id,
            'amount': i.amount,
            'source': i.source,
            'description': getattr(i, 'description', None),
            'date': i.date.isoformat(),
            'account_id': i.account_id
        } for i in pagination.items]
        
        return jsonify({
            'income': income_list,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@income.route('/api/income', methods=['POST'])
def create_income():
    try:
        data = request.get_json()
        account = Account.query.get(data['account_id'])
        if not account:
            return jsonify({'error': 'Account not found'}), 404
            
        new_income = Income(
            amount=data['amount'],
            source=data.get('source'),
            description=data.get('description'),
            date=date.fromisoformat(data['date']) if data.get('date') else date.today(),
            account_id=data['account_id']
        )
        
        account.balance += data['amount']
        db.session.add(new_income)
        db.session.commit()
        
        return jsonify({'message': 'Income created', 'id': new_income.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@income.route('/api/income/<int:id>', methods=['PUT'])
def update_income(id):
    try:
        inc = Income.query.get(id)
        if not inc:
            return jsonify({'error': 'Income not found'}), 404
            
        data = request.get_json()
        
        old_account = Account.query.get(inc.account_id)
        old_account.balance -= inc.amount
        
        inc.amount = data.get('amount', inc.amount)
        inc.source = data.get('source', inc.source)
        if 'description' in data:
            inc.description = data['description']
        if 'date' in data:
            inc.date = date.fromisoformat(data['date'])
        inc.account_id = data.get('account_id', inc.account_id)
        
        new_account = Account.query.get(inc.account_id)
        new_account.balance += inc.amount
        
        db.session.commit()
        return jsonify({'message': 'Income updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@income.route('/api/income/<int:id>', methods=['DELETE'])
def delete_income(id):
    try:
        inc = Income.query.get(id)
        if not inc:
            return jsonify({'error': 'Income not found'}), 404
            
        account = Account.query.get(inc.account_id)
        account.balance -= inc.amount
        
        db.session.delete(inc)
        db.session.commit()
        return jsonify({'message': 'Income deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
