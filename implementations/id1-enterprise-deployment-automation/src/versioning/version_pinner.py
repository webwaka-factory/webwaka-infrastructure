"""Version pinning for locking component versions."""

import logging
from typing import Optional, Dict, List
from datetime import datetime

from ..models.version import VersionPin


logger = logging.getLogger(__name__)


class VersionPinner:
    """Manages version pins for instances."""
    
    def __init__(self):
        """Initialize the version pinner."""
        self.pins: Dict[str, VersionPin] = {}
        self.instance_pins: Dict[str, List[VersionPin]] = {}
    
    async def pin_version(
        self,
        instance_id: str,
        component_type: str,
        component_name: str,
        pinned_version: str,
        reason: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> VersionPin:
        """Pin a version for an instance.
        
        Args:
            instance_id: Instance ID
            component_type: Component type
            component_name: Component name
            pinned_version: Version to pin
            reason: Reason for pinning
            expires_at: Optional expiration date
            
        Returns:
            Created version pin
        """
        logger.info(f"Pinning {component_type} {component_name} to {pinned_version} for instance {instance_id}")
        
        pin_id = f"pin-{datetime.utcnow().timestamp()}"
        
        pin = VersionPin(
            id=pin_id,
            instance_id=instance_id,
            component_type=component_type,
            component_name=component_name,
            pinned_version=pinned_version,
            reason=reason,
            expires_at=expires_at
        )
        
        self.pins[pin_id] = pin
        
        if instance_id not in self.instance_pins:
            self.instance_pins[instance_id] = []
        
        self.instance_pins[instance_id].append(pin)
        
        logger.info(f"Version pin {pin_id} created successfully")
        return pin
    
    async def unpin_version(self, pin_id: str) -> bool:
        """Remove a version pin.
        
        Args:
            pin_id: Pin ID
            
        Returns:
            True if unpinned, False if not found
        """
        logger.info(f"Unpinning version {pin_id}")
        
        pin = self.pins.get(pin_id)
        if not pin:
            logger.warning(f"Pin {pin_id} not found")
            return False
        
        del self.pins[pin_id]
        
        if pin.instance_id in self.instance_pins:
            self.instance_pins[pin.instance_id] = [
                p for p in self.instance_pins[pin.instance_id] if p.id != pin_id
            ]
        
        logger.info(f"Version pin {pin_id} removed successfully")
        return True
    
    async def get_pinned_version(
        self,
        instance_id: str,
        component_type: str,
        component_name: str
    ) -> Optional[str]:
        """Get pinned version for a component.
        
        Args:
            instance_id: Instance ID
            component_type: Component type
            component_name: Component name
            
        Returns:
            Pinned version or None
        """
        pins = self.instance_pins.get(instance_id, [])
        
        for pin in pins:
            if (pin.component_type == component_type and 
                pin.component_name == component_name):
                
                # Check if pin has expired
                if pin.expires_at and pin.expires_at < datetime.utcnow():
                    logger.info(f"Pin {pin.id} has expired")
                    await self.unpin_version(pin.id)
                    continue
                
                return pin.pinned_version
        
        return None
    
    async def get_instance_pins(self, instance_id: str) -> List[VersionPin]:
        """Get all pins for an instance.
        
        Args:
            instance_id: Instance ID
            
        Returns:
            List of version pins
        """
        pins = self.instance_pins.get(instance_id, [])
        
        # Remove expired pins
        active_pins = []
        for pin in pins:
            if pin.expires_at and pin.expires_at < datetime.utcnow():
                await self.unpin_version(pin.id)
            else:
                active_pins.append(pin)
        
        return active_pins
    
    def get_pin(self, pin_id: str) -> Optional[VersionPin]:
        """Get pin by ID.
        
        Args:
            pin_id: Pin ID
            
        Returns:
            Pin or None if not found
        """
        return self.pins.get(pin_id)
    
    def list_pins(self) -> List[VersionPin]:
        """List all pins.
        
        Returns:
            List of pins
        """
        return list(self.pins.values())
