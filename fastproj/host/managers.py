from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, userName, email=None, password=None, **extra_fields):
        if not userName:
            raise ValueError('The UserName field must be set')
        email = self.normalize_email(email)
        user = self.model(userName=userName, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
