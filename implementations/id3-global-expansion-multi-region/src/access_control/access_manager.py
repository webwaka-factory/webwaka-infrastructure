"""Cross-border access management."""

import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta

from ..models.access_control import (
    AccessRequest,
    AccessGrant,
    AccessRequestStatus
)


logger = logging.getLogger(__name__)


class AccessManager:
    """Manages cross-border access requests and grants."""
    
    def __init__(self):
        """Initialize the access manager."""
        self.requests: Dict[str, AccessRequest] = {}
        self.grants: Dict[str, AccessGrant] = {}
        self.request_counter = 0
        self.grant_counter = 0
    
    async def create_access_request(
        self,
        requester_id: str,
        data_id: str,
        source_region: str,
        target_region: str,
        access_type: str,
        reason: str,
        expires_at: Optional[datetime] = None
    ) -> AccessRequest:
        """Create an access request.
        
        Args:
            requester_id: User ID requesting access
            data_id: Data ID
            source_region: Source region
            target_region: Target region
            access_type: Type of access
            reason: Business reason
            expires_at: Optional expiration time
            
        Returns:
            Created access request
        """
        logger.info(f"Creating access request for {requester_id} to {data_id}")
        
        self.request_counter += 1
        request_id = f"access-req-{self.request_counter:03d}"
        
        request = AccessRequest(
            id=request_id,
            requester_id=requester_id,
            data_id=data_id,
            source_region=source_region,
            target_region=target_region,
            access_type=access_type,
            reason=reason,
            expires_at=expires_at or (datetime.utcnow() + timedelta(days=7))
        )
        
        self.requests[request_id] = request
        logger.info(f"Access request {request_id} created successfully")
        
        return request
    
    def get_access_request(self, request_id: str) -> Optional[AccessRequest]:
        """Get access request by ID.
        
        Args:
            request_id: Request ID
            
        Returns:
            Access request or None if not found
        """
        return self.requests.get(request_id)
    
    def list_access_requests(
        self,
        status: Optional[AccessRequestStatus] = None
    ) -> List[AccessRequest]:
        """List access requests.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of access requests
        """
        requests = list(self.requests.values())
        if status:
            requests = [r for r in requests if r.status == status]
        return requests
    
    async def approve_access_request(
        self,
        request_id: str,
        approver_id: str
    ) -> Optional[AccessGrant]:
        """Approve an access request.
        
        Args:
            request_id: Request ID
            approver_id: Approver user ID
            
        Returns:
            Created access grant or None if request not found
        """
        logger.info(f"Approving access request {request_id}")
        
        request = self.requests.get(request_id)
        if not request:
            logger.warning(f"Access request {request_id} not found")
            return None
        
        # Update request status
        request.status = AccessRequestStatus.APPROVED
        request.approved_by = approver_id
        request.approved_at = datetime.utcnow()
        self.requests[request_id] = request
        
        # Create access grant
        self.grant_counter += 1
        grant_id = f"grant-{self.grant_counter:03d}"
        
        grant = AccessGrant(
            id=grant_id,
            request_id=request_id,
            user_id=request.requester_id,
            data_id=request.data_id,
            source_region=request.source_region,
            target_region=request.target_region,
            access_type=request.access_type,
            expires_at=request.expires_at
        )
        
        self.grants[grant_id] = grant
        logger.info(f"Access grant {grant_id} created for request {request_id}")
        
        return grant
    
    async def reject_access_request(
        self,
        request_id: str,
        rejection_reason: str
    ) -> Optional[AccessRequest]:
        """Reject an access request.
        
        Args:
            request_id: Request ID
            rejection_reason: Reason for rejection
            
        Returns:
            Updated access request or None if not found
        """
        logger.info(f"Rejecting access request {request_id}")
        
        request = self.requests.get(request_id)
        if not request:
            logger.warning(f"Access request {request_id} not found")
            return None
        
        request.status = AccessRequestStatus.REJECTED
        request.rejection_reason = rejection_reason
        self.requests[request_id] = request
        
        logger.info(f"Access request {request_id} rejected")
        return request
    
    def get_access_grant(self, grant_id: str) -> Optional[AccessGrant]:
        """Get access grant by ID.
        
        Args:
            grant_id: Grant ID
            
        Returns:
            Access grant or None if not found
        """
        return self.grants.get(grant_id)
    
    def list_access_grants(self, user_id: Optional[str] = None) -> List[AccessGrant]:
        """List access grants.
        
        Args:
            user_id: Optional user ID filter
            
        Returns:
            List of access grants
        """
        grants = list(self.grants.values())
        if user_id:
            grants = [g for g in grants if g.user_id == user_id and g.revoked_at is None]
        return grants
    
    async def revoke_access_grant(
        self,
        grant_id: str,
        revoked_by: str
    ) -> Optional[AccessGrant]:
        """Revoke an access grant.
        
        Args:
            grant_id: Grant ID
            revoked_by: User ID revoking access
            
        Returns:
            Updated access grant or None if not found
        """
        logger.info(f"Revoking access grant {grant_id}")
        
        grant = self.grants.get(grant_id)
        if not grant:
            logger.warning(f"Access grant {grant_id} not found")
            return None
        
        grant.revoked_at = datetime.utcnow()
        grant.revoked_by = revoked_by
        self.grants[grant_id] = grant
        
        logger.info(f"Access grant {grant_id} revoked")
        return grant
