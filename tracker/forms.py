from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator


class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation",
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_username(self):
        """
        Validate that the username is unique and doesn't already exist in the system.
        """
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(
                'Username already exists. Please choose a different one')
        return username

    def clean_password2(self):
        """
        Ensure that both password fields match.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2


class UserLoginForm(forms.Form):
    """
    Form to handle user login, requiring a username and password.
    """
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class PasswordResetForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError("This email is not registered.")
        return email


class SetNewpasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput,
                                   label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput,
                                       label="Confirm New Password")

    def __init__(self, *args, **kwargs):
        self.uidb64 = kwargs.pop('uidb64', None)
        self.token = kwargs.pop('token', None)
        super().__init__(*args, **kwargs)

    def save(self):
        cleaned_data = super.clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise ValidationError("Password don't match.")
        return cleaned_data

    def save(self):
        try:
            uid = urlsafe_base64_decode(self.uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, User.DoesNotExist):
            raise ValidationError("Invalid user.")

        # Verify token
        if not default_token_generator.check_token(user, self.token):
            raise ValidationError("Invalid or expired token.")

        user.set_password(self.cleaned_data['new_password'])
        user.save()
        return user
