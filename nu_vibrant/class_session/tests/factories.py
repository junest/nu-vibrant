import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from datetime import timedelta

from nu_vibrant.class_session.models import Instructor, ClassSession, ClassBooking
from nu_vibrant.users.tests.factories import UserFactory
from nu_vibrant.subscription.tests.factories import SubscriptionFactory


class InstructorFactory(DjangoModelFactory):
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

    class Meta:
        model = Instructor


class ClassSessionFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Class Session {n}")
    instructor = factory.SubFactory(InstructorFactory)
    status = 'scheduled'
    start_date = factory.LazyFunction(timezone.now)
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(hours=1))
    capacity = 10
    properties = factory.Dict({'level': 'beginner', 'equipment': ['mat']})

    class Meta:
        model = ClassSession


class ClassBookingFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    class_session = factory.SubFactory(ClassSessionFactory)
    status = 'unverified'

    class Meta:
        model = ClassBooking