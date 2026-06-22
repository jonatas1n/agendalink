from django import forms
from django.core.exceptions import ValidationError

from core.store_slug import validate_store_slug

from .models import StoreProfile


class StoreSettingsForm(forms.ModelForm):
    slug = forms.SlugField(
        label="Endereço da sua loja",
        max_length=80,
        help_text="Letras minúsculas, números e hífens. Ex.: studio-bella",
    )

    class Meta:
        model = StoreProfile
        fields = [
            "slug",
            "name",
            "tagline",
            "description",
            "public_email",
            "public_phone",
            "city",
        ]
        labels = {
            "name": "Nome da loja",
            "tagline": "Frase de destaque",
            "description": "Sobre a loja",
            "public_email": "E-mail público",
            "public_phone": "Telefone / WhatsApp",
            "city": "Cidade ou região",
        }
        widgets = {
            "slug": forms.TextInput(
                attrs={
                    "placeholder": "minha-clinica",
                    "autocomplete": "off",
                    "autocapitalize": "off",
                    "autocorrect": "off",
                    "spellcheck": "false",
                    "inputmode": "url",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Ex.: Studio Bella, Clínica Saúde+",
                }
            ),
            "tagline": forms.TextInput(
                attrs={
                    "placeholder": "Ex.: Beleza e bem-estar no centro da cidade",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Conte um pouco sobre você ou seu negócio — aparece na página de agendamento.",
                }
            ),
            "public_email": forms.EmailInput(
                attrs={
                    "placeholder": "contato@sualoja.com",
                }
            ),
            "public_phone": forms.TextInput(
                attrs={
                    "placeholder": "Ex.: (11) 99999-0000",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "placeholder": "Ex.: São Paulo — Zona Sul",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.slug:
            self.fields["slug"].initial = self.instance.slug

    def clean_slug(self):
        raw = self.cleaned_data.get("slug") or ""
        exclude = self.instance.pk if self.instance else None
        try:
            return validate_store_slug(raw, exclude_profile_id=exclude)
        except ValidationError as e:
            raise forms.ValidationError(e.messages[0] if e.messages else str(e)) from e
