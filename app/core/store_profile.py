from .models import StoreProfile


def get_store_profile(user):
    profile, created = StoreProfile.objects.get_or_create(user=user)
    if created and not profile.name.strip():
        default_name = user.get_full_name().strip() or user.username
        profile.name = default_name
        profile.save(update_fields=["name", "updated_at"])
    return profile
