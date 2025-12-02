from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit

from .models import MarketingLead, NewsletterSubscriber


class NewsletterSubscriptionForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email", "name", "consent"]
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "Enter your email"}),
            "name": forms.TextInput(attrs={"placeholder": "Enter your name (optional)"}),
        }
        help_texts = {
            "consent": "I agree to receive product updates and marketing emails from ComfyZone.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["consent"].required = True
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("name", css_class="col-auto"),
                Column("email", css_class="col-auto"),
                Column("consent", css_class="col-auto pt-2"),
                Column(
                    Submit("submit", "Subscribe", css_class="btn btn-primary"),
                    css_class="col-auto"
                ),
                css_class="row g-3"
            )
        )


class MarketingLeadForm(forms.ModelForm):
    class Meta:
        model = MarketingLead
        fields = ["name", "email", "phone", "interest", "message", "consent"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4}),
        }
        help_texts = {
            "consent": "I consent to being contacted about ComfyZone products and services.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["consent"].required = True
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("name", css_class="col-md-6"),
                Column("email", css_class="col-md-6"),
            ),
            Row(
                Column("phone", css_class="col-md-6"),
                Column("interest", css_class="col-md-6"),
            ),
            "message",
            "consent",
            Submit("submit", "Send enquiry", css_class="btn btn-primary"),
        )
