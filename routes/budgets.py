from flask import Blueprint, request, jsonify, render_template
from models import db, Budget, Category, Expense
from sqlalchemy import func
from datetime import date
import calendar

budgets = Blueprint('budgets', __name__, url_prefix='/budgets')

@budgets.route('/')
def budgets_page():
    return render_template('budgets.html')

@budgets.route('/api/budgets', methods=['GET'])
def get_budgets():
    try:
        month = request.args.get('month', date.today().month, type=int)
        year = request.args.get('year', date.today().year, type=int)
        
        start_date = date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = date(year, month, last_day)
        
        all_budgets = Budget.query.filter_by(month=month, year=year).all()
        
        results = []
        for b in all_budgets:
            category = Category.query.get(b.category_id)
            actual_spend = db.session.query(func.sum(Expense.amount))\
                .filter(Expense.category_id == b.category_id, 
                        Expense.date >= start_date, 
                        Expense.date <= end_date).scalar() or 0
                        
            results.append({
                'id': b.id,
                'category_id': b.category_id,
                'category_name': category.name if category else 'Unknown',
                'amount': b.amount,
                'actual_spend': actual_spend,
                'month': b.month,
                'year': b.year
            })
            
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budgets.route('/api/budgets', methods=['POST'])
def create_or_update_budget():
    try:
        data = request.get_json()
        
        # Handle both backend and React frontend formats
        category_id = data.get('category_id')
        category_name = data.get('category')
        
        if not category_id and category_name:
            # Look up or create category by name
            category = Category.query.filter(Category.name.ilike(category_name)).first()
            if not category:
                category = Category(name=category_name, type='expense')
                db.session.add(category)
                db.session.commit()
            category_id = category.id
            
        month = data.get('month', date.today().month)
        year = data.get('year', date.today().year)
        amount = float(data.get('amount') or data.get('limit') or 0)
        
        budget = Budget.query.filter_by(category_id=category_id, month=month, year=year).first()
        if budget:
            budget.amount = amount
            msg = 'Budget updated'
        else:
            budget = Budget(
                category_id=category_id,
                month=month,
                year=year,
                amount=amount
            )
            db.session.add(budget)
            msg = 'Budget created'
            
        db.session.commit()
        return jsonify({'message': msg, 'id': budget.id}), 200 if budget.id else 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@budgets.route('/api/budgets/<int:id>', methods=['DELETE'])
def delete_budget(id):
    try:
        budget = Budget.query.get(id)
        if not budget:
            return jsonify({'error': 'Budget not found'}), 404
            
        db.session.delete(budget)
        db.session.commit()
        return jsonify({'message': 'Budget deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
