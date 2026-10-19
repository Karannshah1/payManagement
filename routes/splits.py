from flask import Blueprint, request, jsonify, render_template
from models import db, SplitGroup, SplitMember

splits = Blueprint('splits', __name__, url_prefix='/splits')

@splits.route('/')
def splits_page():
    return render_template('splits.html')

@splits.route('/api/splits', methods=['GET'])
def get_splits():
    try:
        groups = SplitGroup.query.all()
        result = []
        for g in groups:
            members = SplitMember.query.filter_by(group_id=g.id).all()
            result.append({
                'id': g.id,
                'name': g.name,
                'total_amount': g.total_amount,
                'is_settled': getattr(g, 'is_settled', False),
                'date': g.date.isoformat() if getattr(g, 'date', None) else None,
                'members': [{
                    'id': m.id,
                    'name': m.name,
                    'share_amount': m.share_amount,
                    'paid_amount': m.paid_amount
                } for m in members]
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@splits.route('/api/splits', methods=['POST'])
def create_split():
    try:
        data = request.get_json()
        group = SplitGroup(
            name=data['name'],
            total_amount=float(data.get('total_amount', 0)),
            is_settled=False
        )
        if 'date' in data:
            from datetime import date
            group.date = date.fromisoformat(data['date'])
            
        db.session.add(group)
        db.session.flush() # To get group.id
        
        members_data = data.get('members', [])
        for m_data in members_data:
            member = SplitMember(
                group_id=group.id,
                name=m_data['name'],
                share_amount=float(m_data.get('share_amount', 0)),
                paid_amount=float(m_data.get('paid_amount', 0))
            )
            db.session.add(member)
            
        db.session.commit()
        return jsonify({'message': 'Split group created', 'id': group.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@splits.route('/api/splits/<int:id>/settle', methods=['PUT'])
def settle_split(id):
    try:
        group = SplitGroup.query.get(id)
        if not group:
            return jsonify({'error': 'Split group not found'}), 404
            
        group.is_settled = True
        db.session.commit()
        return jsonify({'message': 'Split marked as settled'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@splits.route('/api/splits/<int:id>', methods=['DELETE'])
def delete_split(id):
    try:
        group = SplitGroup.query.get(id)
        if not group:
            return jsonify({'error': 'Split group not found'}), 404
            
        SplitMember.query.filter_by(group_id=id).delete()
        db.session.delete(group)
        db.session.commit()
        return jsonify({'message': 'Split group deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
