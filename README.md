# Enterprise KPI Monitoring System

A comprehensive Flask-based KPI monitoring system with REST APIs and Power BI integration for real-time organizational performance tracking.

## Features

- **RESTful API**: Complete CRUD operations for KPIs, departments, and data points
- **Power BI Integration**: Real-time data sync with Power BI dashboards
- **Multi-Department Support**: Track KPIs across different organizational units
- **Real-time Dashboard**: Live performance monitoring and visualization
- **Bulk Data Import**: Support for bulk KPI data ingestion
- **Performance Analytics**: Automatic performance status calculation
- **Responsive Design**: Mobile-friendly web interface

## Technology Stack

- **Backend**: Flask, SQLAlchemy, Python 3.8+
- **Database**: SQLite (configurable to PostgreSQL/MySQL)
- **Frontend**: HTML5, CSS3, JavaScript
- **Integration**: Power BI REST APIs, MSAL authentication
- **Testing**: Pytest
- **Deployment**: Gunicorn ready

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/enterprise-kpi-system.git
cd enterprise-kpi-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///kpi_monitoring.db

# Power BI Configuration (Optional)
POWERBI_CLIENT_ID=your-powerbi-client-id
POWERBI_CLIENT_SECRET=your-powerbi-client-secret
POWERBI_TENANT_ID=your-tenant-id
POWERBI_WORKSPACE_ID=your-workspace-id
```

### 3. Database Setup

```bash
python app.py
```

### 4. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## API Documentation

### Departments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/departments/` | Get all departments |
| POST | `/api/departments/` | Create new department |
| GET | `/api/departments/{id}` | Get specific department |
| GET | `/api/departments/{id}/kpis` | Get department KPIs |

### KPIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/kpi/` | Get all KPIs |
| POST | `/api/kpi/` | Create new KPI |
| GET | `/api/kpi/{id}` | Get specific KPI |
| GET | `/api/kpi/{id}/data` | Get KPI data points |
| POST | `/api/kpi/{id}/data` | Add KPI data point |
| POST | `/api/kpi/data/bulk` | Bulk add KPI data |

### Example API Usage

#### Add KPI Data Point

```bash
curl -X POST "http://localhost:5000/api/kpi/1/data" \
  -H "Content-Type: application/json" \
  -d '{
    "value": 95.5,
    "target": 90.0,
    "period": "daily",
    "notes": "Exceeded target performance",
    "created_by": "john.doe"
  }'
```

#### Bulk Add KPI Data

```bash
curl -X POST "http://localhost:5000/api/kpi/data/bulk" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "kpi_id": 1,
      "value": 88.0,
      "target": 85.0,
      "period": "daily",
      "created_by": "system"
    },
    {
      "kpi_id": 2,
      "value": 150000,
      "target": 140000,
      "period": "monthly",
      "created_by": "system"
    }
  ]'
```

## Power BI Integration

### Setup

1. Register an application in Azure AD
2. Grant Power BI API permissions
3. Configure the environment variables
4. Create a Power BI workspace and dataset

### Data Sync

The system automatically formats data for Power BI consumption:

```python
from powerbi.integration import PowerBIIntegration

powerbi = PowerBIIntegration()

from powerbi.integration import sync_kpi_data_to_powerbi
sync_kpi_data_to_powerbi()
```

## Project Structure

```
enterprise-kpi-system/
├── app.py                 # Main Flask application
├── models.py             # Database models
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
├── database/
│   └── init_db.py       # Database initialization
├── api/
│   ├── __init__.py
│   ├── kpi_routes.py    # KPI API endpoints
│   └── department_routes.py # Department API endpoints
├── powerbi/
│   ├── __init__.py
│   └── integration.py   # Power BI integration
├── static/
│   ├── css/
│   │   └── style.css    # Stylesheet
│   └── js/
│       └── dashboard.js # Frontend JavaScript
├── templates/
│   ├── base.html        # Base template
│   ├── dashboard.html   # Dashboard page
│   └── kpi_form.html   # KPI form page
└── tests/
    ├── __init__.py
    └── test_api.py      # API tests
```

## Database Schema

### Departments
- id (Primary Key)
- name (Unique)
- description
- created_at

### KPIs
- id (Primary Key)
- name
- description
- unit
- target_type
- department_id (Foreign Key)
- created_at
- is_active

### KPI Data
- id (Primary Key)
- kpi_id (Foreign Key)
- value
- target
- timestamp
- period
- notes
- created_by

## Testing

Run the test suite:

```bash
pip install pytest pytest-flask

pytest tests/

pytest --cov=. tests/
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### Environment Variables for Production

```env
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@localhost/kpi_db
POWERBI_CLIENT_ID=your-client-id
POWERBI_CLIENT_SECRET=your-client-secret
POWERBI_TENANT_ID=your-tenant-id
POWERBI_WORKSPACE_ID=your-workspace-id
```

## Sample Data

The system comes with pre-loaded sample data including:

- **Departments**: Sales, Marketing, Operations, Finance, HR, Customer Service
- **KPIs**: Revenue metrics, conversion rates, efficiency scores, satisfaction ratings
- **Historical Data**: 30 days of sample KPI data points

## API Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": [...],
  "message": "Operation completed successfully",
  "count": 10
}
```

Error responses:

```json
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support, please open an issue in the GitHub repository.
