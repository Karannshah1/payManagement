from flask import Blueprint, request, jsonify, render_template
from models import db, Category, Expense

categories = Blueprint('categories', __name__, url_prefix='/categories')

@categories.route('/')
def categories_page():
    return render_template('categories.html')

@categories.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        cats = Category.query.all()
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'is_custom': getattr(c, 'is_custom', False),
            'color': getattr(c, 'color', None)
        } for c in cats])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@categories.route('/api/categories', methods=['POST'])
def create_category():
    try:
        data = request.get_json()
        category = Category(
            name=data['name'],
            is_custom=True,
            color=data.get('color')
        )
        db.session.add(category)
        db.session.commit()
        return jsonify({'message': 'Category created', 'id': category.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@categories.route('/api/categories/<int:id>', methods=['PUT'])
def update_category(id):
    try:
        category = Category.query.get(id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404
            
        if not getattr(category, 'is_custom', False):
            return jsonify({'error': 'Cannot update built-in category'}), 400
            
        data = request.get_json()
        if 'name' in data:
            category.name = data['name']
        if 'color' in data:
            category.color = data['color']
            
        db.session.commit()
        return jsonify({'message': 'Category updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@categories.route('/api/categories/<int:id>', methods=['DELETE'])
def delete_category(id):
    try:
        category = Category.query.get(id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404
            
        if not getattr(category, 'is_custom', False):
            return jsonify({'error': 'Cannot delete built-in category'}), 400
            
        has_expenses = Expense.query.filter_by(category_id=id).first()
        if has_expenses:
            return jsonify({'error': 'Cannot delete category linked to expenses'}), 400
            
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
