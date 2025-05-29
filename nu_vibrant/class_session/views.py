import datetime

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import ClassSession, ClassBooking
from .forms import ClassBookingForm


## Django class-based view ListView
# showing ClassSession scheduled class sessions for the current week
class ClassSessionListView(ListView):
    model = ClassSession
    template_name = "class_session/class_session_list.html"
    context_object_name = "class_sessions"

    def get_queryset(self):
        #get this current week
        week = datetime.date.today().isocalendar()[1]

        qs = ClassSession.objects.scheduled().for_week(
            week=week).order_by("start_date",)
        return qs


## Django class-based view ClassBookingCreateView 
# showing details about selected ClassSession for ClassBooking form creation
class ClassBookingCreateView(LoginRequiredMixin, CreateView):
    model = ClassBooking
    form_class = ClassBookingForm
    template_name = "class_session/class_booking_form.html"
    success_url = reverse_lazy('class_session:bookings')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_session'] = get_object_or_404(ClassSession, pk=self.kwargs['pk'])
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.class_session = get_object_or_404(ClassSession, pk=self.kwargs['pk'])
        return super().form_valid(form)


class ClassBookingListView(LoginRequiredMixin, ListView):
    model = ClassBooking
    template_name = "class_session/class_booking_list.html"
    context_object_name = "bookings"
    
    def get_queryset(self):
        return ClassBooking.objects.filter(user=self.request.user).order_by('-created')
