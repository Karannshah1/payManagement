from flask import Blueprint, request, jsonify, render_template
from models import db, Expense, Category, Account
from datetime import datetime, date

expenses = Blueprint('expenses', __name__, url_prefix='/expenses')

@expenses.route('/')
def expenses_page():
    categories = Category.query.all()
    accounts = Account.query.all()
    return render_template('expenses.html', categories=categories, accounts=accounts)

@expenses.route('/api/expenses', methods=['GET'])
def get_expenses():
    try:
        query = Expense.query
        
        category_id = request.args.get('category_id')
        if category_id:
            query = query.filter(Expense.category_id == category_id)
            
        account_id = request.args.get('account_id')
        if account_id:
            query = query.filter(Expense.account_id == account_id)
            
        payment_method = request.args.get('payment_method')
        if payment_method:
            query = query.filter(Expense.payment_method == payment_method)
            
        date_from = request.args.get('date_from')
        if date_from:
            query = query.filter(Expense.date >= date.fromisoformat(date_from))
            
        date_to = request.args.get('date_to')
        if date_to:
            query = query.filter(Expense.date <= date.fromisoformat(date_to))
            
        amount_min = request.args.get('amount_min')
        if amount_min:
            query = query.filter(Expense.amount >= float(amount_min))
            
        amount_max = request.args.get('amount_max')
        if amount_max:
            query = query.filter(Expense.amount <= float(amount_max))
            
        search = request.args.get('search')
        if search:
            query = query.filter(Expense.description.ilike(f'%{search}%'))
            
        sort_by = request.args.get('sort_by', 'date')
        sort_order = request.args.get('sort_order', 'desc')
        
        if sort_by == 'date':
            if sort_order == 'desc':
                query = query.order_by(Expense.date.desc())
            else:
                query = query.order_by(Expense.date.asc())
        elif sort_by == 'amount':
            if sort_order == 'desc':
                query = query.order_by(Expense.amount.desc())
            else:
                query = query.order_by(Expense.amount.asc())
                
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        expenses_list = [{
            'id': e.id,
            'amount': e.amount,
            'description': e.description,
            'date': e.date.isoformat(),
            'category_id': e.category_id,
            'account_id': e.account_id,
            'payment_method': getattr(e, 'payment_method', None)
        } for e in pagination.items]
        
        return jsonify({
            'expenses': expenses_list,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expenses.route('/api/expenses', methods=['POST'])
def create_expense():
    try:
        data = request.get_json()
        account = Account.query.get(data['account_id'])
        if not account:
            return jsonify({'error': 'Account not found'}), 404
            
        expense = Expense(
            amount=data['amount'],
            description=data.get('description'),
            date=date.fromisoformat(data['date']) if data.get('date') else date.today(),
            category_id=data['category_id'],
            account_id=data['account_id'],
            payment_method=data.get('payment_method')
        )
        
        account.balance -= data['amount']
        db.session.add(expense)
        db.session.commit()
        
        return jsonify({'message': 'Expense created', 'id': expense.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@expenses.route('/api/expenses/<int:id>', methods=['PUT'])
def update_expense(id):
    try:
        expense = Expense.query.get(id)
        if not expense:
            return jsonify({'error': 'Expense not found'}), 404
            
        data = request.get_json()
        
        # Adjust balance
        old_account = Account.query.get(expense.account_id)
        old_account.balance += expense.amount
        
        expense.amount = data.get('amount', expense.amount)
        expense.description = data.get('description', expense.description)
        if 'date' in data:
            expense.date = date.fromisoformat(data['date'])
        expense.category_id = data.get('category_id', expense.category_id)
        expense.account_id = data.get('account_id', expense.account_id)
        if 'payment_method' in data:
            expense.payment_method = data['payment_method']
            
        new_account = Account.query.get(expense.account_id)
        new_account.balance -= expense.amount
        
        db.session.commit()
        return jsonify({'message': 'Expense updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@expenses.route('/api/expenses/<int:id>', methods=['DELETE'])
def delete_expense(id):
    try:
        expense = Expense.query.get(id)
        if not expense:
            return jsonify({'error': 'Expense not found'}), 404
            
        account = Account.query.get(expense.account_id)
        account.balance += expense.amount
        
        db.session.delete(expense)
        db.session.commit()
        return jsonify({'message': 'Expense deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

from services.ai_parser import parse_transaction_with_ai

@expenses.route('/api/expenses/quick-add', methods=['POST'])
def quick_add_expense():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        if not text:
            return jsonify({'error': 'Invalid text'}), 400
            
        # Call the AI Groq Model to parse the natural language
        parsed_data = parse_transaction_with_ai(text)
        
        amount = float(parsed_data.get('amount', 0))
        description = parsed_data.get('description', text)
        category_name = parsed_data.get('category', 'Miscellaneous')
        
        default_account = Account.query.filter_by(is_active=True).first()
        if not default_account:
            return jsonify({'error': 'No active account found'}), 404
            
        category = Category.query.filter(Category.name.ilike(category_name)).first()
        if not category:
            category = Category(name=category_name, type='expense')
            db.session.add(category)
            db.session.commit()
            
        expense = Expense(
            amount=amount,
            description=description,
            category_id=category.id,
            account_id=default_account.id,
            payment_method='UPI',
            date=date.today()
        )
        
        default_account.balance -= amount
        db.session.add(expense)
        db.session.commit()
        
        return jsonify({
            'message': 'AI smartly processed your expense',
            'expense_id': expense.id,
            'ai_parsed': parsed_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@expenses.route('/api/expenses/from-template/<int:template_id>', methods=['POST'])
def create_from_template(template_id):
    try:
        # Assuming ExpenseTemplate model exists
        from models import ExpenseTemplate
        template = ExpenseTemplate.query.get(template_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404
            
        account = Account.query.get(template.account_id)
        if not account:
            return jsonify({'error': 'Account not found'}), 404
            
        expense = Expense(
            amount=template.amount,
            description=template.description,
            date=date.today(),
            category_id=template.category_id,
            account_id=template.account_id,
            payment_method=getattr(template, 'payment_method', None)
        )
        
        account.balance -= template.amount
        db.session.add(expense)
        db.session.commit()
        
        return jsonify({'message': 'Expense created from template', 'id': expense.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

