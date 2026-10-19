import re
from datetime import date

CATEGORY_KEYWORDS = {
    'Food & Dining': ['chai', 'tea', 'coffee', 'lunch', 'dinner', 'breakfast', 'food', 'restaurant', 'swiggy', 'zomato', 'snack', 'biryani', 'pizza', 'burger'],
    'Transport': ['auto', 'cab', 'uber', 'ola', 'metro', 'bus', 'train', 'fuel', 'petrol', 'diesel', 'parking', 'toll'],
    'Rent': ['rent', 'house rent'],
    'Utilities': ['electricity', 'water', 'gas', 'internet', 'wifi', 'broadband', 'phone', 'recharge', 'bill'],
    'Entertainment': ['movie', 'cinema', 'netflix', 'hotstar', 'prime', 'game'],
    'Health': ['medicine', 'doctor', 'hospital', 'pharmacy', 'medical', 'gym', 'fitness'],
    'Shopping': ['amazon', 'flipkart', 'shopping', 'clothes', 'shoes'],
    'Education': ['course', 'book', 'udemy', 'tutorial', 'school', 'college', 'fee', 'tuition'],
    'Subscriptions': ['subscription', 'spotify', 'youtube', 'netflix', 'premium'],
    'Groceries': ['grocery', 'vegetables', 'fruits', 'milk', 'provisions', 'kirana'],
    'Personal Care': ['salon', 'haircut', 'spa', 'cosmetics']
}

def parse_quick_add(text: str) -> dict:
    # Find numbers in the text
    numbers = re.findall(r'\d+(?:\.\d+)?', text)
    amount = 0.0
    if numbers:
        amount = max([float(n) for n in numbers]) # Use largest/only number as amount

    # Remove the amount from text to get description
    amount_str = str(int(amount)) if amount.is_integer() else str(amount)
    desc_text = re.sub(fr'\b{amount_str}\b|\b{amount}\b', '', text).strip()
    desc_text = re.sub(r'\s+', ' ', desc_text).strip()
    description = desc_text if desc_text else "Quick Add Expense"

    # Match against category keywords
    category_name = 'Miscellaneous'
    words = text.lower().split()
    found = False
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in words:
                category_name = cat
                found = True
                break
        if found:
            break

    return {
        'description': description,
        'amount': amount,
        'category_name': category_name,
        'date': date.today().isoformat()
    }
