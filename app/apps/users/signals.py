from apps.users.models import Profile
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


@receiver(post_save, sender=User)
def create_profile_new_user(sender, created, instance: User, **kwargs):
    if created:
        Profile.objects.get_or_create(defaults=dict(user=instance))

    return instance
