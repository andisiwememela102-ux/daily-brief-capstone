"""Forms for registering newsroom users."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegistrationForm(UserCreationForm):
    """Create an account and let the user choose a newsroom role."""

    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'role')

    def save(self, commit=True):
        """Save the selected email address and newsroom role with the user."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user
