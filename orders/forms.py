import re

from django import forms

from .models import Address, Order

PHONE_RE = re.compile(r"^[\d\s+\-()]{7,20}$")
POSTAL_RE = re.compile(r"^\d{4,10}$")


class AddressForm(forms.Form):
    saved_address_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput(),
    )
    line1 = forms.CharField(
        label="Dirección",
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "autocomplete": "street-address",
                "data-checkout-field": "line1",
            }
        ),
    )
    city = forms.CharField(
        label="Ciudad",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "autocomplete": "address-level2",
                "data-checkout-field": "city",
            }
        ),
    )
    department = forms.CharField(
        label="Departamento",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "autocomplete": "address-level1",
                "data-checkout-field": "department",
            }
        ),
    )
    postal_code = forms.CharField(
        label="Código postal",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "autocomplete": "postal-code",
                "inputmode": "numeric",
                "data-checkout-field": "postal_code",
            }
        ),
    )
    phone = forms.CharField(
        label="Teléfono de contacto",
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "autocomplete": "tel",
                "inputmode": "tel",
                "data-checkout-field": "phone",
            }
        ),
    )
    instructions = forms.CharField(
        label="Instrucciones adicionales",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "input checkout-textarea",
                "rows": 3,
                "data-checkout-field": "instructions",
            }
        ),
    )
    save_address = forms.BooleanField(
        label="Guardar esta dirección para futuras compras",
        required=False,
        widget=forms.CheckboxInput(attrs={"data-checkout-field": "save_address"}),
    )

    def __init__(self, user=None, manage=False, *args, **kwargs):
        self.user = user
        self.manage = manage
        super().__init__(*args, **kwargs)
        for name in ("line1", "city", "department", "postal_code", "phone"):
            self.fields[name].required = True
        if manage:
            del self.fields["save_address"]
            del self.fields["saved_address_id"]

    def clean_line1(self):
        value = self.cleaned_data["line1"].strip()
        if not value:
            raise forms.ValidationError("Este campo es obligatorio.")
        return value

    def clean_city(self):
        value = self.cleaned_data["city"].strip()
        if not value:
            raise forms.ValidationError("Este campo es obligatorio.")
        return value

    def clean_department(self):
        value = self.cleaned_data["department"].strip()
        if not value:
            raise forms.ValidationError("Este campo es obligatorio.")
        return value

    def clean_postal_code(self):
        value = self.cleaned_data["postal_code"].strip()
        if not value:
            raise forms.ValidationError("Este campo es obligatorio.")
        if not POSTAL_RE.match(value):
            raise forms.ValidationError("Introduce un código postal válido (4–10 dígitos).")
        return value

    def clean_phone(self):
        value = self.cleaned_data["phone"].strip()
        if not value:
            raise forms.ValidationError("Este campo es obligatorio.")
        if not PHONE_RE.match(value):
            raise forms.ValidationError("Introduce un teléfono válido.")
        return value

    def clean_instructions(self):
        return self.cleaned_data.get("instructions", "").strip()

    def clean(self):
        cleaned = super().clean()
        if self.manage:
            return cleaned
        saved_id = cleaned.get("saved_address_id")
        if saved_id and self.user:
            try:
                address = Address.objects.get(pk=saved_id, user=self.user)
            except Address.DoesNotExist:
                raise forms.ValidationError("La dirección seleccionada no es válida.")
            else:
                cleaned["line1"] = address.line1
                cleaned["city"] = address.city
                cleaned["department"] = address.department
                cleaned["postal_code"] = address.postal_code
                cleaned["phone"] = address.phone
                cleaned["instructions"] = address.instructions or ""
                cleaned["save_address"] = False
        return cleaned


PSE_BANKS = [
    ("", "Selecciona tu banco"),
    ("bancolombia", "Bancolombia"),
    ("davivienda", "Davivienda"),
    ("bbva", "BBVA Colombia"),
    ("bogota", "Banco de Bogotá"),
    ("occidente", "Banco de Occidente"),
]


class PaymentForm(forms.Form):
    payment_method = forms.ChoiceField(
        label="Método de pago",
        choices=Order.PaymentMethod.choices,
        widget=forms.RadioSelect(attrs={"data-payment-method": ""}),
    )

    pse_bank = forms.ChoiceField(
        label="Banco",
        choices=PSE_BANKS,
        required=False,
        widget=forms.Select(attrs={"class": "input", "data-payment-field": "pse"}),
    )
    pse_person_type = forms.ChoiceField(
        label="Tipo de persona",
        choices=[("", "Selecciona"), ("natural", "Persona natural"), ("juridica", "Persona jurídica")],
        required=False,
        widget=forms.Select(attrs={"class": "input", "data-payment-field": "pse"}),
    )

    nequi_phone = forms.CharField(
        label="Número Nequi",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "inputmode": "tel",
                "placeholder": "300 123 4567",
                "data-payment-field": "nequi",
            }
        ),
    )

    daviplata_phone = forms.CharField(
        label="Número Daviplata",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "inputmode": "tel",
                "placeholder": "300 123 4567",
                "data-payment-field": "daviplata",
            }
        ),
    )

    card_number = forms.CharField(
        label="Número de tarjeta",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "inputmode": "numeric",
                "placeholder": "1234 5678 9012 3456",
                "autocomplete": "cc-number",
                "data-payment-field": "card",
            }
        ),
    )
    card_expiry = forms.CharField(
        label="Fecha de vencimiento",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "placeholder": "MM/AA",
                "autocomplete": "cc-exp",
                "data-payment-field": "card",
            }
        ),
    )
    card_cvv = forms.CharField(
        label="CVV",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "inputmode": "numeric",
                "placeholder": "123",
                "autocomplete": "cc-csc",
                "data-payment-field": "card",
            }
        ),
    )
    card_name = forms.CharField(
        label="Nombre en la tarjeta",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "autocomplete": "cc-name",
                "data-payment-field": "card",
            }
        ),
    )

    def clean(self):
        cleaned = super().clean()
        method = cleaned.get("payment_method")

        if method == Order.PaymentMethod.PSE:
            if not cleaned.get("pse_bank"):
                self.add_error("pse_bank", "Selecciona tu banco.")
            if not cleaned.get("pse_person_type"):
                self.add_error("pse_person_type", "Selecciona el tipo de persona.")
        elif method == Order.PaymentMethod.NEQUI:
            phone = (cleaned.get("nequi_phone") or "").strip()
            if not phone or not PHONE_RE.match(phone):
                self.add_error("nequi_phone", "Introduce un número Nequi válido.")
        elif method == Order.PaymentMethod.DAVIPLATA:
            phone = (cleaned.get("daviplata_phone") or "").strip()
            if not phone or not PHONE_RE.match(phone):
                self.add_error("daviplata_phone", "Introduce un número Daviplata válido.")
        elif method == Order.PaymentMethod.CARD:
            card_number = (cleaned.get("card_number") or "").replace(" ", "")
            if len(card_number) < 13:
                self.add_error("card_number", "Introduce un número de tarjeta válido.")
            expiry = (cleaned.get("card_expiry") or "").strip()
            if not re.match(r"^\d{2}/\d{2}$", expiry):
                self.add_error("card_expiry", "Usa el formato MM/AA.")
            cvv = (cleaned.get("card_cvv") or "").strip()
            if not re.match(r"^\d{3,4}$", cvv):
                self.add_error("card_cvv", "Introduce un CVV válido.")
            if not (cleaned.get("card_name") or "").strip():
                self.add_error("card_name", "Este campo es obligatorio.")

        return cleaned

    def payment_session_data(self):
        """Solo método de pago — sin datos sensibles en sesión."""
        return {"method": self.cleaned_data["payment_method"]}
