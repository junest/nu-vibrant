from django.contrib import admin

# Register your models here.
from .models import (
    Instructor,
    ClassSession,
    ClassBooking
)

class ClassBookingInLine(admin.StackedInline):
    model = ClassBooking
    extra = 3  


class ClassSessionAdmin(admin.ModelAdmin):
    inlines = [ClassBookingInLine]

admin.site.register(Instructor)
admin.site.register(ClassSession, ClassSessionAdmin)
