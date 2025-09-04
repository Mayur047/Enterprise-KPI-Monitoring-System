from flask import Flask, render_template, request, jsonify, redirect, flash
from flask_cors import CORS
from datetime import datetime
import os
from config import Config
from database import db
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

db.init_app(app)
CORS(app)

from models import Department, KPI, KPIData

from api.kpi_routes import kpi_bp
from api.department_routes import dept_bp

app.register_blueprint(kpi_bp, url_prefix='/api/kpi')
app.register_blueprint(dept_bp, url_prefix='/api/departments')

@app.route('/')
def dashboard():
    """Main dashboard page"""
    departments = Department.query.all()
    recent_kpis = KPIData.query.order_by(KPIData.timestamp.desc()).limit(10).all()
    return render_template('dashboard.html', departments=departments, recent_kpis=recent_kpis)

@app.route('/kpi-form')
def kpi_form():
    """KPI data entry form"""
    departments = Department.query.all()
    kpis = KPI.query.all()
    return render_template('kpi_form.html', departments=departments, kpis=kpis)

@app.route('/add-kpi-data', methods=['POST'])
def add_kpi_data():
    """Handle KPI data form submission"""
    try:
        kpi_id = request.form.get('kpi_id')
        value = request.form.get('value')
        target = request.form.get('target')
        period = request.form.get('period')
        notes = request.form.get('notes', '')
        
        if not kpi_id or not value or not target:
            flash('Please fill in all required fields.', 'error')
            return redirect('/kpi-form')
        
        try:
            value = float(value)
            target = float(target)
            kpi_id = int(kpi_id)
        except (ValueError, TypeError):
            flash('Invalid value format. Please enter valid numbers.', 'error')
            return redirect('/kpi-form')
        
        kpi = KPI.query.get(kpi_id)
        if not kpi:
            flash('Selected KPI does not exist.', 'error')
            return redirect('/kpi-form')
        
        kpi_data = KPIData(
            kpi_id=kpi_id,
            value=value,
            target=target,
            period=period,
            notes=notes,
            created_by='admin',
            timestamp=datetime.utcnow()
        )
        
        db.session.add(kpi_data)
        db.session.commit()
        
        flash(f'KPI data for "{kpi.name}" added successfully!', 'success')
        return redirect('/')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding KPI data: {str(e)}', 'error')
        return redirect('/kpi-form')

@app.route('/api/dashboard-data')
def dashboard_data():
    """API endpoint for dashboard data"""
    try:
        total_departments = Department.query.count()
        total_kpis = KPI.query.count()
        total_data_points = KPIData.query.count()
        
        recent_data = db.session.query(
            KPIData, KPI, Department
        ).join(KPI).join(Department).order_by(
            KPIData.timestamp.desc()
        ).limit(20).all()
        
        recent_kpis = []
        for kpi_data, kpi, dept in recent_data:
            recent_kpis.append({
                'id': kpi_data.id,
                'kpi_name': kpi.name,
                'department': dept.name,
                'value': kpi_data.value,
                'target': kpi_data.target,
                'timestamp': kpi_data.timestamp.isoformat(),
                'performance': 'Above Target' if kpi_data.value >= kpi_data.target else 'Below Target'
            })
        
        return jsonify({
            'success': True,
            'summary': {
                'total_departments': total_departments,
                'total_kpis': total_kpis,
                'total_data_points': total_data_points
            },
            'recent_kpis': recent_kpis
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/departments/<int:dept_id>/kpis')
def get_department_kpis(dept_id):
    """Get KPIs for a specific department (for AJAX filtering)"""
    try:
        kpis = KPI.query.filter_by(department_id=dept_id).all()
        kpi_list = [{'id': kpi.id, 'name': kpi.name} for kpi in kpis]
        return jsonify({'success': True, 'kpis': kpi_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors"""
    return render_template('500.html'), 500

@app.route('/export/powerbi-data')
def export_powerbi_data():
    """Export data in format suitable for Power BI"""
    try:
        # Get comprehensive KPI data with joins
        data = db.session.query(
            KPIData.id.label('data_id'),
            KPIData.value,
            KPIData.target,
            KPIData.period,
            KPIData.timestamp,
            KPIData.notes,
            KPIData.created_by,
            KPI.id.label('kpi_id'),
            KPI.name.label('kpi_name'),
            KPI.description.label('kpi_description'),
            KPI.unit.label('kpi_unit'),
            KPI.target_type.label('kpi_target_type'),
            Department.id.label('department_id'),
            Department.name.label('department_name'),
            Department.description.label('department_description')
        ).join(KPI).join(Department).all()
        
        # Convert to list of dictionaries
        result = []
        for row in data:
            # Calculate performance metrics
            achievement_rate = (row.value / row.target * 100) if row.target > 0 else 0
            variance = row.value - row.target
            status = 'Above Target' if row.value >= row.target else 'Below Target'
            
            # Determine performance category
            if achievement_rate >= 100:
                performance_category = 'Excellent'
            elif achievement_rate >= 90:
                performance_category = 'Good'
            elif achievement_rate >= 75:
                performance_category = 'Fair'
            else:
                performance_category = 'Poor'
            
            result.append({
                'Data_ID': row.data_id,
                'KPI_ID': row.kpi_id,
                'KPI_Name': row.kpi_name,
                'KPI_Description': row.kpi_description,
                'KPI_Unit': row.kpi_unit,
                'KPI_Target_Type': row.kpi_target_type,
                'Department_ID': row.department_id,
                'Department_Name': row.department_name,
                'Department_Description': row.department_description,
                'Actual_Value': row.value,
                'Target_Value': row.target,
                'Variance': variance,
                'Achievement_Rate': round(achievement_rate, 2),
                'Status': status,
                'Performance_Category': performance_category,
                'Period': row.period,
                'Date': row.timestamp.strftime('%Y-%m-%d'),
                'DateTime': row.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'Year': row.timestamp.year,
                'Month': row.timestamp.month,
                'Month_Name': row.timestamp.strftime('%B'),
                'Quarter': f"Q{((row.timestamp.month-1)//3)+1}",
                'Week': row.timestamp.isocalendar()[1],
                'Day': row.timestamp.day,
                'Weekday': row.timestamp.strftime('%A'),
                'Notes': row.notes or '',
                'Created_By': row.created_by
            })
        
        return jsonify({
            'success': True,
            'data': result,
            'record_count': len(result)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/export/csv')
def export_csv():
    """Export data as CSV for Power BI import"""
    import csv
    from io import StringIO
    from flask import make_response
    
    try:
        # Get comprehensive KPI data with explicit joins
        data = db.session.query(
            KPIData.id.label('data_id'),
            KPIData.value,
            KPIData.target,
            KPIData.period,
            KPIData.timestamp,
            KPIData.notes,
            KPIData.created_by,
            KPI.id.label('kpi_id'),
            KPI.name.label('kpi_name'),
            KPI.description.label('kpi_description'),
            KPI.unit.label('kpi_unit'),
            KPI.target_type.label('kpi_target_type'),
            Department.id.label('department_id'),
            Department.name.label('department_name'),
            Department.description.label('department_description')
        ).select_from(KPIData)\
         .join(KPI, KPIData.kpi_id == KPI.id)\
         .join(Department, KPI.department_id == Department.id)\
         .all()
        
        # Create CSV content
        output = StringIO()
        fieldnames = [
            'Data_ID', 'KPI_ID', 'KPI_Name', 'KPI_Description', 'KPI_Unit', 'KPI_Target_Type',
            'Department_ID', 'Department_Name', 'Department_Description',
            'Actual_Value', 'Target_Value', 'Variance', 'Achievement_Rate', 'Status', 'Performance_Category',
            'Period', 'Date', 'DateTime', 'Year', 'Month', 'Month_Name', 'Quarter', 'Week', 'Day', 'Weekday',
            'Notes', 'Created_By'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in data:
            # Calculate performance metrics
            achievement_rate = (row.value / row.target * 100) if row.target > 0 else 0
            variance = row.value - row.target
            status = 'Above Target' if row.value >= row.target else 'Below Target'
            
            # Determine performance category
            if achievement_rate >= 100:
                performance_category = 'Excellent'
            elif achievement_rate >= 90:
                performance_category = 'Good'
            elif achievement_rate >= 75:
                performance_category = 'Fair'
            else:
                performance_category = 'Poor'
            
            writer.writerow({
                'Data_ID': row.data_id,
                'KPI_ID': row.kpi_id,
                'KPI_Name': row.kpi_name,
                'KPI_Description': row.kpi_description or '',
                'KPI_Unit': row.kpi_unit or '',
                'KPI_Target_Type': row.kpi_target_type or '',
                'Department_ID': row.department_id,
                'Department_Name': row.department_name,
                'Department_Description': row.department_description or '',
                'Actual_Value': row.value,
                'Target_Value': row.target,
                'Variance': variance,
                'Achievement_Rate': round(achievement_rate, 2),
                'Status': status,
                'Performance_Category': performance_category,
                'Period': row.period,
                'Date': row.timestamp.strftime('%Y-%m-%d'),
                'DateTime': row.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'Year': row.timestamp.year,
                'Month': row.timestamp.month,
                'Month_Name': row.timestamp.strftime('%B'),
                'Quarter': f"Q{((row.timestamp.month-1)//3)+1}",
                'Week': row.timestamp.isocalendar()[1],
                'Day': row.timestamp.day,
                'Weekday': row.timestamp.strftime('%A'),
                'Notes': row.notes or '',
                'Created_By': row.created_by or ''
            })
        
        # Return as downloadable file
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=kpi_data.csv'
        return response
        
    except Exception as e:
        return f"Error exporting CSV: {str(e)}", 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        from database.init_db import init_sample_data
        init_sample_data(db)
    
    app.run(debug=True, host='0.0.0.0', port=5000)