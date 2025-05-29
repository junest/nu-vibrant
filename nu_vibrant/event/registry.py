class EventTypeRegistry:
    """
    Registry for event types from different modules.
    Similar to Django's admin site registry.
    """
    def __init__(self):
        self._registry = {}
    
    def register(self, module, event_type, name=None, description=None):
        """
        Register an event type.
        
        Args:
            module: Module name (e.g., 'class_session')
            event_type: Event type code (e.g., 'booking_created')
            name: Human-readable name (defaults to event_type if None)
            description: Optional description
        """
        if name is None:
            name = event_type.replace('_', ' ').title()
            
        key = f"{module}.{event_type}"
        self._registry[key] = {
            'module': module,
            'event_type': event_type,
            'name': name,
            'description': description or ''
        }
    
    def get_event_types(self):
        """
        Get all registered event types.
        
        Returns:
            dict: Dictionary of registered event types
        """
        return self._registry
    
    def get_event_type(self, module, event_type):
        """
        Get a specific event type.
        
        Args:
            module: Module name
            event_type: Event type code
            
        Returns:
            dict: Event type information or None if not found
        """
        key = f"{module}.{event_type}"
        return self._registry.get(key)
    
    def is_registered(self, module, event_type):
        """
        Check if an event type is registered.
        
        Args:
            module: Module name
            event_type: Event type code
            
        Returns:
            bool: True if registered, False otherwise
        """
        key = f"{module}.{event_type}"
        return key in self._registry


# Create a singleton instance
event_types = EventTypeRegistry()