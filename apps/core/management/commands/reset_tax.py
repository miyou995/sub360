from django.core.management.base import BaseCommand

from apps.crm.models.company import Company


class Command(BaseCommand):
    help = "Initialize the project by loading locations and other setup tasks"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting project init process..."))
        self.reset_taxes()

    def reset_taxes(self):
        companies = Company.objects.all()
        for company in companies:
            company.set_goal()
            company.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Tax reset for company: {company.name} with ID: {company.id} - Goal: {company.annual_goal}"
                )
            )
