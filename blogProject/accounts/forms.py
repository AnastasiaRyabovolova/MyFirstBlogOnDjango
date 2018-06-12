from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from boards.models import City, Country, Profile, Reader, Subject, User


def getSelectsCountry():
    values = []
    all_value = Country.objects.all()
    for value in all_value:
        values.append((value.id, value.country))
    return tuple(values)

def getSelectsCity():
    values = []
    all_value = City.objects.all()
    for value in all_value:
        values.append((value.id, value.country))
    return tuple(values)


class ReaderSignUpForm(UserCreationForm):

    email = forms.CharField(max_length=254,
                            required=True,
                            widget=forms.EmailInput())

    country = forms.ChoiceField(required=True,
                                choices=getSelectsCountry,
                                widget=forms.Select(
                                       attrs={'style': 'height:35px;'}
                                ))

    city = forms.ChoiceField(required=True,
                             choices=getSelectsCity,
                             widget=forms.Select(
                                    attrs={'style': 'height:35px;'}
                             ))

    interests = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'custom-control-input'}),
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'country', 'city', 'interests')

    @transaction.atomic
    def save(self):
        user = super(ReaderSignUpForm, self).save(commit=False)
        user.is_reader = True
        user.save()
        reader = Reader.objects.create(user=user)
        reader.interests.add(*self.cleaned_data.get('interests'))
        return user


# class ReporterSignUpForm(UserCreationForm):
#
#     interests = forms.ModelMultipleChoiceField(
#         queryset=Subject.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         required=True
#     )
#
#     class Meta:
#         model = User
#         fields = ('subject', )


class ReporterSignUpForm(UserCreationForm):

    email = forms.CharField(max_length=254,
                            required=True,
                            widget=forms.EmailInput())

    country = forms.ChoiceField(required=True,
                                choices=getSelectsCountry,
                                widget=forms.Select(
                                       attrs={'style': 'height:35px;'}
                                ))

    city = forms.ChoiceField(required=True,
                             choices=getSelectsCity,
                             widget=forms.Select(
                                    attrs={'style': 'height:35px;'}
                             ))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'country', 'city', )

    @transaction.atomic
    def save(self):
        user = super(ReporterSignUpForm, self).save(commit=False)
        user.is_reporter = True
        user.save()
        return user
