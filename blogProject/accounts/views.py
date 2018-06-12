# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import login as auth_login
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, CreateView
from django.forms.formsets import formset_factory
from django.shortcuts import render, redirect, get_object_or_404
from boards.models import City, Profile, User
from .forms import ReporterSignUpForm, ReaderSignUpForm

# Create your views here.


def load_cities(request):
    country_id = request.GET.get('country')
    cities = City.objects.filter(country_id=country_id).order_by('name')
    return render(request, 'includes/city_dropdown_list_options.html', {'cities': cities})


def signup(request):
    return render(request, 'signup.html')


class ReaderSignUpView(CreateView):
    model = User
    form_class = ReaderSignUpForm
    template_name = 'user_signup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'reader'
        return super(ReaderSignUpView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        city = get_object_or_404(City, pk=form.cleaned_data.get('city'))
        Profile.objects.create(
            user=user,
            city=city
        )
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('home')


class ReporterSignUpView(CreateView):
    model = User
    form_class = ReporterSignUpForm
    template_name = 'user_signup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'reporter'
        return super(ReporterSignUpView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        city = get_object_or_404(City, pk=form.cleaned_data.get('city'))
        Profile.objects.create(
            user=user,
            city=city
        )
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('home')


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email', )
    template_name = 'my_account.html'
    success_url = reverse_lazy('my_account')

    def get_object(self):
        return self.request.user
