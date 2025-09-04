from .database import db
from models import Department, KPI, KPIData
from datetime import datetime, timedelta
import random

def init_sample_data(db):
    """Initialize database with sample data"""
    
    if Department.query.first():
        return
    
    departments_data = [
        {'name': 'Sales', 'description': 'Sales and Revenue Generation'},
        {'name': 'Marketing', 'description': 'Marketing and Customer Acquisition'},
        {'name': 'Operations', 'description': 'Operational Efficiency and Quality'},
        {'name': 'Finance', 'description': 'Financial Performance and Management'},
        {'name': 'HR', 'description': 'Human Resources and Employee Management'},
        {'name': 'Customer Service', 'description': 'Customer Support and Satisfaction'}
    ]
    
    departments = []
    for dept_data in departments_data:
        dept = Department(**dept_data)
        db.session.add(dept)
        departments.append(dept)
    
    db.session.commit()
    
    # Create sample KPIs
    kpis_data = [
        # Sales KPIs
        {'name': 'Monthly Revenue', 'description': 'Total monthly revenue', 'unit': '$', 'target_type': 'higher_better', 'department_id': 1},
        {'name': 'Conversion Rate', 'description': 'Lead to customer conversion rate', 'unit': '%', 'target_type': 'higher_better', 'department_id': 1},
        {'name': 'Average Deal Size', 'description': 'Average value per deal', 'unit': '$', 'target_type': 'higher_better', 'department_id': 1},
        
        # Marketing KPIs
        {'name': 'Lead Generation', 'description': 'Number of leads generated', 'unit': 'leads', 'target_type': 'higher_better', 'department_id': 2},
        {'name': 'Cost Per Lead', 'description': 'Average cost to acquire a lead', 'unit': '$', 'target_type': 'lower_better', 'department_id': 2},
        {'name': 'Website Traffic', 'description': 'Monthly website visitors', 'unit': 'visitors', 'target_type': 'higher_better', 'department_id': 2},
        
        # Operations KPIs
        {'name': 'Production Efficiency', 'description': 'Production efficiency percentage', 'unit': '%', 'target_type': 'higher_better', 'department_id': 3},
        {'name': 'Quality Score', 'description': 'Product quality rating', 'unit': 'score', 'target_type': 'higher_better', 'department_id': 3},
        {'name': 'Delivery Time', 'description': 'Average delivery time', 'unit': 'days', 'target_type': 'lower_better', 'department_id': 3},
        
        # Finance KPIs
        {'name': 'Profit Margin', 'description': 'Net profit margin', 'unit': '%', 'target_type': 'higher_better', 'department_id': 4},
        {'name': 'Cash Flow', 'description': 'Monthly cash flow', 'unit': '$', 'target_type': 'higher_better', 'department_id': 4},
        
        # HR KPIs
        {'name': 'Employee Satisfaction', 'description': 'Employee satisfaction score', 'unit': 'score', 'target_type': 'higher_better', 'department_id': 5},
        {'name': 'Turnover Rate', 'description': 'Employee turnover rate', 'unit': '%', 'target_type': 'lower_better', 'department_id': 5},
        
        # Customer Service KPIs
        {'name': 'Customer Satisfaction', 'description': 'Customer satisfaction score', 'unit': 'score', 'target_type': 'higher_better', 'department_id': 6},
        {'name': 'Response Time', 'description': 'Average response time', 'unit': 'hours', 'target_type': 'lower_better', 'department_id': 6}
    ]
    
    kpis = []
    for kpi_data in kpis_data:
        kpi = KPI(**kpi_data)
        db.session.add(kpi)
        kpis.append(kpi)
    
    db.session.commit()
    
    # Generate sample KPI data for the last 30 days
    base_date = datetime.utcnow() - timedelta(days=30)
    
    for kpi in kpis:
        for i in range(30):
            current_date = base_date + timedelta(days=i)
            
            # Generate realistic sample data based on KPI type
            if 'Revenue' in kpi.name or 'Cash Flow' in kpi.name:
                value = random.uniform(50000, 150000)
                target = 100000
            elif 'Rate' in kpi.name or 'Margin' in kpi.name or 'Efficiency' in kpi.name:
                value = random.uniform(60, 95)
                target = 80
            elif 'Time' in kpi.name:
                value = random.uniform(1, 10)
                target = 5
            elif 'Score' in kpi.name or 'Satisfaction' in kpi.name:
                value = random.uniform(3.5, 5.0)
                target = 4.5
            elif 'Traffic' in kpi.name or 'Generation' in kpi.name:
                value = random.uniform(1000, 5000)
                target = 3000
            else:
                value = random.uniform(50, 150)
                target = 100
            
            kpi_data_point = KPIData(
                kpi_id=kpi.id,
                value=round(value, 2),
                target=target,
                timestamp=current_date,
                period='daily',
                created_by='system'
            )
            db.session.add(kpi_data_point)
    
    db.session.commit()
    print("Sample data initialized successfully!")