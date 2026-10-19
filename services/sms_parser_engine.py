import re

def parse_sms(sms_text: str) -> list[dict]:
    results = []
    lines = sms_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        parsed = None
        
        # Pattern 1: Debited with UPI Ref
        if m := re.search(r'(?:Rs\.?|INR)\s*([\d,]+\.?\d*)\s*debited.*?(?:A/c|a/c).*?(\d+).*?on\s*([\d\-\w]+)\.\s*UPI/([^/]+)/([^/\.]+)', line, re.I):
            parsed = {
                'amount': float(m.group(1).replace(',', '')),
                'type': 'debit',
                'merchant': m.group(4).strip(),
                'date': m.group(3).strip(),
                'upi_ref': m.group(5).strip(),
                'account_last4': m.group(2).strip()
            }
            
        # Pattern 2: Credited
        elif m := re.search(r'(?:a/c|A/c).*?(\d+).*?credited.*?with\s*(?:Rs\.?|INR)\s*([\d,]+\.?\d*)\s*on\s*([\d\-\w]+).*?UPI Ref:\s*(\d+)', line, re.I):
            parsed = {
                'amount': float(m.group(2).replace(',', '')),
                'type': 'credit',
                'merchant': 'Unknown',
                'date': m.group(3).strip(),
                'upi_ref': m.group(4).strip(),
                'account_last4': m.group(1).strip()
            }
            
        # Pattern 3: UPI payment successful
        elif m := re.search(r'UPI payment of\s*(?:Rs\.?|INR)\s*([\d,]+\.?\d*)\s*from.*?(\d+)\s*to\s*(.*?)\s*was successful.*?UPI Ref No\s*(\d+)', line, re.I):
            parsed = {
                'amount': float(m.group(1).replace(',', '')),
                'type': 'debit',
                'merchant': m.group(3).strip(),
                'date': None,
                'upi_ref': m.group(4).strip(),
                'account_last4': m.group(2).strip()
            }
            
        # Pattern 4: Sent Rs
        elif m := re.search(r'Sent\s*(?:Rs\.?|INR)\s*([\d,]+\.?\d*)\s*to\s*(.*?)\s*from.*?A/c.*?(\d+).*?UPI Ref No\s*(\d+)', line, re.I):
            parsed = {
                'amount': float(m.group(1).replace(',', '')),
                'type': 'debit',
                'merchant': m.group(2).strip(),
                'date': None,
                'upi_ref': m.group(4).strip(),
                'account_last4': m.group(3).strip()
            }
            
        # Pattern 5: Received Rs
        elif m := re.search(r'Received\s*(?:Rs\.?|INR)\s*([\d,]+\.?\d*)\s*from\s*(.*?)\s*in your A/c.*?(\d+).*?UPI Ref:\s*(\d+)', line, re.I):
            parsed = {
                'amount': float(m.group(1).replace(',', '')),
                'type': 'credit',
                'merchant': m.group(2).strip(),
                'date': None,
                'upi_ref': m.group(4).strip(),
                'account_last4': m.group(3).strip()
            }
            
        # Pattern 6: GPay style
        elif m := re.search(r'You paid\s*[₹Rs\.INR]+\s*([\d,]+\.?\d*)\s*to\s*(.*)', line, re.I):
            parsed = {
                'amount': float(m.group(1).replace(',', '')),
                'type': 'debit',
                'merchant': m.group(2).strip(),
                'date': None,
                'upi_ref': None,
                'account_last4': None
            }
            
        # Pattern 7: PhonePe style
        elif m := re.search(r'Payment of\s*[₹Rs\.INR]+\s*([\d,]+\.?\d*)\s*to\s*(.*?)\s*successful', line, re.I):
            parsed = {
                'amount': float(m.group(1).replace(',', '')),
                'type': 'debit',
                'merchant': m.group(2).strip(),
                'date': None,
                'upi_ref': None,
                'account_last4': None
            }
            
        if parsed:
            results.append(parsed)
            
    return results
