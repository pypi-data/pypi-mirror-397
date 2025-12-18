import functools

from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from rest_framework.authtoken.models import Token

from .utils import TimesStampMixin, generate_thumbnail, content_file_name


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Gives each newly created user an auth token by default
    """

    if created:
        Token.objects.create(user=instance)


class Member(User, TimesStampMixin):
    phone = models.CharField(max_length=100, blank=True, null=True)
    profile = models.ImageField(
        null=True, blank=True, upload_to=functools.partial(content_file_name, "profile")
    )
    profile_thumbnail = models.ImageField(null=True, blank=True)

    class Meta:
        verbose_name = "Portal Member"
        verbose_name_plural = "Portal Members"

    def __str__(self):
        return self.username

    @classmethod
    def post_create(cls, sender, instance, created, *args, **kwargs):

        if not created:
            return

        group = Group.objects.filter(name="regular_users").first()
        if group:
            instance.groups.add(group)

    def save(self, *args, **kwargs):
        if not self.profile:
            self.profile_thumbnail = None
        else:
            self.profile_thumbnail.name = generate_thumbnail(
                self, "profile", self.profile
            )
        super().save(*args, **kwargs)


post_save.connect(Member.post_create, sender=Member)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_member(sender, instance=None, created=False, **kwargs):
    """
    When we create users also create a corresponding member
    Exclude first user (as admin)
    """

    if created and instance.pk > 1:
        member = Member(user_ptr_id=instance.pk)
        member.__dict__.update(instance.__dict__)
        member.save()


MEMBER_ID_CHOICES = [("ORCID", "ORCID"), ("FREEFORM", "Freeform")]


class MemberIdentifier(models.Model):
    id_type = models.CharField(max_length=8, choices=MEMBER_ID_CHOICES)
    value = models.CharField(max_length=48)
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="identifiers"
    )
