from django.core.management.base import BaseCommand

from apps.core.tasks import sync_all_google_sheets


class Command(BaseCommand):
	help = 'Runs Celery worker with the specified settings'

	def handle(self, *args, **options):
		self.stdout.write(self.style.SUCCESS('Starting importing from sheet...'))

		result = sync_all_google_sheets()
		self.stdout.write(
			self.style.SUCCESS(f'Task sync_all_google_sheets result: {result}')
		)
