from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Profile


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control'}), label='Пароль')
    password_confirm = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control'}), label='Подтверждение пароля')
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control'}))
    photo = forms.ImageField(required=False, widget=forms.FileInput(
        attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                "Пользователь с такой почтой уже существует.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm:
            if password != password_confirm:
                self.add_error('password_confirm', "Пароли не совпадают.")
            else:
                validate_password(password)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            Profile.objects.create(
                user=user, photo=self.cleaned_data.get('photo'))
        return user


class SettingsForm(forms.ModelForm):
    photo = forms.ImageField(required=False, widget=forms.FileInput(
        attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'profile'):
            self.fields['photo'].initial = self.instance.profile.photo

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError(
                "Пользователь с такой почтой уже существует.")
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile = user.profile
            photo = self.cleaned_data.get('photo')
            if photo:
                profile.photo = photo
            profile.save()
        return user
