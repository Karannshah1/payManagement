from collections import defaultdict
import calendar
from datetime import datetime

def compute_daily_average(expenses: list[dict], month: int, year: int) -> float:
    if not expenses:
        return 0.0
        
    total = sum(exp.get('amount', 0) for exp in expenses)
    
    now = datetime.now()
    if now.year == year and now.month == month:
        days = now.day
    else:
        _, days = calendar.monthrange(year, month)
        
    return total / days if days > 0 else 0.0

def compute_savings_rate(total_income: float, total_expenses: float) -> float:
    if total_income <= 0:
        return 0.0
    savings = total_income - total_expenses
    return (savings / total_income) * 100

def compute_spending_forecast(expenses: list[dict], month: int, year: int) -> float:
    daily_avg = compute_daily_average(expenses, month, year)
    _, days = calendar.monthrange(year, month)
    return daily_avg * days

def get_highest_spending_day(expenses: list[dict]) -> dict:
    if not expenses:
        return {}
        
    day_totals = defaultdict(float)
    day_counts = defaultdict(int)
    
    for exp in expenses:
        date_str = exp.get('date')
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str)
                weekday = dt.strftime('%A')
                day_totals[weekday] += exp.get('amount', 0)
                day_counts[weekday] += 1
            except ValueError:
                pass
                
    if not day_totals:
        return {}
        
    day_avgs = {day: day_totals[day] / day_counts[day] for day in day_totals}
    highest_day = max(day_avgs, key=day_avgs.get)
    
    return {
        'day': highest_day,
        'average': round(day_avgs[highest_day], 2)
    }

def compute_category_trends(expenses_by_month: dict) -> dict:
    trends = defaultdict(lambda: defaultdict(float))
    
    for month, expenses in expenses_by_month.items():
        for exp in expenses:
            cat = exp.get('category_name', 'Miscellaneous')
            trends[cat][month] += exp.get('amount', 0)
            
    return {cat: dict(months) for cat, months in trends.items()}
