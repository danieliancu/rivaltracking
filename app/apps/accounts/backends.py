"""Case-insensitive email authentication backend."""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    """Authenticate by email (accepts either ``email`` or ``username`` kwarg)."""

    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        User = get_user_model()
        identifier = email or username
        if identifier is None or password is None:
            return None
        try:
            user = User.objects.get(email__iexact=identifier)
        except User.DoesNotExist:
            # Run the default hasher once to reduce timing differences between
            # "no such user" and "wrong password".
            User().set_password(password)
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
