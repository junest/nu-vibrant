from django.db.models.signals import post_save
from django.dispatch import receiver

from nu_vibrant.event.services import record_event
from .models import ClassBooking


@receiver(post_save, sender=ClassBooking)
def record_class_booking_events(sender, instance, created, **kwargs):
    """
    Record events when a ClassBooking is created or confirmed.
    """
    # Get active subscription for the user
    active_subscription = instance.user.subscriptions.filter(status='active').first()
    
    if created:
        # Record booking creation event
        record_event(
            module='class_session',
            event_type=ClassBooking.BOOKING_EVENT,
            description=f"Booking created for {instance.class_session.name}",
            user=instance.user,
            obj=instance,
            subscription=active_subscription
        )
    elif instance.status == 'verified' and instance.tracker.has_changed('status'):
        # Record booking confirmation event
        record_event(
            module='class_session',
            event_type=ClassBooking.CONFIRMED_BOOKING_EVENT,
            description=f"Booking confirmed for {instance.class_session.name}",
            user=instance.user,
            obj=instance,
            subscription=active_subscription
        )