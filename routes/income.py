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
            'date': i.date.isoformat() if i.date else '',
            'account_id': i.account_id,
            'account_name': i.account.name if i.account else 'Default'
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
        data = request.get_json() or {}
        
        # Resolve Account: supports account_id (int) or account (name/id string)
        account = None
        account_val = data.get('account_id') or data.get('account')
        if account_val:
            try:
                account = Account.query.get(int(account_val))
            except (ValueError, TypeError):
                account = Account.query.filter(Account.name.ilike(str(account_val).strip())).first()
                if not account:
                    account = Account(name=str(account_val).strip(), account_type='bank', balance=0.0)
                    db.session.add(account)
                    db.session.flush()

        if not account:
            account = Account.query.first()
            if not account:
                account = Account(name='Bank Account', account_type='bank', balance=0.0)
                db.session.add(account)
                db.session.flush()

        # Parse date
        inc_date = date.today()
        if data.get('date'):
            try:
                inc_date = date.fromisoformat(str(data['date']).split('T')[0])
            except Exception:
                inc_date = date.today()

        amount = float(data.get('amount', 0))

        new_income = Income(
            amount=amount,
            source=data.get('source', 'Income'),
            description=data.get('description', ''),
            date=inc_date,
            account_id=account.id
        )
        
        account.balance += amount
        db.session.add(new_income)
        db.session.commit()
        
        return jsonify({
            'message': 'Income created',
            'id': new_income.id,
            'account_name': account.name
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@income.route('/api/income/<int:id>', methods=['PUT'])
def update_income(id):
    try:
        inc = Income.query.get(id)
        if not inc:
            return jsonify({'error': 'Income not found'}), 404
            
        data = request.get_json() or {}
        
        # Revert old balance
        old_account = Account.query.get(inc.account_id)
        if old_account:
            old_account.balance -= inc.amount
        
        if 'amount' in data:
            inc.amount = float(data['amount'])
        if 'source' in data:
            inc.source = data['source']
        if 'description' in data:
            inc.description = data['description']
        if 'date' in data and data['date']:
            try:
                inc.date = date.fromisoformat(str(data['date']).split('T')[0])
            except Exception:
                pass
                
        # Resolve new account if updated
        account_val = data.get('account_id') or data.get('account')
        if account_val:
            try:
                acc = Account.query.get(int(account_val))
            except (ValueError, TypeError):
                acc = Account.query.filter(Account.name.ilike(str(account_val).strip())).first()
            if acc:
                inc.account_id = acc.id
                
        new_account = Account.query.get(inc.account_id)
        if new_account:
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
