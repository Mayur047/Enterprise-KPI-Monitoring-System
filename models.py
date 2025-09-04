from database.database import db
from datetime import datetime

class Department(db.Model):
    """Department model"""
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    kpis = db.relationship('KPI', backref='department', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'kpi_count': len(self.kpis)
        }

class KPI(db.Model):
    """KPI definition model"""
    __tablename__ = 'kpis'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    unit = db.Column(db.String(50))
    target_type = db.Column(db.String(20), default='higher_better')
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    kpi_data = db.relationship('KPIData', backref='kpi', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'unit': self.unit,
            'target_type': self.target_type,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'data_points': len(self.kpi_data)
        }

class KPIData(db.Model):
    """KPI data points model"""
    __tablename__ = 'kpi_data'
    
    id = db.Column(db.Integer, primary_key=True)
    kpi_id = db.Column(db.Integer, db.ForeignKey('kpis.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    target = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    period = db.Column(db.String(20), default='daily')
    notes = db.Column(db.Text)
    created_by = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'kpi_id': self.kpi_id,
            'kpi_name': self.kpi.name if self.kpi else None,
            'department_name': self.kpi.department.name if self.kpi and self.kpi.department else None,
            'value': self.value,
            'target': self.target,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'period': self.period,
            'notes': self.notes,
            'created_by': self.created_by,
            'performance_status': self.get_performance_status()
        }
    
    def get_performance_status(self):
        """Calculate performance status based on value vs target"""
        if not self.target:
            return 'No Target Set'
        
        if not self.kpi:
            return 'Unknown'
            
        if self.kpi.target_type == 'higher_better':
            if self.value >= self.target:
                return 'Above Target'
            else:
                return 'Below Target'
        elif self.kpi.target_type == 'lower_better':
            if self.value <= self.target:
                return 'Above Target'
            else:
                return 'Below Target'
        else:
            return 'On Target' if self.value == self.target else 'Off Target'