from flask import Blueprint, request, jsonify, render_template
from sqlalchemy import func, extract
from models import db, Expense, Income, Account, Category, Budget, Reminder, Subscription
from datetime import date, datetime, timedelta
import calendar

dashboard = Blueprint('dashboard', __name__, url_prefix='')

@dashboard.route('/')
def index():
    return render_template('index.html')

def get_month_year():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    if not month or not year:
        today = date.today()
        month = month or today.month
        year = year or today.year
        
    return month, year

def get_date_range(month, year):
    start_date = date(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    end_date = date(year, month, last_day)
    return start_date, end_date

@dashboard.route('/api/dashboard/summary', methods=['GET'])
def get_summary():
    try:
        month, year = get_month_year()
        account_id = request.args.get('account_id')
        start_date, end_date = get_date_range(month, year)
        
        income_q = db.session.query(func.sum(Income.amount)).filter(Income.date >= start_date, Income.date <= end_date)
        expense_q = db.session.query(func.sum(Expense.amount)).filter(Expense.date >= start_date, Expense.date <= end_date)
        
        if account_id:
            income_q = income_q.filter(Income.account_id == account_id)
            expense_q = expense_q.filter(Expense.account_id == account_id)
            
        total_income = income_q.scalar() or 0
        total_expenses = expense_q.scalar() or 0
        net_savings = total_income - total_expenses
        
        # transaction count
        t_income = db.session.query(func.count(Income.id)).filter(Income.date >= start_date, Income.date <= end_date)
        t_expense = db.session.query(func.count(Expense.id)).filter(Expense.date >= start_date, Expense.date <= end_date)
        if account_id:
            t_income = t_income.filter(Income.account_id == account_id)
            t_expense = t_expense.filter(Expense.account_id == account_id)
            
        transaction_count = (t_income.scalar() or 0) + (t_expense.scalar() or 0)
        
        # budget used percent
        budgets = db.session.query(func.sum(Budget.limit_amount)).filter(Budget.month == month, Budget.year == year).scalar() or 0
        budget_used_percent = (total_expenses / budgets * 100) if budgets > 0 else 0
        
        return jsonify({
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_savings': net_savings,
            'budget_used_percent': round(budget_used_percent, 2),
            'transaction_count': transaction_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard.route('/api/dashboard/category-breakdown', methods=['GET'])
def category_breakdown():
    try:
        month, year = get_month_year()
        account_id = request.args.get('account_id')
        start_date, end_date = get_date_range(month, year)
        
        q = db.session.query(Category.name, getattr(Category, 'color', None), func.sum(Expense.amount))\
            .join(Expense, Expense.category_id == Category.id)\
            .filter(Expense.date >= start_date, Expense.date <= end_date)
            
        if account_id:
            q = q.filter(Expense.account_id == account_id)
            
        results = q.group_by(Category.id).all()
        
        return jsonify([{
            'category_name': r[0],
            'category_color': r[1],
            'total': r[2]
        } for r in results])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard.route('/api/dashboard/daily-trend', methods=['GET'])
def daily_trend():
    try:
        month, year = get_month_year()
        account_id = request.args.get('account_id')
        start_date, end_date = get_date_range(month, year)
        
        q = db.session.query(Expense.date, func.sum(Expense.amount))\
            .filter(Expense.date >= start_date, Expense.date <= end_date)
            
        if account_id:
            q = q.filter(Expense.account_id == account_id)
            
        results = q.group_by(Expense.date).order_by(Expense.date).all()
        
        # Fill in missing days
        days_in_month = end_date.day
        trend_dict = {date(year, month, d).isoformat(): 0 for d in range(1, days_in_month + 1)}
        for r in results:
            trend_dict[r[0].isoformat()] = r[1]
            
        return jsonify([{'date': k, 'amount': v} for k, v in trend_dict.items()])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard.route('/api/dashboard/monthly-comparison', methods=['GET'])
def monthly_comparison():
    try:
        account_id = request.args.get('account_id')
        today = date.today()
        
        results = []
        for i in range(5, -1, -1):
            target_date = today.replace(day=1) - timedelta(days=28 * i)
            month, year = target_date.month, target_date.year
            # Precise calculation for month/year might need dateutil, simple approach:
            y = today.year - ((today.month - i - 1) < 0)
            m = (today.month - i - 1) % 12 + 1
            
            start_date, end_date = get_date_range(m, y)
            
            inc_q = db.session.query(func.sum(Income.amount)).filter(Income.date >= start_date, Income.date <= end_date)
            exp_q = db.session.query(func.sum(Expense.amount)).filter(Expense.date >= start_date, Expense.date <= end_date)
            
            if account_id:
                inc_q = inc_q.filter(Income.account_id == account_id)
                exp_q = exp_q.filter(Expense.account_id == account_id)
                
            inc = inc_q.scalar() or 0
            exp = exp_q.scalar() or 0
            
            month_label = date(y, m, 1).strftime('%b %Y')
            results.append({
                'month_label': month_label,
                'income': inc,
                'expenses': exp
            })
            
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard.route('/api/dashboard/payment-methods', methods=['GET'])
def payment_methods():
    try:
        month, year = get_month_year()
        account_id = request.args.get('account_id')
        start_date, end_date = get_date_range(month, year)
        
        q = db.session.query(getattr(Expense, 'payment_method', Expense.id), func.sum(Expense.amount))\
            .filter(Expense.date >= start_date, Expense.date <= end_date)
            
        if account_id:
            q = q.filter(Expense.account_id == account_id)
            
        # Assuming payment_method exists, otherwise fallback grouping
        if hasattr(Expense, 'payment_method'):
            results = q.group_by(Expense.payment_method).all()
            return jsonify([{'method': r[0] or 'Unknown', 'total': r[1]} for r in results])
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard.route('/api/dashboard/top-expenses', methods=['GET'])
def top_expenses():
    try:
        month, year = get_month_year()
        account_id = request.args.get('account_id')
        start_date, end_date = get_date_range(month, year)
        
        q = db.session.query(Expense.description, Expense.amount, Category.name, Expense.date)\
            .join(Category, Expense.category_id == Category.id)\
            .filter(Expense.date >= start_date, Expense.date <= end_date)
            
        if account_id:
            q = q.filter(Expense.account_id == account_id)
            
        results = q.order_by(Expense.amount.desc()).limit(5).all()
        
        return jsonify([{
            'description': r[0],
            'amount': r[1],
            'category': r[2],
            'date': r[3].isoformat()
        } for r in results])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard.route('/api/dashboard/cash-vs-digital', methods=['GET'])
def cash_vs_digital():
    try:
        month, year = get_month_year()
        start_date, end_date = get_date_range(month, year)
        
        if hasattr(Expense, 'payment_method'):
            cash_total = db.session.query(func.sum(Expense.amount))\
                .filter(Expense.date >= start_date, Expense.date <= end_date, Expense.payment_method == 'Cash').scalar() or 0
            digital_total = db.session.query(func.sum(Expense.amount))\
                .filter(Expense.date >= start_date, Expense.date <= end_date, Expense.payment_method != 'Cash').scalar() or 0
        else:
            cash_total = 0
            digital_total = 0
            
        return jsonify({
            'cash_total': cash_total,
            'digital_total': digital_total
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard.route('/api/dashboard/account-balances', methods=['GET'])
def account_balances():
    try:
        accounts = Account.query.all()
        return jsonify([{
            'account_name': a.name,
            'account_type': getattr(a, 'type', 'General'),
            'balance': a.balance,
            'color': getattr(a, 'color', '#000000')
        } for a in accounts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard.route('/api/dashboard/upcoming', methods=['GET'])
def upcoming():
    try:
        today = date.today()
        next_week = today + timedelta(days=7)
        
        reminders = Reminder.query.filter(Reminder.due_date >= today, Reminder.due_date <= next_week, Reminder.is_completed == False).all()
        subs = Subscription.query.filter(Subscription.next_billing_date >= today, Subscription.next_billing_date <= next_week, getattr(Subscription, 'is_active', True) == True).all()
        
        upcoming_list = []
        for r in reminders:
            upcoming_list.append({
                'type': 'reminder',
                'title': r.title,
                'date': r.due_date.isoformat(),
                'amount': getattr(r, 'amount', 0)
            })
            
        for s in subs:
            upcoming_list.append({
                'type': 'subscription',
                'title': s.name,
                'date': s.next_billing_date.isoformat(),
                'amount': s.amount
            })
            
        upcoming_list.sort(key=lambda x: x['date'])
        return jsonify(upcoming_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard.route('/api/dashboard/anomalies', methods=['GET'])
def anomalies():
    try:
        month, year = get_month_year()
        start_date, end_date = get_date_range(month, year)
        
        # Calculate average per category over last 6 months
        six_months_ago = start_date - timedelta(days=180)
        
        avg_query = db.session.query(Expense.category_id, (func.sum(Expense.amount) / 6).label('avg_amount'))\
            .filter(Expense.date >= six_months_ago, Expense.date < start_date)\
            .group_by(Expense.category_id).all()
            
        avg_dict = {r[0]: r[1] for r in avg_query}
        
        # Get current month expenses
        current_expenses = Expense.query.filter(Expense.date >= start_date, Expense.date <= end_date).all()
        
        anomalies_list = []
        for e in current_expenses:
            cat_avg = avg_dict.get(e.category_id, 0)
            if cat_avg > 0 and e.amount > (cat_avg * 2):
                cat = Category.query.get(e.category_id)
                anomalies_list.append({
                    'description': e.description,
                    'amount': e.amount,
                    'category': cat.name if cat else 'Unknown',
                    'date': e.date.isoformat(),
                    'average': float(cat_avg)
                })
                
        return jsonify(anomalies_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard.route('/api/dashboard/predictive', methods=['GET'])
def get_predictive_insights():
    try:
        from models import Expense, Budget
        from sqlalchemy import func
        from datetime import date
        import calendar

        today = date.today()
        month = today.month
        year = today.year
        days_in_month = calendar.monthrange(year, month)[1]
        days_passed = today.day

        # Get total spend this month
        start_date = date(year, month, 1)
        end_date = date(year, month, days_in_month)
        
        total_spend = db.session.query(func.sum(Expense.amount)).filter(
            Expense.date >= start_date, Expense.date <= end_date
        ).scalar() or 0

        # Get total budget this month
        total_budget = db.session.query(func.sum(Budget.limit_amount)).filter_by(
            month=month, year=year
        ).scalar() or 0

        daily_average = total_spend / days_passed if days_passed > 0 else 0
        projected_total = daily_average * days_in_month

        runway_days = 0
        if daily_average > 0 and total_budget > 0:
            remaining_budget = total_budget - total_spend
            runway_days = remaining_budget / daily_average if remaining_budget > 0 else 0

        insights = []
        if projected_total > total_budget and total_budget > 0:
            insights.append({
                "type": "warning",
                "title": "Budget Alert",
                "message": f"At your current spending rate of ?{daily_average:,.0f}/day, you will exceed your monthly budget of ?{total_budget:,.0f}. Projected spend: ?{projected_total:,.0f}."
            })
        elif total_budget > 0:
            insights.append({
                "type": "success",
                "title": "On Track",
                "message": f"Great job! You are projected to spend ?{projected_total:,.0f} this month, keeping you safely under your ?{total_budget:,.0f} budget."
            })

        if runway_days > 0 and runway_days < (days_in_month - days_passed):
             insights.append({
                "type": "danger",
                "title": "Runway Warning",
                "message": f"Warning: You only have {int(runway_days)} days of budget runway left before you run out."
            })

        return jsonify({
            "projected_spend": projected_total,
            "daily_average": daily_average,
            "insights": insights
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
