from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import NewsletterSubscriber


class NewsletterSubscriptionForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email", "name"]
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "Enter your email"}),
            "name": forms.TextInput(attrs={"placeholder": "Enter your name (optional)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("name", css_class="col-auto"),
                Column("email", css_class="col-auto"),
                Column(
                    Submit("submit", "Subscribe", css_class="btn btn-primary"),
                    css_class="col-auto"
                ),
                css_class="row g-3"
            )
        )


