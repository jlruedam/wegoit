from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import TourSchedule, Reservation, Tour

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
    class Meta:
        model = Reservation
        fields = [
            "schedule",
            "customer_name",
            "pax",
            "net_payment",
            "pending_balance",
            "status",
            "debt",
            "payment_received_on_tour",
            "total_payment",
            "agency",
        ]

    def __init__(self, *args, **kwargs):
        schedule = kwargs.pop("schedule", None)  # 🔹 Se elimina antes de super()
        super().__init__(*args, **kwargs)

        if schedule:
            self.fields["schedule"].initial = schedule
            self.fields["schedule"].disabled = True  # no editable

        self.fields["status"].initial = "Reservado"
        self.fields["status"].disabled = True