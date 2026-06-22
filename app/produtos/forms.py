from django import forms
from django.core.exceptions import ValidationError

from core.store_profile import get_store_profile
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "image",
            "simultaneous_capacity",
            "service_kind",
            "contact_channel",
            "price_criterion",
            "price_criterion_label",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Ex: Sala de reunião, Quadra esportiva..."}
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Descreva o que está sendo agendado...",
                }
            ),
            "service_kind": forms.RadioSelect,
            "contact_channel": forms.RadioSelect,
        }
        labels = {
            "name": "Nome do produto/serviço",
            "description": "Descrição",
            "image": "Foto (opcional)",
            "simultaneous_capacity": "Vagas simultâneas",
            "service_kind": "Tipo",
            "contact_channel": "Como o cliente pode entrar em contato",
        }

    def clean(self):
        cleaned = super().clean()
        kind = cleaned.get("service_kind") or "agendamento"
        description = (cleaned.get("description") or "").strip()
        channel = cleaned.get("contact_channel") or ""

        if kind == "outros":
            if not description:
                raise ValidationError("Para o tipo Outros, preencha a descrição.")
            if channel not in dict(Product.CONTACT_CHANNEL):
                raise ValidationError("Escolha como o cliente pode entrar em contato.")
            owner = getattr(self.instance, "owner", None)
            if owner is not None:
                store = get_store_profile(owner)
                if (
                    channel in ("email", "both")
                    and not (store.public_email or "").strip()
                ):
                    raise ValidationError(
                        "Informe um e-mail público em Definições da loja para contato por e-mail.",
                    )
                if (
                    channel in ("whatsapp", "both")
                    and not (store.public_phone or "").strip()
                ):
                    raise ValidationError(
                        "Informe telefone/WhatsApp em Definições da loja para contato por WhatsApp.",
                    )
        else:
            cleaned["contact_channel"] = ""
        return cleaned
