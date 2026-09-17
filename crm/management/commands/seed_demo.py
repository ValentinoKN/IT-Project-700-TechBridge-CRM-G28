from django.core.management.base import BaseCommand
from crm.models import User


class Command(BaseCommand):
    help = "Creates demo users for the class project"

    def handle(self, *args, **options):
        demo_users = [
            ("admin", "Administrator", User.ADMIN, True),
            ("manager", "Manager", User.MANAGER, False),
            ("rep", "Representative", User.REPRESENTATIVE, False),
        ]
        for username, first_name, role, is_superuser in demo_users:
            user, created = User.objects.get_or_create(username=username, defaults={"first_name": first_name, "role": role, "is_staff": is_superuser, "is_superuser": is_superuser})
            if created:
                user.set_password("DemoPass123!")
                user.save()
        self.stdout.write(self.style.SUCCESS("Demo users are ready."))

