from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

# Model za tipove korisnika
class User(AbstractUser):
    USER_TYPES = (
        ('unauthenticated', 'Unauthenticated'),
        ('authenticated', 'Authenticated'),
        ('admin', 'Admin'),
    )
    # Dodatna polja za User model
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='unauthenticated')
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username

# Model za verificiranog korisnika sa dodatnim poljima
class VerifiedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="verified_user")
    follower_count = models.IntegerField(default=0)
    post_count = models.IntegerField(default=0)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)

    def __str__(self):
        return f"VerifiedUser: {self.user.username}"

# Model za admin korisnika
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin_profile")

    def __str__(self):
        return f"Admin: {self.user.username}"