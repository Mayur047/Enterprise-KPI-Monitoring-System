from flask import Blueprint, request, jsonify
from models import Department, KPI
from database import db

dept_bp = Blueprint('departments', __name__)

@dept_bp.route('/', methods=['GET'])
def get_departments():
    """Get all departments"""
    try:
        departments = Department.query.all()
        return jsonify({
            'success': True,
            'data': [dept.to_dict() for dept in departments],
            'count': len(departments)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@dept_bp.route('/', methods=['POST'])
def create_department():
    """Create a new department"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'name' not in data:
            return jsonify({'success': False, 'error': 'Missing required field: name'}), 400
        
        # Check if department name already exists
        existing_dept = Department.query.filter_by(name=data['name']).first()
        if existing_dept:
            return jsonify({'success': False, 'error': 'Department with this name already exists'}), 409
        
        # Create new department
        department = Department(
            name=data['name'],
            description=data.get('description', '')
        )
        
        db.session.add(department)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Department created successfully',
            'data': department.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@dept_bp.route('/<int:dept_id>', methods=['GET'])
def get_department(dept_id):
    """Get a specific department by ID"""
    try:
        department = Department.query.get_or_404(dept_id)
        return jsonify({
            'success': True,
            'data': department.to_dict()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@dept_bp.route('/<int:dept_id>/kpis', methods=['GET'])
def get_department_kpis(dept_id):
    """Get all KPIs for a specific department"""
    try:
        department = Department.query.get_or_404(dept_id)
        kpis = KPI.query.filter_by(department_id=dept_id).all()
        
        return jsonify({
            'success': True,
            'data': [kpi.to_dict() for kpi in kpis],
            'count': len(kpis),
            'department': department.to_dict()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500