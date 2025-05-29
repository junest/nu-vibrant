from django.contrib.contenttypes.models import ContentType
from .models import EventRecord
from .registry import event_types


def record_event(module, event_type, description="", user=None, obj=None, data=None, subscription=None, billable_metric=None):
    """
    Record an event in the system.
    
    Args:
        module: Module name (e.g., 'class_session')
        event_type: Event type code (e.g., 'booking_created')
        description: Optional description of the event
        user: Optional user associated with the event
        obj: Optional related object (any model instance)
        data: Optional additional data as dictionary
        subscription: Optional subscription associated with the event
        billable_metric: Optional billable metric associated with the event
    
    Returns:
        EventRecord: The created event record
    """
    if not event_types.is_registered(module, event_type):
        raise ValueError(f"Event type {module}.{event_type} is not registered")
    
    if data is None:
        data = {}
        
    event = EventRecord(
        module=module,
        event_type=event_type,
        description=description,
        user=user,
        data=data,
        subscription=subscription,
        billable_metric=billable_metric
    )
    
    if obj is not None:
        content_type = ContentType.objects.get_for_model(obj)
        event.content_type = content_type
        event.object_id = obj.pk
        
    # If billable_metric is not provided but event_type matches a BillableMetric identifier, try to find it
    if billable_metric is None and subscription is not None:
        from nu_vibrant.subscription.models import BillableMetric
        try:
            event.billable_metric = BillableMetric.objects.get(identifier=event_type)
        except BillableMetric.DoesNotExist:
            pass
        
    event.save()
    return event