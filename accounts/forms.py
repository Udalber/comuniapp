from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()

GENERIC_LOGIN_ERROR = (
    "Correo o contraseña incorrectos. Inténtalo de nuevo."
)


class RegisterForm(forms.Form):
    full_name = forms.CharField(
        label="Nombre completo",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "autocomplete": "name",
                "id": "id_full_name",
            }
        ),
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(
            attrs={
                "class": "input",
                "autocomplete": "email",
                "id": "id_email",
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "input",
                "autocomplete": "new-password",
                "id": "id_password",
            }
        ),
    )

    def clean_full_name(self):
        name = self.cleaned_data["full_name"].strip()
        if not name:
            raise forms.ValidationError("Este campo es obligatorio.")
        return name

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            try:
                validate_password(password)
            except ValidationError as exc:
                raise forms.ValidationError(exc.messages) from exc
        return password

    def save(self):
        full_name = self.cleaned_data["full_name"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]

        parts = full_name.split(None, 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""

        user = User(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(
            attrs={
                "class": "input",
                "autocomplete": "email",
                "id": "id_login_email",
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "input",
                "autocomplete": "current-password",
                "id": "id_login_password",
            }
        ),
    )
    remember_me = forms.BooleanField(
        label="Recordarme",
        required=False,
        widget=forms.CheckboxInput(attrs={"id": "id_remember_me"}),
    )

    error_messages = {
        "invalid_login": GENERIC_LOGIN_ERROR,
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            self.user_cache = authenticate(
                self.request,
                email=email.strip().lower(),
                password=password,
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                )
        return cleaned_data

    def get_user(self):
        return self.user_cache


class ProfileForm(forms.Form):
    first_name = forms.CharField(
        label="Nombre",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "autocomplete": "given-name",
            }
        ),
    )
    last_name = forms.CharField(
        label="Apellido",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "autocomplete": "family-name",
            }
        ),
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(
            attrs={
                "class": "input",
                "autocomplete": "email",
            }
        ),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_first_name(self):
        value = self.cleaned_data["first_name"].strip()
        if not value:
            raise forms.ValidationError("Este campo es obligatorio.")
        return value

    def clean_last_name(self):
        value = self.cleaned_data["last_name"].strip()
        if not value:
            raise forms.ValidationError("Este campo es obligatorio.")
        return value

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def save(self):
        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]
        email = self.cleaned_data["email"]
        if email != self.user.email:
            self.user.email = email
            self.user.username = email
        self.user.save()
        return self.user
