import pytest
import json
from app import app, db
from models import Department, KPI, KPIData

@pytest.fixture
def client():
    """Test client fixture"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

@pytest.fixture
def sample_data():
    """Create sample test data"""
    # Create department
    dept = Department(name='Test Department', description='Test Description')
    db.session.add(dept)
    db.session.commit()
    
    # Create KPI
    kpi = KPI(
        name='Test KPI',
        description='Test KPI Description',
        unit='%',
        target_type='higher_better',
        department_id=dept.id
    )
    db.session.add(kpi)
    db.session.commit()
    
    return {'department': dept, 'kpi': kpi}

class TestDepartmentAPI:
    def test_get_departments(self, client, sample_data):
        """Test getting all departments"""
        response = client.get('/api/departments/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 1
        assert data['data'][0]['name'] == 'Test Department'

    def test_create_department(self, client):
        """Test creating a new department"""
        dept_data = {
            'name': 'New Department',
            'description': 'New Department Description'
        }
        
        response = client.post('/api/departments/', 
                             data=json.dumps(dept_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['name'] == 'New Department'

    def test_get_department_kpis(self, client, sample_data):
        """Test getting KPIs for a department"""
        dept_id = sample_data['department'].id
        response = client.get(f'/api/departments/{dept_id}/kpis')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 1

    def test_create_duplicate_department(self, client, sample_data):
        """Test creating department with duplicate name"""
        dept_data = {
            'name': 'Test Department',  # Same as sample_data
            'description': 'Duplicate Department'
        }
        
        response = client.post('/api/departments/', 
                             data=json.dumps(dept_data),
                             content_type='application/json')
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert data['success'] == False

class TestKPIAPI:
    def test_get_kpis(self, client, sample_data):
        """Test getting all KPIs"""
        response = client.get('/api/kpi/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 1

    def test_create_kpi(self, client, sample_data):
        """Test creating a new KPI"""
        kpi_data = {
            'name': 'New Test KPI',
            'description': 'New KPI Description',
            'unit': '$',
            'target_type': 'higher_better',
            'department_id': sample_data['department'].id
        }
        
        response = client.post('/api/kpi/', 
                             data=json.dumps(kpi_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['name'] == 'New Test KPI'

    def test_create_kpi_invalid_department(self, client):
        """Test creating KPI with invalid department ID"""
        kpi_data = {
            'name': 'Invalid KPI',
            'description': 'KPI with invalid department',
            'unit': '$',
            'target_type': 'higher_better',
            'department_id': 999  # Non-existent department
        }
        
        response = client.post('/api/kpi/', 
                             data=json.dumps(kpi_data),
                             content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] == False

    def test_get_kpi_by_id(self, client, sample_data):
        """Test getting specific KPI by ID"""
        kpi_id = sample_data['kpi'].id
        response = client.get(f'/api/kpi/{kpi_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['name'] == 'Test KPI'

    def test_add_kpi_data(self, client, sample_data):
        """Test adding KPI data"""
        kpi_id = sample_data['kpi'].id
        data_point = {
            'value': 85.5,
            'target': 90.0,
            'period': 'daily',
            'notes': 'Test data point',
            'created_by': 'test_user'
        }
        
        response = client.post(f'/api/kpi/{kpi_id}/data',
                             data=json.dumps(data_point),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['value'] == 85.5

    def test_add_kpi_data_missing_value(self, client, sample_data):
        """Test adding KPI data without required value field"""
        kpi_id = sample_data['kpi'].id
        data_point = {
            'target': 90.0,
            'period': 'daily',
            'notes': 'Test data point without value'
        }
        
        response = client.post(f'/api/kpi/{kpi_id}/data',
                             data=json.dumps(data_point),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False

    def test_get_kpi_data(self, client, sample_data):
        """Test getting KPI data"""
        kpi_id = sample_data['kpi'].id
        
        # First add some data
        kpi_data = KPIData(
            kpi_id=kpi_id,
            value=75.0,
            target=80.0,
            period='daily',
            created_by='test_user'
        )
        db.session.add(kpi_data)
        db.session.commit()
        
        response = client.get(f'/api/kpi/{kpi_id}/data')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 1
        assert data['data'][0]['value'] == 75.0

    def test_get_kpi_data_with_limit(self, client, sample_data):
        """Test getting KPI data with limit parameter"""
        kpi_id = sample_data['kpi'].id
        
        # Add multiple data points
        for i in range(5):
            kpi_data = KPIData(
                kpi_id=kpi_id,
                value=70.0 + i,
                target=80.0,
                period='daily',
                created_by='test_user'
            )
            db.session.add(kpi_data)
        db.session.commit()
        
        response = client.get(f'/api/kpi/{kpi_id}/data?limit=3')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 3

    def test_bulk_add_kpi_data(self, client, sample_data):
        """Test bulk adding KPI data"""
        kpi_id = sample_data['kpi'].id
        bulk_data = [
            {
                'kpi_id': kpi_id,
                'value': 80.0,
                'target': 85.0,
                'period': 'daily',
                'created_by': 'bulk_test'
            },
            {
                'kpi_id': kpi_id,
                'value': 82.5,
                'target': 85.0,
                'period': 'daily',
                'created_by': 'bulk_test'
            }
        ]
        
        response = client.post('/api/kpi/data/bulk',
                             data=json.dumps(bulk_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['created_count'] == 2

    def test_bulk_add_invalid_data(self, client, sample_data):
        """Test bulk adding with some invalid data"""
        kpi_id = sample_data['kpi'].id
        bulk_data = [
            {
                'kpi_id': kpi_id,
                'value': 80.0,
                'target': 85.0,
                'period': 'daily',
                'created_by': 'bulk_test'
            },
            {
                'kpi_id': 999,  # Invalid KPI ID
                'value': 82.5,
                'target': 85.0,
                'period': 'daily',
                'created_by': 'bulk_test'
            },
            {
                # Missing required kpi_id and value
                'target': 85.0,
                'period': 'daily',
                'created_by': 'bulk_test'
            }
        ]
        
        response = client.post('/api/kpi/data/bulk',
                             data=json.dumps(bulk_data),
                             content_type='application/json')
        
        # Should still return 201 if at least one item was created
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['created_count'] == 1
        assert len(data['errors']) == 2

    def test_filter_kpis_by_department(self, client, sample_data):
        """Test filtering KPIs by department"""
        dept_id = sample_data['department'].id
        response = client.get(f'/api/kpi/?department_id={dept_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 1
        assert data['data'][0]['department_id'] == dept_id

class TestDashboard:
    def test_dashboard_page(self, client, sample_data):
        """Test dashboard page loads"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'KPI Dashboard' in response.data

    def test_dashboard_data_api(self, client, sample_data):
        """Test dashboard data API"""
        # Add some KPI data first
        kpi_data = KPIData(
            kpi_id=sample_data['kpi'].id,
            value=88.0,
            target=90.0,
            period='daily',
            created_by='test_user'
        )
        db.session.add(kpi_data)
        db.session.commit()
        
        response = client.get('/api/dashboard-data')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'summary' in data
        assert 'recent_kpis' in data
        assert data['summary']['total_departments'] == 1
        assert data['summary']['total_kpis'] == 1
        assert data['summary']['total_data_points'] == 1

    def test_kpi_form_page(self, client, sample_data):
        """Test KPI form page loads"""
        response = client.get('/kpi-form')
        assert response.status_code == 200
        assert b'Add KPI Data' in response.data

class TestErrorHandling:
    def test_get_nonexistent_kpi(self, client):
        """Test getting non-existent KPI"""
        response = client.get('/api/kpi/999')
        assert response.status_code == 404

    def test_get_nonexistent_department(self, client):
        """Test getting non-existent department"""
        response = client.get('/api/departments/999')
        assert response.status_code == 404

    def test_add_data_to_nonexistent_kpi(self, client):
        """Test adding data to non-existent KPI"""
        data_point = {
            'value': 85.5,
            'target': 90.0,
            'period': 'daily'
        }
        
        response = client.post('/api/kpi/999/data',
                             data=json.dumps(data_point),
                             content_type='application/json')
        
        assert response.status_code == 404

    def test_invalid_json_request(self, client):
        """Test sending invalid JSON"""
        response = client.post('/api/departments/',
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 400

class TestPerformanceStatus:
    def test_performance_status_higher_better(self, client, sample_data):
        """Test performance status calculation for higher_better KPIs"""
        kpi_id = sample_data['kpi'].id
        
        # Add data above target
        data_point = {
            'value': 95.0,
            'target': 90.0,
            'period': 'daily',
            'created_by': 'test_user'
        }
        
        response = client.post(f'/api/kpi/{kpi_id}/data',
                             data=json.dumps(data_point),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['data']['performance_status'] == 'Above Target'

    def test_performance_status_lower_better(self, client, sample_data):
        """Test performance status calculation for lower_better KPIs"""
        # Create a lower_better KPI
        kpi = KPI(
            name='Response Time',
            description='Average response time',
            unit='seconds',
            target_type='lower_better',
            department_id=sample_data['department'].id
        )
        db.session.add(kpi)
        db.session.commit()
        
        # Add data below target (good for lower_better)
        data_point = {
            'value': 2.5,
            'target': 3.0,
            'period': 'daily',
            'created_by': 'test_user'
        }
        
        response = client.post(f'/api/kpi/{kpi.id}/data',
                             data=json.dumps(data_point),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['data']['performance_status'] == 'Above Target'

if __name__ == '__main__':
    pytest.main(['-v', __file__])