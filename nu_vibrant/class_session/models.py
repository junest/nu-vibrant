from model_utils.models import TimeStampedModel
from model_utils import Choices, FieldTracker
from django.db import models
from django.core.exceptions import ValidationError


## Custom QuerySet for ClassSession
class ClassSessionQuerySet(models.QuerySet):

    # to filter class sessions for the current week
    def for_week(self, week):
        return self.filter(start_date__week=week)

    # to filter only scheduled class sessions
    def scheduled(self):
        return self.filter(status='scheduled')


class Instructor(TimeStampedModel):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ClassSession(TimeStampedModel):
    STATUS = Choices(
        'scheduled', 'ongoing', 'completed', 'cancelled')

    name = models.CharField(max_length=25)

    instructor = models.ForeignKey(
        "Instructor",
        on_delete=models.CASCADE,
        related_name="class_sessions")

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='scheduled')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    description = models.CharField(max_length=80, blank=True)

    capacity = models.IntegerField(default=0)

    properties = models.JSONField()

    # apply ClassSessionQuerySet custom QuerySet
    objects = ClassSessionQuerySet.as_manager()


    def __str__(self):
        return self.name + " - " + self.status + " by " + self.instructor.first_name

    # validate end_date must be later than start_date
    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError("End date must be later than start date")

    def get_duration(self):
        return (
            self.end_date - self.start_date
        ).total_seconds() / 3600

    @property
    def reserved_capacity(self):
        return self.capacity - self.class_bookings.filter(
            status='verified').count()


class ClassBooking(TimeStampedModel):

    BOOKING_EVENT = 'class_booking_event'
    CONFIRMED_BOOKING_EVENT = 'confirmed_class_booking_event'

    STATUS = Choices(
        'unverified', 'verified', 'cancelled')
    
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="class_bookings")
    
    class_session = models.ForeignKey(
        "ClassSession",
        on_delete=models.CASCADE,
        related_name="class_bookings")

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='unverified')
        
    # Track changes to fields
    tracker = FieldTracker(fields=['status'])

    def __str__(self):
        return self.user.name + " - " + self.class_session.name
    
    def clean(self):
        # Validate number of verified class booking for class_session is not
        # at full capacity
        if self.class_session.class_bookings.filter(
                status='verified').count() >= self.class_session.capacity:
            raise ValidationError(
                "Class session is at full capacity")

        # Validate only books scheduled class_session
        if self.class_session.status != 'scheduled':
            raise ValidationError(
                "Class session is not scheduled or no longer open for booking")

        # Validate user subscription is active
        user_subscription = self.user.subscriptions.filter(status='active')
        if not user_subscription.exists():
            raise ValidationError(
                "User must have an active subscription to book a class")

        self.validate_plan_charges()

    def _get_plan_charge(self):
        from nu_vibrant.subscription.models import PlanCharge
        # Validate user plan charges for ClassBooking.CONFIRMED_BOOKING_EVENT threshold are still valid
        event_subscription = self.user.subscriptions.active().filter_event(
            ClassBooking.CONFIRMED_BOOKING_EVENT)
        plan_charge = PlanCharge.objects.filter(
            plan__subscriptions__in=event_subscription).first()
        return plan_charge

    def validate_plan_charges(self):
        plan_charge = self._get_plan_charge()

        if not plan_charge:
            raise ValidationError(
                "User plan charges are not found. Please renew subscription")

        is_rate_limiting = plan_charge.is_rate_limiting

        if plan_charge.charge_left <= 0 and is_rate_limiting:
            raise ValidationError(
                "User plan charges are exhausted. Please renew subscription")
