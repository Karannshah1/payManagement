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
            'name': e.loan_name,
            'loan_name': e.loan_name,
            'amount': e.emi_amount,
            'emi_amount': e.emi_amount,
            'emiAmount': e.emi_amount,
            'total_months': e.total_tenure,
            'total_tenure': e.total_tenure,
            'totalTenure': e.total_tenure,
            'completed_months': e.completed_months,
            'completedMonths': e.completed_months,
            'start_date': e.start_date.isoformat() if getattr(e, 'start_date', None) else None,
            'account_id': e.account_id,
            'account_name': e.account.name if getattr(e, 'account', None) else 'Default Account',
            'category_id': getattr(e, 'category_id', None)
        } for e in emis])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@emi.route('/api/emi', methods=['POST'])
def create_emi():
    try:
        data = request.get_json() or {}
        
        # Flexible account resolution
        account = None
        account_val = data.get('account_id') or data.get('account')
        if account_val:
            try:
                account = Account.query.get(int(account_val))
            except (ValueError, TypeError):
                account = Account.query.filter(Account.name.ilike(str(account_val).strip())).first()
        if not account:
            account = Account.query.first()
            if not account:
                account = Account(name='Bank Account', account_type='bank', balance=0.0)
                db.session.add(account)
                db.session.flush()

        start_dt = date.today()
        if data.get('start_date'):
            try:
                start_dt = date.fromisoformat(str(data['start_date']).split('T')[0])
            except Exception:
                start_dt = date.today()

        loan_name = data.get('loan_name') or data.get('name') or 'Loan EMI'
        emi_amount = float(data.get('emi_amount') or data.get('amount') or 0)
        total_tenure = int(data.get('total_tenure') or data.get('total_months') or 12)

        new_emi = EMI(
            loan_name=loan_name,
            emi_amount=emi_amount,
            total_tenure=total_tenure,
            completed_months=int(data.get('completed_months', 0)),
            start_date=start_dt,
            account_id=account.id
        )
        db.session.add(new_emi)
        db.session.commit()
        return jsonify({'message': 'EMI created', 'id': new_emi.id, 'account_name': account.name}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@emi.route('/api/emi/<int:id>', methods=['PUT'])
def update_emi(id):
    try:
        e = EMI.query.get(id)
        if not e:
            return jsonify({'error': 'EMI not found'}), 404
            
        data = request.get_json() or {}
        if 'loan_name' in data or 'name' in data:
            e.loan_name = data.get('loan_name') or data.get('name')
        if 'emi_amount' in data or 'amount' in data:
            e.emi_amount = float(data.get('emi_amount') or data.get('amount'))
        if 'total_tenure' in data or 'total_months' in data:
            e.total_tenure = int(data.get('total_tenure') or data.get('total_months'))
        if 'account_id' in data:
            e.account_id = data['account_id']
            
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
            
        if e.completed_months >= e.total_tenure:
            return jsonify({'error': 'EMI already fully paid'}), 400
            
        account = Account.query.get(e.account_id)
        if not account:
            account = Account.query.first()
            
        if account:
            # Deduct from account
            account.balance -= e.emi_amount
        
        # Increment completed months
        e.completed_months += 1
        
        # Resolve category for EMI expense (non-null in DB)
        cat = Category.query.filter(Category.name.ilike('%EMI%')).first() or Category.query.filter(Category.name.ilike('%Utilities%')).first() or Category.query.first()
        cat_id = cat.id if cat else 1

        # Create an expense record for the EMI payment
        expense = Expense(
            amount=e.emi_amount,
            description=f'EMI Payment: {e.loan_name}',
            date=date.today(),
            category_id=cat_id,
            account_id=account.id if account else 1
        )
        db.session.add(expense)
        
        db.session.commit()
        return jsonify({'message': 'EMI payment successful', 'completed_months': e.completed_months})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
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
