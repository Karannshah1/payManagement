def detect_anomalies(expenses: list[dict], threshold: float = 2.0) -> list[dict]:
    if not expenses:
        return []
        
    category_totals = {}
    category_counts = {}
    
    for exp in expenses:
        cat = exp.get('category_name', 'Miscellaneous')
        amt = exp.get('amount', 0)
        category_totals[cat] = category_totals.get(cat, 0) + amt
        category_counts[cat] = category_counts.get(cat, 0) + 1
        
    category_avgs = {cat: category_totals[cat] / category_counts[cat] for cat in category_totals}
    
    anomalies = []
    for exp in expenses:
        cat = exp.get('category_name', 'Miscellaneous')
        amt = exp.get('amount', 0)
        avg = category_avgs[cat]
        
        if avg > 0 and amt > threshold * avg:
            ratio = amt / avg
            anomalies.append({
                'expense': exp,
                'category_avg': round(avg, 2),
                'ratio': round(ratio, 2),
                'message': f"Amount {amt} is {ratio:.1f}x higher than category average of {avg:.2f}"
            })
            
    return anomalies
