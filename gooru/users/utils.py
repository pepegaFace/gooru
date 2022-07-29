from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

from gooru import settings


def email_generator(title, text, to_user):
    email_message = {
            'subject': title,
            'text': text + """\nThanks for using our site!

The compas-goo.ru team""",
            
            'html': text + """\nThanks for using our site!

The compas-goo.ru team""",

            'from': {'name': 'Compass Pro', 'email': settings.DEFAULT_FROM_EMAIL},
            'to': [{'name': to_user.username, 'email': to_user.email}]
    }
    return email_message


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )
account_activation_token = TokenGenerator()