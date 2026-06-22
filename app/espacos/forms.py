from django import forms

from .models import Space, SpaceMember


class SpaceForm(forms.ModelForm):
    class Meta:
        model = Space
        fields = [
            "name",
            "description",
            "address",
            "logo",
            "cover_photo",
            "collective_schedule_active",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Ex: Coworking Central, Clínica Bem Estar…"}
            ),
            "description": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Conte sobre o espaço…"}
            ),
            "address": forms.TextInput(attrs={"placeholder": "Rua, número, cidade…"}),
        }
        labels = {
            "name": "Nome do espaço",
            "description": "Sobre o espaço",
            "address": "Endereço",
            "logo": "Logo",
            "cover_photo": "Foto de capa",
            "collective_schedule_active": "Permitir que membros vejam a agenda coletiva",
        }


class MemberProfileForm(forms.ModelForm):
    class Meta:
        model = SpaceMember
        fields = ["bio", "specialty", "profile_photo"]
        widgets = {
            "bio": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Apresentação curta…"}
            ),
            "specialty": forms.TextInput(
                attrs={"placeholder": "Ex: Fisioterapia, Design, Advocacia…"}
            ),
        }
        labels = {
            "bio": "Sobre você",
            "specialty": "Especialidade",
            "profile_photo": "Foto de perfil",
        }
