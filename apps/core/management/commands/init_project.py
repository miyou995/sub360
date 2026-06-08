from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Initialize the project by loading locations and other setup tasks"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting project init process..."))
        call_command("migrate")
        self.stdout.write(self.style.SUCCESS("Migrations completed successfully!"))

        self.create_superuser()

        # self.load_demo_fixture("locations.json", "core")
        # self.load_fixture("apps/projects/fixtures/branches.json")
        # self.load_fixture("apps/projects/fixtures/execution_types.json")
        self.stdout.write(self.style.SUCCESS("Project Inited completed successfully!"))

    def create_superuser(self):
        User = get_user_model()
        if not User.objects.filter(email="admin@admin.com").exists():
            User.objects.create_superuser(email="admin@admin.com", password="admin")
            self.stdout.write(
                self.style.SUCCESS(
                    "Superuser admin@admin.com password: admin created successfully!"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING("Superuser admin@admin.com already exists.")
            )

    def load_fixture(self, fixture_path):
        call_command("loaddata", fixture_path)
        self.stdout.write(self.style.SUCCESS(f"Loaded fixture: {fixture_path}"))

    def load_demo_fixture(self, fixture_path, store):
        call_command("loaddata", fixture_path)
