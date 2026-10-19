def classify_bill(raw_text: str) -> dict:
    text_lower = raw_text.lower()
    
    income_keywords = ['salary', 'credit', 'refund', 'cashback', 'received', 'credited', 'bonus', 'dividend', 'interest earned', 'reimbursement']
    expense_keywords = ['invoice', 'bill', 'receipt', 'payment', 'debit', 'debited', 'total', 'amount due', 'payable', 'charged']
    
    income_score = sum(1 for kw in income_keywords if kw in text_lower)
    expense_score = sum(1 for kw in expense_keywords if kw in text_lower)
    
    if income_score > expense_score:
        confidence = min(0.5 + (income_score - expense_score) * 0.1, 0.99)
        return {
            'type': 'income',
            'confidence': round(confidence, 2),
            'reason': f'Matched {income_score} income keywords'
        }
    elif expense_score > income_score:
        confidence = min(0.5 + (expense_score - income_score) * 0.1, 0.99)
        return {
            'type': 'expense',
            'confidence': round(confidence, 2),
            'reason': f'Matched {expense_score} expense keywords'
        }
    else:
        return {
            'type': 'expense',
            'confidence': 0.5,
            'reason': 'Default classification'
        }
