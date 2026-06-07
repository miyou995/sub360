# Forms for the tenders app.

from django import forms

from apps.core.abstract_forms import AbstractModelForm

from .models import Tender


class TenderForm(AbstractModelForm):
    class Meta:
        model = Tender
        fields = (
            "title",
            "owner",
            "description",
            "execution_type",
            "branch",
            "canton",
            "city",
            "zip_code",
            "start_date",
            "application_deadline",
            "material_offered",
            "material",
            "project_volume",
            "procedure",
            "status",
        )
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "application_deadline": forms.DateInput(attrs={"type": "date"}),
        }
