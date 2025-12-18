import unicodedata

from django.contrib.auth.models import Group

# from rest_framework.authtoken.models import Token
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from ..models.member import Member


def generate_username(email):

    return unicodedata.normalize("NFKC", email.split("@")[0][:150])


class MemberOIDCAuthenticationBackend(OIDCAuthenticationBackend):

    def __init__(self, *args, **kwargs):
        self.default_scopes = ("openid", "email", "profile")
        super().__init__(self, args, kwargs)

    def get_scopes(self):
        env_settings = self.get_settings("OIDC_RP_SCOPES", None)
        if env_settings:
            return env_settings.split()
        return self.default_scopes

    def verify_claims(self, claims):
        if "email" not in claims:
            return False
        return True

    def get_username(self, claims):
        if "preferred_username" in claims:
            return claims["preferred_username"]
        return generate_username(claims.get("email"))

    def create_user(self, claims):
        user = super().create_user(claims)
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")

        # Create an associated Member
        member = Member(user_ptr_id=user.pk)
        member.__dict__.update(user.__dict__)

        # If there's a 'regular user' group assign them
        group = Group.objects.filter(name="regular_users").first()
        if group:
            member.groups.add(group)
        member.save()

        # Token.objects.create(user=user)

        return user
