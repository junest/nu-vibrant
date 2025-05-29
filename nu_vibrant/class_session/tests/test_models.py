import pytest
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta

from nu_vibrant.class_session.models import ClassSession, ClassBooking
from nu_vibrant.class_session.tests.factories import InstructorFactory, ClassSessionFactory, ClassBookingFactory
from nu_vibrant.users.tests.factories import UserFactory
from nu_vibrant.subscription.tests.factories import SubscriptionFactory, PlanFactory


@pytest.mark.django_db
class TestInstructorModel:
    def test_instructor_str(self):
        """Test the string representation of an Instructor"""
        instructor = InstructorFactory(first_name="John", last_name="Doe")
        assert str(instructor) == "John Doe"


@pytest.mark.django_db
class TestClassSessionModel:
    def test_class_session_str(self):
        """Test the string representation of a ClassSession"""
        instructor = InstructorFactory(first_name="Jane")
        class_session = ClassSessionFactory(
            name="Pilates Basic",
            instructor=instructor,
            status="scheduled"
        )
        assert str(class_session) == "Pilates Basic - scheduled by Jane"

    def test_clean_valid_dates(self):
        """Test that clean method passes with valid dates"""
        now = timezone.now()
        class_session = ClassSessionFactory(
            start_date=now,
            end_date=now + timedelta(hours=1)
        )
        class_session.clean()  # Should not raise exception

    def test_clean_invalid_dates(self):
        """Test that clean method raises ValidationError with invalid dates"""
        now = timezone.now()
        class_session = ClassSessionFactory(
            start_date=now,
            end_date=now - timedelta(hours=1)
        )
        with pytest.raises(ValidationError):
            class_session.clean()
            
    def test_queryset_for_week(self):
        """Test the for_week queryset method"""
        # Create class sessions in different weeks
        now = timezone.now()
        
        # Create a class session for this week
        this_week_session = ClassSessionFactory(start_date=now)
        
        # Create a class session for next week
        next_week = now + timedelta(days=7)
        next_week_session = ClassSessionFactory(start_date=next_week)
        
        # Get the week number for the current date
        current_week = now.isocalendar()[1]
        
        # Query sessions for the current week
        this_week_sessions = ClassSession.objects.for_week(current_week)
        
        # Check that only the current week session is returned
        assert this_week_session in this_week_sessions
        assert next_week_session not in this_week_sessions
        
    def test_queryset_scheduled(self):
        """Test the scheduled queryset method"""
        # Create class sessions with different statuses
        scheduled_session = ClassSessionFactory(status='scheduled')
        ongoing_session = ClassSessionFactory(status='ongoing')
        completed_session = ClassSessionFactory(status='completed')
        cancelled_session = ClassSessionFactory(status='cancelled')
        
        # Query scheduled sessions
        scheduled_sessions = ClassSession.objects.scheduled()
        
        # Check that only scheduled sessions are returned
        assert scheduled_session in scheduled_sessions
        assert ongoing_session not in scheduled_sessions
        assert completed_session not in scheduled_sessions
        assert cancelled_session not in scheduled_sessions


@pytest.mark.django_db
class TestClassBookingModel:
    def test_class_booking_str(self):
        """Test the string representation of a ClassBooking"""
        user = UserFactory(name="testuser")
        class_session = ClassSessionFactory(name="Pilates Basic")
        class_booking = ClassBookingFactory(
            user=user,
            class_session=class_session
        )
        assert str(class_booking) == "testuser - Pilates Basic"

    def test_capacity_validation(self):
        """Test that booking validation fails when class is at capacity"""
        now = timezone.now()
        plan = PlanFactory()
        
        # Create class session with capacity of 2
        class_session = ClassSessionFactory(capacity=2)
        
        # Create two users with active subscriptions
        user1 = UserFactory()
        user2 = UserFactory()
        user3 = UserFactory()
        
        subscription1 = SubscriptionFactory(user=user1, plan=plan)
        subscription2 = SubscriptionFactory(user=user2, plan=plan)
        subscription3 = SubscriptionFactory(user=user3, plan=plan)
        
        # Create two verified bookings
        booking1 = ClassBookingFactory(
            user=user1,
            class_session=class_session,
            status="verified"
        )
        
        booking2 = ClassBookingFactory(
            user=user2,
            class_session=class_session,
            status="verified"
        )
        
        # Try to create a third booking
        booking3 = ClassBooking(
            user=user3,
            class_session=class_session,
            status="verified"
        )
        
        # This should fail validation as capacity is 2
        with pytest.raises(ValidationError):
            booking3.clean()

    def test_class_status_validation(self):
        """Test that booking validation fails when class is not scheduled"""
        user = UserFactory()
        plan = PlanFactory()
        subscription = SubscriptionFactory(user=user, plan=plan)
        
        # Create completed class session
        class_session = ClassSessionFactory(status="completed")
        
        # Try to create a booking
        booking = ClassBooking(
            user=user,
            class_session=class_session,
            status="unverified"
        )
        
        with pytest.raises(ValidationError):
            booking.clean()

    def test_subscription_validation(self):
        """Test that booking validation fails when user has no active subscription"""
        user = UserFactory()
        plan = PlanFactory()
        
        # Create inactive subscription
        subscription = SubscriptionFactory(
            user=user,
            plan=plan,
            status="inactive"
        )
        
        class_session = ClassSessionFactory()
        
        # Try to create a booking
        booking = ClassBooking(
            user=user,
            class_session=class_session,
            status="unverified"
        )
        
        with pytest.raises(ValidationError):
            booking.clean()
            
    def test_booking_event_constants(self):
        """Test that booking event constants are defined correctly"""
        assert hasattr(ClassBooking, 'BOOKING_EVENT')
        assert ClassBooking.BOOKING_EVENT == 'class_booking_event'
        
        assert hasattr(ClassBooking, 'CONFIRMED_BOOKING_EVENT')
        assert ClassBooking.CONFIRMED_BOOKING_EVENT == 'confirmed_class_booking_event'