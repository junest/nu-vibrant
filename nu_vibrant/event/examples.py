# nu_vibrant/class_session/events.py
from nu_vibrant.event.registry import event_types
from nu_vibrant.event.services import record_event

# Register event types for this module
event_types.register(
    module='class_session',
    event_type='booking_created',
    name='Booking Created',
    description='A new class booking was created'
)

event_types.register(
    module='class_session',
    event_type='booking_verified',
    name='Booking Verified',
    description='A class booking was verified'
)

# Function to record a booking event
def record_booking_created(booking):
    record_event(
        module='class_session',
        event_type='booking_created',
        description=f"Booking created for {booking.class_session.name}",
        user=booking.user,
        obj=booking
    )