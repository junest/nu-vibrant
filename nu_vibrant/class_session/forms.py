from django import forms
from .models import ClassBooking


class ClassBookingForm(forms.ModelForm):
    class Meta:
        model = ClassBooking
        fields = []  # No fields needed as we set user and class_session in the view
        
    def clean(self):
        cleaned_data = super().clean()
        
        # The validation is handled in the model's clean method
        # We just need to make sure the instance has user and class_session set
        # before the model validation runs
        
        return cleaned_data