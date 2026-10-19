from flask import Blueprint, request, jsonify, render_template
from sqlalchemy import func
from models import db, Expense, Income, Category, Account
from datetime import date
import calendar

reports = Blueprint('reports', __name__, url_prefix='/reports')

@reports.route('/')
def reports_page():
    return render_template('reports.html')

@reports.route('/api/reports/tax', methods=['GET'])
def tax_report():
    try:
        from models import Expense, Category, Account
        from datetime import date
        year = request.args.get('year', date.today().year, type=int)
        
        # Get all expenses for the year, joined with Category and Account
        expenses = db.session.query(Expense, Category, Account).join(Category).join(Account).filter(
            db.extract('year', Expense.date) == year
        ).all()
        
        sections = {}
        for exp, cat, acc in expenses:
            # Check if it qualifies for tax
            if acc.include_in_tax_report or exp.is_tax_deductible_override:
                section = cat.tax_section if getattr(cat, 'tax_section', None) else 'Uncategorized'
                
                # Auto map based on names if empty
                if section == 'Uncategorized':
                    if cat.name.lower() in ['health', 'medical', 'insurance']:
                        section = '80D'
                    elif cat.name.lower() in ['education', 'tuition', 'mutual funds', 'pf', 'ppf']:
                        section = '80C'
                    elif cat.name.lower() in ['rent', 'house rent']:
                        section = '80GG'
                        
                if section != 'Uncategorized':
                    if section not in sections:
                        sections[section] = 0
                    sections[section] += exp.amount
                    
        return jsonify({
            'year': year,
            'sections': sections,
            'total_deductions': sum(sections.values())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports.route('/api/reports/monthly-summary', methods=['GET'])
def monthly_summary():
    try:
        month = request.args.get('month', date.today().month, type=int)
        year = request.args.get('year', date.today().year, type=int)
        
        start_date = date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = date(year, month, last_day)
        
        income = db.session.query(func.sum(Income.amount)).filter(Income.date >= start_date, Income.date <= end_date).scalar() or 0
        expenses = db.session.query(func.sum(Expense.amount)).filter(Expense.date >= start_date, Expense.date <= end_date).scalar() or 0
        savings = income - expenses
        
        cat_q = db.session.query(Category.name, func.sum(Expense.amount))\
            .join(Expense, Expense.category_id == Category.id)\
            .filter(Expense.date >= start_date, Expense.date <= end_date)\
            .group_by(Category.id).all()
            
        category_breakdown = [{'category': r[0], 'total': r[1]} for r in cat_q]
        
        top_exp = Expense.query.filter(Expense.date >= start_date, Expense.date <= end_date)\
            .order_by(Expense.amount.desc()).limit(5).all()
            
        top_expenses = [{
            'description': e.description,
            'amount': e.amount,
            'date': e.date.isoformat()
        } for e in top_exp]
        
        daily_avg = expenses / last_day
        
        return jsonify({
            'income': income,
            'expenses': expenses,
            'savings': savings,
            'category_breakdown': category_breakdown,
            'top_expenses': top_expenses,
            'daily_avg': round(daily_avg, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports.route('/api/reports/year-review', methods=['GET'])
def year_review():
    try:
        year = request.args.get('year', date.today().year, type=int)
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        total_income = db.session.query(func.sum(Income.amount)).filter(Income.date >= start_date, Income.date <= end_date).scalar() or 0
        total_expenses = db.session.query(func.sum(Expense.amount)).filter(Expense.date >= start_date, Expense.date <= end_date).scalar() or 0
        total_savings = total_income - total_expenses
        savings_rate = (total_savings / total_income * 100) if total_income > 0 else 0
        
        # Monthly breakdown
        monthly_breakdown = []
        for m in range(1, 13):
            m_start = date(year, m, 1)
            _, last_day = calendar.monthrange(year, m)
            m_end = date(year, m, last_day)
            
            m_inc = db.session.query(func.sum(Income.amount)).filter(Income.date >= m_start, Income.date <= m_end).scalar() or 0
            m_exp = db.session.query(func.sum(Expense.amount)).filter(Expense.date >= m_start, Expense.date <= m_end).scalar() or 0
            monthly_breakdown.append({
                'month': calendar.month_abbr[m],
                'income': m_inc,
                'expenses': m_exp
            })
            
        # Top categories
        cat_q = db.session.query(Category.name, func.sum(Expense.amount))\
            .join(Expense, Expense.category_id == Category.id)\
            .filter(Expense.date >= start_date, Expense.date <= end_date)\
            .group_by(Category.id).order_by(func.sum(Expense.amount).desc()).limit(5).all()
        top_categories = [{'category': r[0], 'total': r[1]} for r in cat_q]
        
        # Biggest expense
        biggest = Expense.query.filter(Expense.date >= start_date, Expense.date <= end_date).order_by(Expense.amount.desc()).first()
        biggest_expense = {
            'description': biggest.description,
            'amount': biggest.amount,
            'date': biggest.date.isoformat()
        } if biggest else None
        
        return jsonify({
            'total_income': total_income,
            'total_expenses': total_expenses,
            'total_savings': total_savings,
            'monthly_breakdown': monthly_breakdown,
            'top_categories': top_categories,
            'biggest_expense': biggest_expense,
            'savings_rate': round(savings_rate, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

