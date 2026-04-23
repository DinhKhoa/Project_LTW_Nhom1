from django import forms
from django.contrib.auth.models import User
from .models import InstallationTask


class InstallationTaskForm(forms.ModelForm):
    assigned_staff = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Nhân viên phụ trách",
    )

    class Meta:
        model = InstallationTask
        fields = ["assigned_staff", "status", "note"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-control"}),
            "note": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Ghi chú kỹ thuật...",
                }
            ),
        }
