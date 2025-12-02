from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "title", "comment"]
        widgets = {
            "rating": forms.NumberInput(attrs={"type": "hidden", "id": "id_rating"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "comment": forms.Textarea(attrs={"rows": 5, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "title",
            "comment",
            "rating",  # Hidden field for the actual rating value
            Submit("submit", "Submit Review", css_class="btn btn-primary")
        )

    def clean_rating(self):
        rating = self.cleaned_data.get("rating")
        if not rating or int(rating) not in {1, 2, 3, 4, 5}:
            raise ValidationError("Please select a rating between 1 and 5 stars.")
        return rating
