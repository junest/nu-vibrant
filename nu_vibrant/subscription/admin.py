from django.contrib import admin

# Register your models here.
from .models import (
    BillableMetric,
    Plan
)

admin.site.register(BillableMetric)
admin.site.register(Plan)
