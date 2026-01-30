"""Audit logging for cross-border access."""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from ..models.access_control import AccessAuditLog


logger = logging.getLogger(__name__)


class AuditLogger:
    """Logs and manages audit trails for cross-border access."""
    
    def __init__(self):
        """Initialize the audit logger."""
        self.audit_logs: Dict[str, AccessAuditLog] = {}
        self.log_counter = 0
    
    async def log_access_action(
        self,
        user_id: str,
        action: str,
        data_id: str,
        source_region: str,
        target_region: str,
        status: str,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AccessAuditLog:
        """Log an access action.
        
        Args:
            user_id: User ID
            action: Action performed
            data_id: Data ID
            source_region: Source region
            target_region: Target region
            status: Action status
            details: Optional action details
            ip_address: Optional IP address
            user_agent: Optional user agent
            
        Returns:
            Created audit log entry
        """
        logger.info(f"Logging {action} for {user_id} on {data_id}")
        
        self.log_counter += 1
        log_id = f"audit-{self.log_counter:05d}"
        
        log_entry = AccessAuditLog(
            id=log_id,
            user_id=user_id,
            action=action,
            data_id=data_id,
            source_region=source_region,
            target_region=target_region,
            status=status,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.audit_logs[log_id] = log_entry
        logger.info(f"Audit log {log_id} created successfully")
        
        return log_entry
    
    def get_audit_log(self, log_id: str) -> Optional[AccessAuditLog]:
        """Get audit log by ID.
        
        Args:
            log_id: Log ID
            
        Returns:
            Audit log or None if not found
        """
        return self.audit_logs.get(log_id)
    
    def list_audit_logs(
        self,
        user_id: Optional[str] = None,
        data_id: Optional[str] = None,
        action: Optional[str] = None
    ) -> List[AccessAuditLog]:
        """List audit logs with optional filters.
        
        Args:
            user_id: Optional user ID filter
            data_id: Optional data ID filter
            action: Optional action filter
            
        Returns:
            List of audit logs
        """
        logs = list(self.audit_logs.values())
        
        if user_id:
            logs = [l for l in logs if l.user_id == user_id]
        if data_id:
            logs = [l for l in logs if l.data_id == data_id]
        if action:
            logs = [l for l in logs if l.action == action]
        
        # Sort by timestamp descending
        logs.sort(key=lambda l: l.timestamp, reverse=True)
        return logs
    
    def get_user_audit_trail(self, user_id: str) -> List[AccessAuditLog]:
        """Get complete audit trail for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of audit logs for the user
        """
        return self.list_audit_logs(user_id=user_id)
    
    def get_data_access_audit_trail(self, data_id: str) -> List[AccessAuditLog]:
        """Get complete audit trail for data access.
        
        Args:
            data_id: Data ID
            
        Returns:
            List of audit logs for the data
        """
        return self.list_audit_logs(data_id=data_id)
    
    async def generate_audit_report(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[str] = None
    ) -> Dict:
        """Generate audit report for a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            user_id: Optional user ID filter
            
        Returns:
            Audit report
        """
        logger.info(f"Generating audit report from {start_date} to {end_date}")
        
        logs = self.list_audit_logs(user_id=user_id)
        filtered_logs = [
            l for l in logs
            if start_date <= l.timestamp <= end_date
        ]
        
        # Count actions by type
        action_counts = {}
        for log in filtered_logs:
            action_counts[log.action] = action_counts.get(log.action, 0) + 1
        
        # Count by status
        status_counts = {}
        for log in filtered_logs:
            status_counts[log.status] = status_counts.get(log.status, 0) + 1
        
        report = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_entries": len(filtered_logs),
            "action_counts": action_counts,
            "status_counts": status_counts,
            "entries": filtered_logs
        }
        
        logger.info(f"Audit report generated with {len(filtered_logs)} entries")
        return report
