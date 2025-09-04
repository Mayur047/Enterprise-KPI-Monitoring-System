import requests
import msal
from config import Config
import json
from datetime import datetime

class PowerBIIntegration:
    """Power BI integration for pushing KPI data"""
    
    def __init__(self):
        self.client_id = Config.POWERBI_CLIENT_ID
        self.client_secret = Config.POWERBI_CLIENT_SECRET
        self.tenant_id = Config.POWERBI_TENANT_ID
        self.workspace_id = Config.POWERBI_WORKSPACE_ID
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["https://analysis.windows.net/powerbi/api/.default"]
        self.access_token = None
    
    def get_access_token(self):
        """Get access token for Power BI API"""
        try:
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=self.authority,
                client_credential=self.client_secret
            )
            
            result = app.acquire_token_for_client(scopes=self.scope)
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                return True
            else:
                print(f"Error acquiring token: {result.get('error_description', 'Unknown error')}")
                return False
        
        except Exception as e:
            print(f"Exception in get_access_token: {str(e)}")
            return False
    
    def create_dataset(self, dataset_name, table_schema):
        """Create a dataset in Power BI"""
        if not self.access_token:
            if not self.get_access_token():
                return None
        
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{self.workspace_id}/datasets"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        dataset_definition = {
            "name": dataset_name,
            "tables": [table_schema]
        }
        
        try:
            response = requests.post(url, headers=headers, json=dataset_definition)
            
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Error creating dataset: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            print(f"Exception in create_dataset: {str(e)}")
            return None
    
    def push_data_to_powerbi(self, dataset_id, table_name, data):
        """Push data to Power BI dataset"""
        if not self.access_token:
            if not self.get_access_token():
                return False
        
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{self.workspace_id}/datasets/{dataset_id}/tables/{table_name}/rows"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {"rows": data}
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                return True
            else:
                print(f"Error pushing data: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            print(f"Exception in push_data_to_powerbi: {str(e)}")
            return False
    
    def get_kpi_table_schema(self):
        """Get table schema for KPI data"""
        return {
            "name": "KPIData",
            "columns": [
                {"name": "ID", "dataType": "Int64"},
                {"name": "KPIName", "dataType": "string"},
                {"name": "Department", "dataType": "string"},
                {"name": "Value", "dataType": "Double"},
                {"name": "Target", "dataType": "Double"},
                {"name": "Timestamp", "dataType": "DateTime"},
                {"name": "Period", "dataType": "string"},
                {"name": "PerformanceStatus", "dataType": "string"},
                {"name": "Unit", "dataType": "string"}
            ]
        }
    
    def format_kpi_data_for_powerbi(self, kpi_data_list):
        """Format KPI data for Power BI consumption"""
        formatted_data = []
        
        for kpi_data in kpi_data_list:
            formatted_data.append({
                "ID": kpi_data.id,
                "KPIName": kpi_data.kpi.name if kpi_data.kpi else "Unknown",
                "Department": kpi_data.kpi.department.name if kpi_data.kpi and kpi_data.kpi.department else "Unknown",
                "Value": kpi_data.value,
                "Target": kpi_data.target or 0,
                "Timestamp": kpi_data.timestamp.isoformat() if kpi_data.timestamp else datetime.utcnow().isoformat(),
                "Period": kpi_data.period,
                "PerformanceStatus": kpi_data.get_performance_status(),
                "Unit": kpi_data.kpi.unit if kpi_data.kpi else ""
            })
        
        return formatted_data

def sync_kpi_data_to_powerbi():
    """Sync KPI data to Power BI"""
    from models import KPIData
    
    powerbi = PowerBIIntegration()
    
    recent_kpi_data = KPIData.query.order_by(KPIData.timestamp.desc()).limit(1000).all()
    
    if not recent_kpi_data:
        print("No KPI data to sync")
        return
    
    formatted_data = powerbi.format_kpi_data_for_powerbi(recent_kpi_data)
    
    dataset_name = "Enterprise_KPI_Data"
    table_schema = powerbi.get_kpi_table_schema()
    
    dataset_id = "your-dataset-id-here"
    success = powerbi.push_data_to_powerbi(dataset_id, "KPIData", formatted_data)
    
    if success:
        print(f"Successfully synced {len(formatted_data)} KPI data points to Power BI")
    else:
        print("Failed to sync data to Power BI")