"""
Fuzentry Exporter Module - Data Export & Compliance
"""

from typing import Dict, Any
from ..core import FuzentryClient


class ExporterClient:
    """Data export and compliance"""
    
    def __init__(self, client: FuzentryClient):
        self.client = client
    
    def export_usage(
        self,
        start_date: str,
        end_date: str,
        format: str = "csv"
    ) -> Dict[str, Any]:
        """Export usage data"""
        response = self.client.post('/export/usage', body={
            'startDate': start_date,
            'endDate': end_date,
            'format': format
        })
        return response['data']
    
    def export_vectors(self, folder_id: str, format: str = "jsonl") -> Dict[str, Any]:
        """Export vector memories"""
        response = self.client.post('/export/vectors', body={
            'folderId': folder_id,
            'format': format
        })
        return response['data']
    
    def export_audit_log(
        self,
        start_date: str,
        end_date: str,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export audit logs (GDPR/HIPAA compliance)"""
        response = self.client.post('/export/audit', body={
            'startDate': start_date,
            'endDate': end_date,
            'format': format
        })
        return response['data']
    
    def get_export_status(self, job_id: str) -> Dict[str, Any]:
        """Get export job status"""
        response = self.client.get(f'/export/jobs/{job_id}')
        return response['data']
    
    def request_deletion(self) -> Dict[str, Any]:
        """Request data deletion (GDPR right to be forgotten)"""
        response = self.client.post('/export/delete-request', body={})
        return response['data']
