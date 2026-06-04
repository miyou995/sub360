from django.core.management.base import BaseCommand

from public_apps.tenant.models import Client, Domain  # or your tenant model


class Command(BaseCommand):
	help = 'Initialize the project by loading locations and other setup tasks'

	def handle(self, *args, **options):
		self.stdout.write(self.style.SUCCESS('Starting project init process...'))

		tenant = Client.objects.create(schema_name='public', name='Public Tenant')

		Domain.objects.create(
			domain='localhost',  # VERY IMPORTANT
			tenant=tenant,
			is_primary=True,
		)
