from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()


# ---------------------------------------------------------------------------
# Account
# ---------------------------------------------------------------------------
class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(30), nullable=False)  # cash, bank, credit_card, upi_wallet
    balance = db.Column(db.Float, default=0.0)
    icon = db.Column(db.String(50), default='bi-wallet2')
    color = db.Column(db.String(20), default='#0d6efd')
    include_in_tax_report = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    expenses = db.relationship('Expense', backref='account', lazy='dynamic')
    incomes = db.relationship('Income', backref='account', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'account_type': self.account_type,
            'balance': self.balance,
            'icon': self.icon,
            'color': self.color,
            'include_in_tax_report': self.include_in_tax_report,
            'is_active': self.is_active,
        }


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False, unique=True)
    icon = db.Column(db.String(50), default='bi-tag')
    color = db.Column(db.String(20), default='#6c757d')
    is_custom = db.Column(db.Boolean, default=False)
    is_income_category = db.Column(db.Boolean, default=False)

    expenses = db.relationship('Expense', backref='category', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'color': self.color,
            'is_custom': self.is_custom,
            'is_income_category': self.is_income_category,
        }


# ---------------------------------------------------------------------------
# Expense
# ---------------------------------------------------------------------------
class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    amount = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    payment_method = db.Column(db.String(30), default='cash')  # cash, upi, card, net_banking
    description = db.Column(db.String(255), default='')
    tags = db.Column(db.String(255), default='')
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_type = db.Column(db.String(20), default=None)  # daily, weekly, monthly, yearly
    receipt_path = db.Column(db.String(500), default=None)
    split_group_id = db.Column(db.Integer, db.ForeignKey('split_groups.id'), default=None)
    is_tax_deductible_override = db.Column(db.Boolean, default=None)  # None=use account default
    import_source = db.Column(db.String(30), default='manual')  # manual, scan, sms, email, screenshot, qr, csv, pdf_bill
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'amount': self.amount,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else '',
            'category_color': self.category.color if self.category else '#6c757d',
            'category_icon': self.category.icon if self.category else 'bi-tag',
            'account_id': self.account_id,
            'account_name': self.account.name if self.account else '',
            'account_type': self.account.account_type if self.account else '',
            'payment_method': self.payment_method,
            'description': self.description,
            'tags': self.tags,
            'is_recurring': self.is_recurring,
            'recurrence_type': self.recurrence_type,
            'receipt_path': self.receipt_path,
            'is_tax_deductible_override': self.is_tax_deductible_override,
            'import_source': self.import_source,
        }

    @property
    def is_cash(self):
        return self.account and self.account.account_type == 'cash'

    @property
    def include_in_tax(self):
        if self.is_tax_deductible_override is not None:
            return self.is_tax_deductible_override
        return self.account.include_in_tax_report if self.account else True


# ---------------------------------------------------------------------------
# Income
# ---------------------------------------------------------------------------
class Income(db.Model):
    __tablename__ = 'incomes'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(100), nullable=False)  # salary, freelance, investment, etc.
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    description = db.Column(db.String(255), default='')
    import_source = db.Column(db.String(30), default='manual')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'amount': self.amount,
            'source': self.source,
            'account_id': self.account_id,
            'account_name': self.account.name if self.account else '',
            'description': self.description,
            'import_source': self.import_source,
        }


# ---------------------------------------------------------------------------
# Transfer (between accounts)
# ---------------------------------------------------------------------------
class Transfer(db.Model):
    __tablename__ = 'transfers'
    id = db.Column(db.Integer, primary_key=True)
    from_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    to_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(255), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    from_account = db.relationship('Account', foreign_keys=[from_account_id], backref='transfers_out')
    to_account = db.relationship('Account', foreign_keys=[to_account_id], backref='transfers_in')

    def to_dict(self):
        return {
            'id': self.id,
            'from_account_id': self.from_account_id,
            'from_account_name': self.from_account.name if self.from_account else '',
            'to_account_id': self.to_account_id,
            'to_account_name': self.to_account.name if self.to_account else '',
            'amount': self.amount,
            'date': self.date.isoformat(),
            'description': self.description,
        }


# ---------------------------------------------------------------------------
# Budget
# ---------------------------------------------------------------------------
class Budget(db.Model):
    __tablename__ = 'budgets'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    limit_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship('Category', backref='budgets')

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else '',
            'month': self.month,
            'year': self.year,
            'limit_amount': self.limit_amount,
        }


# ---------------------------------------------------------------------------
# Savings Goal
# ---------------------------------------------------------------------------
class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.Date, default=None)
    icon = db.Column(db.String(50), default='bi-piggy-bank')
    color = db.Column(db.String(20), default='#198754')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'progress': round((self.current_amount / self.target_amount) * 100, 1) if self.target_amount > 0 else 0,
            'icon': self.icon,
            'color': self.color,
        }


# ---------------------------------------------------------------------------
# EMI
# ---------------------------------------------------------------------------
class EMI(db.Model):
    __tablename__ = 'emis'
    id = db.Column(db.Integer, primary_key=True)
    loan_name = db.Column(db.String(100), nullable=False)
    emi_amount = db.Column(db.Float, nullable=False)
    total_tenure = db.Column(db.Integer, nullable=False)  # in months
    completed_months = db.Column(db.Integer, default=0)
    interest_rate = db.Column(db.Float, default=0.0)
    start_date = db.Column(db.Date, nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), default=None)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    account = db.relationship('Account', backref='emis')

    def to_dict(self):
        remaining = self.total_tenure - self.completed_months
        return {
            'id': self.id,
            'loan_name': self.loan_name,
            'emi_amount': self.emi_amount,
            'total_tenure': self.total_tenure,
            'completed_months': self.completed_months,
            'remaining_months': remaining,
            'interest_rate': self.interest_rate,
            'start_date': self.start_date.isoformat(),
            'total_paid': self.emi_amount * self.completed_months,
            'total_remaining': self.emi_amount * remaining,
            'is_active': self.is_active,
        }


# ---------------------------------------------------------------------------
# Split Group & Members
# ---------------------------------------------------------------------------
class SplitGroup(db.Model):
    __tablename__ = 'split_groups'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    settled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    members = db.relationship('SplitMember', backref='split_group', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'total_amount': self.total_amount,
            'date': self.date.isoformat(),
            'settled': self.settled,
            'members': [m.to_dict() for m in self.members],
        }


class SplitMember(db.Model):
    __tablename__ = 'split_members'
    id = db.Column(db.Integer, primary_key=True)
    split_group_id = db.Column(db.Integer, db.ForeignKey('split_groups.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    share_amount = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'share_amount': self.share_amount,
            'paid_amount': self.paid_amount,
            'owed': round(self.share_amount - self.paid_amount, 2),
        }


# ---------------------------------------------------------------------------
# Subscription
# ---------------------------------------------------------------------------
class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    billing_cycle = db.Column(db.String(20), default='monthly')  # monthly, yearly, weekly
    next_renewal = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), default=None)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), default=None)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship('Category', backref='subscriptions')
    account = db.relationship('Account', backref='subscriptions')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.amount,
            'billing_cycle': self.billing_cycle,
            'next_renewal': self.next_renewal.isoformat(),
            'category_name': self.category.name if self.category else '',
            'account_name': self.account.name if self.account else '',
            'is_active': self.is_active,
        }


# ---------------------------------------------------------------------------
# Reminder
# ---------------------------------------------------------------------------
class Reminder(db.Model):
    __tablename__ = 'reminders'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, default=None)
    due_date = db.Column(db.Date, nullable=False)
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_type = db.Column(db.String(20), default=None)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'amount': self.amount,
            'due_date': self.due_date.isoformat(),
            'is_recurring': self.is_recurring,
            'recurrence_type': self.recurrence_type,
            'is_completed': self.is_completed,
        }


# ---------------------------------------------------------------------------
# Expense Template
# ---------------------------------------------------------------------------
class ExpenseTemplate(db.Model):
    __tablename__ = 'expense_templates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), default=None)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), default=None)
    payment_method = db.Column(db.String(30), default='upi')
    description = db.Column(db.String(255), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship('Category', backref='templates')
    account = db.relationship('Account', backref='templates')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.amount,
            'category_name': self.category.name if self.category else '',
            'account_name': self.account.name if self.account else '',
            'payment_method': self.payment_method,
            'description': self.description,
        }


# ---------------------------------------------------------------------------
# Scanned Document (bill scanner history)
# ---------------------------------------------------------------------------
class ScannedDocument(db.Model):
    __tablename__ = 'scanned_documents'
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(20), default='image')  # image, pdf, screenshot
    raw_text = db.Column(db.Text, default='')
    extracted_data = db.Column(db.Text, default='{}')  # JSON
    classified_as = db.Column(db.String(20), default='expense')  # expense, income
    confidence_score = db.Column(db.Float, default=0.0)
    qr_data = db.Column(db.Text, default=None)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'), default=None)
    income_id = db.Column(db.Integer, db.ForeignKey('incomes.id'), default=None)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    expense = db.relationship('Expense', backref='scanned_doc')
    income = db.relationship('Income', backref='scanned_doc')


# ---------------------------------------------------------------------------
# Setting
# ---------------------------------------------------------------------------
class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(255), default='')

    @staticmethod
    def get(key, default=''):
        s = Setting.query.filter_by(key=key).first()
        return s.value if s else default

    @staticmethod
    def set(key, value):
        s = Setting.query.filter_by(key=key).first()
        if s:
            s.value = str(value)
        else:
            s = Setting(key=key, value=str(value))
            db.session.add(s)
        db.session.commit()


# ---------------------------------------------------------------------------
# Seed default data
# ---------------------------------------------------------------------------
def seed_defaults():
    """Create default categories and accounts if they don't exist."""
    if Category.query.first() is None:
        defaults = [
            Category(name='Food & Dining', icon='bi-cup-hot', color='#e74c3c'),
            Category(name='Transport', icon='bi-bus-front', color='#3498db'),
            Category(name='Rent', icon='bi-house-door', color='#9b59b6'),
            Category(name='Utilities', icon='bi-lightning', color='#f39c12'),
            Category(name='Entertainment', icon='bi-film', color='#e91e63'),
            Category(name='Health', icon='bi-heart-pulse', color='#1abc9c'),
            Category(name='Shopping', icon='bi-bag', color='#e67e22'),
            Category(name='Education', icon='bi-book', color='#2ecc71'),
            Category(name='Subscriptions', icon='bi-repeat', color='#00bcd4'),
            Category(name='Groceries', icon='bi-cart3', color='#8bc34a'),
            Category(name='Personal Care', icon='bi-person', color='#ff9800'),
            Category(name='Miscellaneous', icon='bi-three-dots', color='#95a5a6'),
        ]
        db.session.add_all(defaults)

    if Account.query.first() is None:
        default_accounts = [
            Account(name='Cash', account_type='cash', icon='bi-cash-stack',
                    color='#198754', include_in_tax_report=False, balance=0),
            Account(name='Bank Account', account_type='bank', icon='bi-bank',
                    color='#0d6efd', include_in_tax_report=True, balance=0),
            Account(name='Credit Card', account_type='credit_card', icon='bi-credit-card',
                    color='#dc3545', include_in_tax_report=True, balance=0),
            Account(name='UPI Wallet', account_type='upi_wallet', icon='bi-phone',
                    color='#6f42c1', include_in_tax_report=True, balance=0),
        ]
        db.session.add_all(default_accounts)

    # Default settings
    if Setting.query.first() is None:
        defaults_settings = [
            Setting(key='currency_symbol', value='₹'),
            Setting(key='currency_code', value='INR'),
            Setting(key='theme', value='light'),
            Setting(key='fiscal_year_start', value='4'),  # April
        ]
        db.session.add_all(defaults_settings)

    db.session.commit()

