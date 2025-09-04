from flask import Blueprint, request, jsonify
from models import KPI, KPIData, Department
from database import db
from datetime import datetime

kpi_bp = Blueprint('kpi', __name__)

@kpi_bp.route('/', methods=['GET'])
def get_kpis():
    """Get all KPIs with optional filtering"""
    try:
        department_id = request.args.get('department_id', type=int)
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        query = KPI.query
        
        if department_id:
            query = query.filter_by(department_id=department_id)
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        kpis = query.all()
        
        return jsonify({
            'success': True,
            'data': [kpi.to_dict() for kpi in kpis],
            'count': len(kpis)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@kpi_bp.route('/', methods=['POST'])
def create_kpi():
    """Create a new KPI"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'department_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Validate department exists
        department = Department.query.get(data['department_id'])
        if not department:
            return jsonify({'success': False, 'error': 'Department not found'}), 404
        
        # Create new KPI
        kpi = KPI(
            name=data['name'],
            description=data.get('description', ''),
            unit=data.get('unit', ''),
            target_type=data.get('target_type', 'higher_better'),
            department_id=data['department_id'],
            is_active=data.get('is_active', True)
        )
        
        db.session.add(kpi)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'KPI created successfully',
            'data': kpi.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@kpi_bp.route('/<int:kpi_id>', methods=['GET'])
def get_kpi(kpi_id):
    """Get a specific KPI by ID"""
    try:
        kpi = KPI.query.get_or_404(kpi_id)
        return jsonify({
            'success': True,
            'data': kpi.to_dict()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@kpi_bp.route('/<int:kpi_id>/data', methods=['GET'])
def get_kpi_data(kpi_id):
    """Get data points for a specific KPI"""
    try:
        kpi = KPI.query.get_or_404(kpi_id)
        
        # Get query parameters for filtering
        limit = request.args.get('limit', 100, type=int)
        period = request.args.get('period')
        
        query = KPIData.query.filter_by(kpi_id=kpi_id)
        
        if period:
            query = query.filter_by(period=period)
        
        kpi_data = query.order_by(KPIData.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [data.to_dict() for data in kpi_data],
            'count': len(kpi_data),
            'kpi': kpi.to_dict()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@kpi_bp.route('/<int:kpi_id>/data', methods=['POST'])
def add_kpi_data(kpi_id):
    """Add new data point for a KPI"""
    try:
        kpi = KPI.query.get_or_404(kpi_id)
        data = request.get_json()
        
        # Validate required fields
        if 'value' not in data:
            return jsonify({'success': False, 'error': 'Missing required field: value'}), 400
        
        # Create new KPI data point
        kpi_data = KPIData(
            kpi_id=kpi_id,
            value=float(data['value']),
            target=float(data.get('target', 0)) if data.get('target') else None,
            period=data.get('period', 'daily'),
            notes=data.get('notes', ''),
            created_by=data.get('created_by', 'api_user'),
            timestamp=datetime.fromisoformat(data['timestamp']) if data.get('timestamp') else datetime.utcnow()
        )
        
        db.session.add(kpi_data)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'KPI data added successfully',
            'data': kpi_data.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({'success': False, 'error': 'Invalid data format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@kpi_bp.route('/data/bulk', methods=['POST'])
def bulk_add_kpi_data():
    """Bulk add KPI data points"""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'success': False, 'error': 'Data must be a list of KPI data points'}), 400
        
        created_count = 0
        errors = []
        
        for i, item in enumerate(data):
            try:
                # Validate required fields
                if 'kpi_id' not in item or 'value' not in item:
                    errors.append(f'Item {i}: Missing required fields (kpi_id, value)')
                    continue
                
                # Validate KPI exists
                kpi = KPI.query.get(item['kpi_id'])
                if not kpi:
                    errors.append(f'Item {i}: KPI with ID {item["kpi_id"]} not found')
                    continue
                
                # Create KPI data point
                kpi_data = KPIData(
                    kpi_id=int(item['kpi_id']),
                    value=float(item['value']),
                    target=float(item.get('target', 0)) if item.get('target') else None,
                    period=item.get('period', 'daily'),
                    notes=item.get('notes', ''),
                    created_by=item.get('created_by', 'bulk_api'),
                    timestamp=datetime.fromisoformat(item['timestamp']) if item.get('timestamp') else datetime.utcnow()
                )
                
                db.session.add(kpi_data)
                created_count += 1
                
            except (ValueError, KeyError) as e:
                errors.append(f'Item {i}: Invalid data format - {str(e)}')
                continue
        
        if created_count > 0:
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Bulk operation completed. {created_count} items created.',
            'created_count': created_count,
            'errors': errors
        }), 201 if created_count > 0 else 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500