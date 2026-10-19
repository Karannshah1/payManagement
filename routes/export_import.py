from flask import Blueprint, request, jsonify, render_template, send_file
from models import db, Expense, Income, Category, Account
from datetime import date
import pandas as pd
import io
import openpyxl

export_import = Blueprint('export_import', __name__, url_prefix='')

@export_import.route('/import')
def import_page():
    return render_template('smart-import.html')

@export_import.route('/export/excel', methods=['GET'])
def export_excel():
    try:
        query = db.session.query(
            Expense.date, Expense.amount, Category.name.label('category'),
            Account.name.label('account'), getattr(Expense, 'payment_method', Expense.id).label('payment_method'), 
            Expense.description, getattr(Expense, 'tags', Expense.id).label('tags')
        ).join(Category, Expense.category_id == Category.id)\
         .join(Account, Expense.account_id == Account.id)
         
        date_from = request.args.get('date_from')
        if date_from:
            query = query.filter(Expense.date >= date.fromisoformat(date_from))
        date_to = request.args.get('date_to')
        if date_to:
            query = query.filter(Expense.date <= date.fromisoformat(date_to))
        account_id = request.args.get('account_id')
        if account_id:
            query = query.filter(Expense.account_id == account_id)
        category_id = request.args.get('category_id')
        if category_id:
            query = query.filter(Expense.category_id == category_id)
            
        df = pd.DataFrame([{
            'Date': r.date.isoformat(),
            'Amount': r.amount,
            'Category': r.category,
            'Account': r.account,
            'Payment Method': getattr(r, 'payment_method', ''),
            'Description': r.description,
            'Tags': getattr(r, 'tags', '')
        } for r in query.all()])
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Expenses')
        output.seek(0)
        
        return send_file(output, as_attachment=True, download_name='export.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@export_import.route('/export/csv', methods=['GET'])
def export_csv():
    try:
        query = db.session.query(
            Expense.date, Expense.amount, Category.name.label('category'),
            Account.name.label('account'), getattr(Expense, 'payment_method', Expense.id).label('payment_method'), 
            Expense.description
        ).join(Category, Expense.category_id == Category.id)\
         .join(Account, Expense.account_id == Account.id)
         
        date_from = request.args.get('date_from')
        if date_from:
            query = query.filter(Expense.date >= date.fromisoformat(date_from))
        date_to = request.args.get('date_to')
        if date_to:
            query = query.filter(Expense.date <= date.fromisoformat(date_to))
        account_id = request.args.get('account_id')
        if account_id:
            query = query.filter(Expense.account_id == account_id)
        category_id = request.args.get('category_id')
        if category_id:
            query = query.filter(Expense.category_id == category_id)
            
        df = pd.DataFrame([{
            'Date': r.date.isoformat(),
            'Amount': r.amount,
            'Category': r.category,
            'Account': r.account,
            'Payment Method': getattr(r, 'payment_method', ''),
            'Description': r.description
        } for r in query.all()])
        
        output = io.BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        return send_file(output, as_attachment=True, download_name='export.csv', mimetype='text/csv')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@export_import.route('/api/import/excel-csv', methods=['POST'])
def preview_import():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        filename = file.filename.lower()
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(file)
        else:
            return jsonify({'error': 'Unsupported file format'}), 400
            
        # Basic parsing, replace nan with None
        df = df.where(pd.notnull(df), None)
        
        preview = df.head(10).to_dict(orient='records')
        return jsonify({'preview': preview, 'columns': df.columns.tolist(), 'total_rows': len(df)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@export_import.route('/api/import/confirm', methods=['POST'])
def confirm_import():
    try:
        data = request.get_json()
        entries = data.get('entries', [])
        
        default_account = Account.query.first()
        default_category = Category.query.first()
        
        if not default_account:
            return jsonify({'error': 'No account available for import'}), 400
            
        count = 0
        for entry in entries:
            # Assuming minimal mapping is done client side or simple structure
            amount = entry.get('amount') or entry.get('Amount')
            if not amount:
                continue
                
            expense = Expense(
                amount=float(amount),
                description=entry.get('description') or entry.get('Description', 'Imported'),
                date=date.fromisoformat(str(entry.get('date') or entry.get('Date'))[:10]) if entry.get('date') or entry.get('Date') else date.today(),
                account_id=entry.get('account_id', default_account.id),
                category_id=entry.get('category_id', default_category.id if default_category else None)
            )
            db.session.add(expense)
            account = Account.query.get(expense.account_id)
            if account:
                account.balance -= float(amount)
            count += 1
            
        db.session.commit()
        return jsonify({'message': f'Imported {count} entries successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

from services.ai_parser import parse_transaction_with_ai

@export_import.route('/api/import/ai-parse', methods=['POST'])
def ai_parse_text():
    try:
        raw_text = ""
        
        # Handle file upload (PDF/Text)
        if 'file' in request.files:
            file = request.files['file']
            if file.filename.endswith('.pdf'):
                import pypdf
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    raw_text += page.extract_text() + "\n"
            else:
                raw_text = file.read().decode('utf-8')
        # Handle JSON text payload
        elif request.is_json:
            data = request.get_json()
            raw_text = data.get('text', '')
            
        raw_text = raw_text.strip()
        if not raw_text:
            return jsonify({'error': 'No text or valid file provided'}), 400
            
        # Limit text size to avoid blowing up the LLM context
        raw_text = raw_text[:8000]
            
        parsed_data = parse_transaction_with_ai(raw_text)
        return jsonify({'parsed': parsed_data}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
