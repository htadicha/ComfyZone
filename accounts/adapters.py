from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Keep the custom User flags in sync with django-allauth confirmations.

    We mark users as verified/active as soon as their primary email has been
    confirmed via allauth's email confirmation flow.
    """

    def confirm_email(self, request, email_address):
        response = super().confirm_email(request, email_address)

        user = email_address.user
        updates = []

        if not user.is_verified:
            user.is_verified = True
            updates.append("is_verified")

        if not user.is_active:
            user.is_active = True
            updates.append("is_active")

        if updates:
            user.save(update_fields=updates)

        return response

