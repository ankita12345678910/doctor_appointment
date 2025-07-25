from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from appointmentapp.models import UserDetails

class Command(BaseCommand):
    help = 'Seeds the database with an admin user.'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        email = 'admin@gmail.com'
        password = 'admin123'

        if not User.objects.filter(username=email).exists():
            # 1. Create the admin user
            user = User.objects.create_superuser(
                username=email,
                email=email,
                password=password,
                first_name='Admin',
                last_name='User'
            )

            UserDetails.objects.create(
                user=user,
                role='role_admin',
                phone_number='1234567890',
                address='Admin HQ'
            )

            self.stdout.write(self.style.SUCCESS(f"✅ Admin user created:\nEmail: {email}\nPassword: {password}"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ Admin user already exists: {email}"))
