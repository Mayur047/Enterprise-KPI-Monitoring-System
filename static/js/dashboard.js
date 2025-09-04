// Enterprise KPI Monitoring System - Dashboard JavaScript

class KPIDashboard {
    constructor() {
        this.init();
    }

    init() {
        this.loadDashboardData();
        this.setupEventListeners();
        this.setupAutoRefresh();
    }

    setupEventListeners() {
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadDashboardData();
            });
        }

        const deptFilter = document.getElementById('department-filter');
        if (deptFilter) {
            deptFilter.addEventListener('change', () => {
                this.filterKPIsByDepartment(deptFilter.value);
            });
        }

        const kpiForm = document.getElementById('kpi-form');
        if (kpiForm) {
            kpiForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitKPIData();
            });
        }
    }

    setupAutoRefresh() {
        setInterval(() => {
            this.loadDashboardData();
        }, 300000);
    }

    async loadDashboardData() {
        try {
            this.showLoading();
            
            const response = await fetch('/api/dashboard-data');
            const data = await response.json();

            if (data.success) {
                this.updateSummaryStats(data.summary);
                this.updateRecentKPIs(data.recent_kpis);
                this.hideLoading();
            } else {
                this.showError('Failed to load dashboard data: ' + data.error);
            }
        } catch (error) {
            this.showError('Error loading dashboard data: ' + error.message);
        }
    }

    updateSummaryStats(summary) {
        const elements = {
            'total-departments': summary.total_departments,
            'total-kpis': summary.total_kpis,
            'total-data-points': summary.total_data_points
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value.toLocaleString();
            }
        });
    }

    updateRecentKPIs(recentKPIs) {
        const tbody = document.getElementById('recent-kpis-tbody');
        if (!tbody) return;

        tbody.innerHTML = '';

        recentKPIs.forEach(kpi => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${kpi.kpi_name}</td>
                <td>${kpi.department}</td>
                <td>${kpi.value}</td>
                <td>${kpi.target || 'N/A'}</td>
                <td>
                    <span class="performance-badge ${this.getPerformanceBadgeClass(kpi.performance)}">
                        ${kpi.performance}
                    </span>
                </td>
                <td>${this.formatDateTime(kpi.timestamp)}</td>
            `;
            tbody.appendChild(row);
        });
    }

    getPerformanceBadgeClass(performance) {
        switch (performance) {
            case 'Above Target':
                return 'performance-above';
            case 'Below Target':
                return 'performance-below';
            case 'On Target':
                return 'performance-target';
            default:
                return 'performance-target';
        }
    }

    formatDateTime(isoString) {
        const date = new Date(isoString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }

    async filterKPIsByDepartment(departmentId) {
        try {
            let url = '/api/kpi/';
            if (departmentId && departmentId !== 'all') {
                url += `?department_id=${departmentId}`;
            }

            const response = await fetch(url);
            const data = await response.json();

            if (data.success) {
                this.updateKPIList(data.data);
            } else {
                this.showError('Failed to filter KPIs: ' + data.error);
            }
        } catch (error) {
            this.showError('Error filtering KPIs: ' + error.message);
        }
    }

    updateKPIList(kpis) {
        const container = document.getElementById('kpi-list');
        if (!container) return;

        container.innerHTML = '';

        if (kpis.length === 0) {
            container.innerHTML = '<div class="empty-state">No KPIs found for the selected department.</div>';
            return;
        }

        kpis.forEach(kpi => {
            const kpiCard = document.createElement('div');
            kpiCard.className = 'card';
            kpiCard.innerHTML = `
                <div class="card-header">
            <h2 class="card-title"><i class="fas fa-plus-circle"></i> Add KPI Data</h2>
        </div>
        <div class="card-body">
            <form id="kpi-form">
                <div class="form-group">
                    <label for="department" class="form-label">Department</label>
                    <select id="department" name="department" class="form-control" onchange="loadKPIsForDepartment(this.value)">
                        <option value="">Select Department</option>
                        {% for dept in departments %}
                        <option value="{{ dept.id }}">{{ dept.name }}</option>
                        {% endfor %}
                    </select>
                </div>

                <div class="form-group">
                    <label for="kpi_id" class="form-label">KPI</label>
                    <select id="kpi_id" name="kpi_id" class="form-control" required>
                        <option value="">Select KPI</option>
                        {% for kpi in kpis %}
                        <option value="{{ kpi.id }}" data-department="{{ kpi.department_id }}" data-unit="{{ kpi.unit }}">
                            {{ kpi.name }} ({{ kpi.unit or 'No Unit' }})
                        </option>
                        {% endfor %}
                    </select>
                </div>

                <div class="form-group">
                    <label for="value" class="form-label">Value</label>
                    <input type="number" id="value" name="value" class="form-control" step="0.01" required>
                    <small class="form-text">Current KPI value</small>
                </div>

                <div class="form-group">
                    <label for="target" class="form-label">Target (Optional)</label>
                    <input type="number" id="target" name="target" class="form-control" step="0.01">
                    <small class="form-text">Target value for this KPI</small>
                </div>

                <div class="form-group">
                    <label for="period" class="form-label">Period</label>
                    <select id="period" name="period" class="form-control">
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                        <option value="quarterly">Quarterly</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="notes" class="form-label">Notes (Optional)</label>
                    <textarea id="notes" name="notes" class="form-control" rows="3" placeholder="Any additional notes or comments..."></textarea>
                </div>

                <div class="form-group">
                    <label for="created_by" class="form-label">Created By</label>
                    <input type="text" id="created_by" name="created_by" class="form-control" placeholder="Your name or ID">
                </div>

                <div class="form-actions">
                    <button type="submit" class="btn btn-success">
                        <i class="fas fa-save"></i> Submit KPI Data
                    </button>
                    <button type="reset" class="btn btn-secondary" style="margin-left: 1rem;">
                        <i class="fas fa-undo"></i> Reset Form
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- Quick Stats -->
    <div class="card" style="margin-top: 2rem;">
        <div class="card-header">
            <h3 class="card-title"><i class="fas fa-info-circle"></i> API Integration Examples</h3>
        </div>
        <div class="card-body">
            <h4>REST API Endpoints:</h4>
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 4px; margin: 1rem 0;">
                <strong>Add KPI Data:</strong><br>
                <code>POST /api/kpi/&lt;kpi_id&gt;/data</code><br><br>
                
                <strong>Bulk Add KPI Data:</strong><br>
                <code>POST /api/kpi/data/bulk</code><br><br>
                
                <strong>Get KPI Data:</strong><br>
                <code>GET /api/kpi/&lt;kpi_id&gt;/data</code><br><br>
                
                <strong>Get All KPIs:</strong><br>
                <code>GET /api/kpi/</code>
            </div>

            <h4>Sample API Request (JSON):</h4>
            <pre style="background: #2c3e50; color: white; padding: 1rem; border-radius: 4px; overflow-x: auto;"><code>{
  "value": 95.5,
  "target": 90.0,
  "period": "daily",
  "notes": "Performance exceeded target",
  "created_by": "api_user"
}</code></pre>

            <h4>Power BI Integration:</h4>
            <p>This system automatically syncs data with Power BI datasets for real-time dashboard visualization. Configure your Power BI credentials in the environment variables.</p>
        </div>
    </div>
</div>

<script>
function loadKPIsForDepartment(departmentId) {
    const kpiSelect = document.getElementById('kpi_id');
    const options = kpiSelect.querySelectorAll('option');
    
    options.forEach(option => {
        if (option.value === '') {
            option.style.display = 'block';
            return;
        }
        
        if (!departmentId || option.dataset.department === departmentId) {
            option.style.display = 'block';
        } else {
            option.style.display = 'none';
        }
    });
    
    kpiSelect.value = '';
}
</script>
{% endblock %}
