from django import forms


class PaidSubscribeForm(forms.Form):
    cpf_cnpj = forms.CharField(
        label="CPF ou CNPJ",
        max_length=18,
        widget=forms.TextInput(
            attrs={"placeholder": "000.000.000-00 ou 00.000.000/0000-00"}
        ),
    )
