from django.db import models
from model_utils.models import TimeStampedModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class EventRecord(TimeStampedModel):
    """
    Model to record events from other modules.
    """
    module = models.CharField(max_length=50)
    event_type = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    user = models.ForeignKey(
        "users.User", 
        on_delete=models.CASCADE, 
        related_name="events",
        null=True, 
        blank=True
    )
    
    # Generic relation to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Relation to BillableMetric
    billable_metric = models.ForeignKey(
        "subscription.BillableMetric",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events"
    )
    
    # Relation to Subscription
    subscription = models.ForeignKey(
        "subscription.Subscription",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events"
    )
    
    # Additional data stored as JSON
    data = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.module}.{self.event_type} - {self.created}"