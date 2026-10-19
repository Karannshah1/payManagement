def categorize_vendor(vendor_name: str) -> str:
    if not vendor_name:
        return 'Miscellaneous'
        
    vendor_lower = vendor_name.lower()
    
    mapping = {
        'Food & Dining': ['swiggy', 'zomato', 'dominos', 'mcdonalds', 'kfc', 'pizza hut', 'starbucks', 'cafe'],
        'Transport': ['uber', 'ola', 'rapido', 'metro', 'irctc', 'redbus'],
        'Shopping': ['amazon', 'flipkart', 'myntra', 'ajio', 'meesho', 'nykaa'],
        'Subscriptions': ['netflix', 'hotstar', 'prime video', 'spotify', 'youtube', 'jiocinema'],
        'Health': ['apollo', 'medplus', 'pharmeasy', '1mg', 'practo'],
        'Utilities': ['airtel', 'jio', 'vi', 'bsnl', 'tata play', 'act fibernet'],
        'Education': ['byju', 'unacademy', 'coursera', 'udemy'],
        'Groceries': ['bigbasket', 'blinkit', 'zepto', 'instamart', 'dmart']
    }
    
    for category, keywords in mapping.items():
        for kw in keywords:
            if kw in vendor_lower:
                return category
                
    return 'Miscellaneous'
