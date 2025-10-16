from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import (TourSchedule, Reservation,
                    ReservationPayment, Tour, Agency)

class TourScheduleForm(forms.ModelForm):
    class Meta:
        model = TourSchedule
        fields = ["tour", "date", "start_time", "capacity", "opened"]

        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form__input"}),
            "start_time": forms.TimeInput(attrs={"type": "time", "class": "form__input"}),
            "capacity": forms.NumberInput(attrs={"class": "form__input", "min": 1}),
            "tour": forms.Select(attrs={"class": "form__select"}),
            "opened": forms.CheckboxInput(attrs={"class": "form__checkbox"}),
        }

    def clean_date(self):
        selected_date = self.cleaned_data["date"]
        today = date.today()
        if selected_date < today:
            raise ValidationError("La fecha no puede ser menor a la fecha actual.")
        return selected_date
       
class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = "__all__"
        widgets = {
            "tour_name": forms.TextInput(attrs={"class": "form__input"}),
            "base_price": forms.NumberInput(attrs={"class": "form__input", "step": "0.01"}),
            "default_capacity": forms.NumberInput(attrs={"class": "form__input", "min": "1"}),
            "description": forms.Textarea(attrs={"class": "form__input", "rows": 4}),
            "default_start_time": forms.TimeInput(attrs={"class": "form__input", "type": "time"}),
            "active": forms.CheckboxInput(attrs={"class": "form__checkbox"}),
        }

class ReservationForm(forms.ModelForm):
    DOCUMENT_TYPE_CHOICES = [
        ("CC", "Cédula de Ciudadanía"),
        ("CE", "Cédula de Extranjería"),
        ("TI", "Tarjeta de Identidad"),
        ("PA", "Pasaporte"),
    ]

    type_document = forms.ChoiceField(
        choices=DOCUMENT_TYPE_CHOICES,
        label="Tipo de Documento",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    base_price = forms.DecimalField(
        label="Precio Base",
        max_digits=10,
        decimal_places=2,
        required=False,
        disabled=True,  # solo lectura
    )

    schedule = forms.ModelChoiceField(
        queryset=TourSchedule.objects.filter(opened=True),
        label="Programación",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = Reservation
        fields = [
            "schedule",
            "type_document",    
            "costumer_document",
            "customer_name",
            "customer_phone",
            "pax",
            "total_to_pay",
            "expected_agency_payment",
            "expected_customer_payment",
            "agency",
            "status",
        ]
        labels = {
            "schedule": "Programación",
            "costumer_document": "Documento Cliente",
            "customer_name": "Nombre Cliente",
            "customer_phone": "Teléfono Cliente",
            "pax": "Número de Personas",
            "total_to_pay": "Total a Pagar",
            "expected_agency_payment": "Pago Esperado Agencia",
            "expected_customer_payment": "Pago Esperado Cliente",
            "agency": "Agencia",
            "status": "Estado",
        }

    def __init__(self, *args, **kwargs):
        schedule = kwargs.pop("schedule", None)
        updating = kwargs.pop("updating", False)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            schedule = self.instance.schedule

        if schedule:
            self.fields["schedule"].initial = schedule
            self.fields["base_price"].initial = schedule.tour.base_price
            if not updating:
                self.fields["schedule"].disabled = True

        # ⚡ Aquí forzamos que agency sea obligatorio
        self.fields["agency"].required = True  
        self.fields["agency"].empty_label = "Seleccione una agencia"  

        self.fields["status"].initial = "Reservado"
        self.fields["status"].disabled = True

        self.fields["type_document"].required = False
        self.fields["costumer_document"].required = False


class AgencyForm(forms.ModelForm):
    class Meta:
        model = Agency
        fields = ["name", "tax_id", "phone", "email"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "modal__input",
                "placeholder": "Nombre de la agencia"
            }),
            "tax_id": forms.TextInput(attrs={
                "class": "modal__input",
                "placeholder": "NIT de la agencia"
            }),
            "phone": forms.TextInput(attrs={
                "class": "modal__input",
                "placeholder": "Teléfono de contacto"
            }),
            "email": forms.EmailInput(attrs={
                "class": "modal__input",
                "placeholder": "Correo electrónico"
            }),
        }
        labels = {
            "name": "Nombre",
            "tax_id": "NIT",
            "phone": "Teléfono",
            "email": "Email",
        }

class ReservationPaymentForm(forms.ModelForm):
    class Meta:
        model = ReservationPayment
        fields = ["source", "amount", "note"]