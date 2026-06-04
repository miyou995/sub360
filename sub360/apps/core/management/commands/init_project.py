import json
import os
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone
from django_tenants.utils import tenant_context

from apps.subscription.models import Subscription
from apps.wilayas.models import Commune, Wilaya
from public_apps.landing.models import Plan


class Command(BaseCommand):
	help = 'Initialize the project by loading locations and other setup tasks'

	def handle(self, *args, **options):
		self.stdout.write(self.style.SUCCESS('Starting project init process...'))
		call_command('migrate')
		self.create_superuser()
		self.create_public_tenant()
		self.create_demo_tenant()

		self.stdout.write(self.style.SUCCESS('Project Inited completed successfully!'))

	def create_superuser(self):
		User = get_user_model()
		if not User.objects.filter(email='admin@admin.com').exists():
			User.objects.create_superuser(email='admin@admin.com', password='admin')
			self.stdout.write(self.style.SUCCESS('Superuser created successfully!'))
		else:
			self.stdout.write(self.style.WARNING('Superuser already exists.'))

	def load_wilayas(self):
		self.stdout.write(self.style.SUCCESS('Loading wilayas...'))
		wilayas_path = os.path.join(settings.BASE_DIR, 'fixtures', 'wilayas.json')
		with open(wilayas_path, encoding='utf-8') as f:
			wilayas_data = json.load(f)

		wilaya_objs = [
			Wilaya(
				id=int(w['id']),
				code=w['code'],
				name=w['name'],
				ar_name=w['ar_name'],
				longitude=float(w['longitude']),
				latitude=float(w['latitude']),
			)
			for w in wilayas_data
		]

		Wilaya.objects.bulk_create(wilaya_objs, ignore_conflicts=True)
		self.stdout.write(self.style.SUCCESS('Locations loaded successfully!'))

	def load_communes(self):
		self.stdout.write(self.style.SUCCESS('Loading communes...'))
		communes_path = os.path.join(settings.BASE_DIR, 'fixtures', 'communes.json')
		with open(communes_path, encoding='utf-8') as f:
			communes_data = json.load(f)
		communes_objs = [
			Commune(
				id=int(c['id']),
				wilaya_id=int(c['wilaya_id']),
				name=c['name'],
				postal_code=c.get('postal_code', ''),
				ar_name=c.get('ar_name', ''),
				longitude=float(c.get('longitude', 0)),
				latitude=float(c.get('latitude', 0)),
				is_active=c.get('is_active', True),
			)
			for c in communes_data
		]
		Commune.objects.bulk_create(communes_objs, ignore_conflicts=True)

		self.stdout.write(self.style.SUCCESS('Communes loaded successfully!'))

	def create_public_tenant(self):
		from public_apps.tenant.models import Client, Domain

		public_tenant = Client.objects.filter(schema_name='public').first()
		if not public_tenant:
			Client.objects.bulk_create(
				[Client(schema_name='public', name='public')],
				ignore_conflicts=True,
			)
			public_tenant = Client.objects.get(schema_name='public')
			self.stdout.write(self.style.SUCCESS('Public tenant created.'))
		else:
			self.stdout.write(self.style.WARNING('Public tenant already exists.'))

		Domain.objects.get_or_create(
			domain='localhost' if settings.DEBUG else 'octocrm.app',
			defaults={'tenant': public_tenant, 'is_primary': True},
		)

	def create_demo_tenant(self):
		from public_apps.tenant.models import Client, Domain

		TENANT_EMAIL = 'admin@admin.com'
		TENANT_PASSWORD = '123456'
		SCHEMA_NAME = 'admin'
		DOMAIN = 'admin.localhost' if settings.DEBUG else 'admin.octocrm.app'

		self.stdout.write(self.style.SUCCESS('Creating demo tenant...'))

		tenant, created = Client.objects.get_or_create(
			schema_name=SCHEMA_NAME,
			defaults={'name': 'admin'},
		)
		Domain.objects.get_or_create(domain=DOMAIN, tenant=tenant, is_primary=True)
		if created:
			self.stdout.write(self.style.SUCCESS(f'Tenant "{SCHEMA_NAME}" created.'))
		else:
			self.stdout.write(
				self.style.WARNING(f'Tenant "{SCHEMA_NAME}" already exists.')
			)

		with tenant_context(tenant):
			User = get_user_model()
			if not User.objects.filter(email=TENANT_EMAIL).exists():
				User.objects.create_superuser(
					email=TENANT_EMAIL, password=TENANT_PASSWORD
				)
				Subscription.objects.create(
					plan=Plan.objects.first(),  # Assuming you have a default plan
					starting_date=timezone.now(),
					ending_date=timezone.now() + timedelta(days=30),
					is_paid=True,
					is_active=True,
					on_trial=False,
				)
				self.stdout.write(
					self.style.SUCCESS(
						f'Superuser {TENANT_EMAIL} created in tenant schema.'
					)
				)
			else:
				self.stdout.write(
					self.style.WARNING(
						f'User {TENANT_EMAIL} already exists in tenant schema.'
					)
				)

			store = self.ensure_demo_store()

			init_data_path = os.path.join(
				settings.BASE_DIR, 'fixtures', 'init_data.json'
			)
			if os.path.exists(init_data_path):
				self.load_wilayas()
				self.load_communes()
				self.load_demo_fixture(init_data_path, store)
				self.stdout.write(
					self.style.SUCCESS('init_data.json loaded into tenant schema.')
				)
			else:
				self.stdout.write(
					self.style.WARNING('fixtures/init_data.json not found, skipping.')
				)

	def ensure_demo_store(self):
		from apps.business.models import LegalEntity, Store

		legal_entity = LegalEntity.objects.filter(pk=1).first()
		if legal_entity is None:
			legal_entity = LegalEntity.objects.create(name='Entité principale')

		store = Store.objects.filter(is_main=True).select_related('legal_entity').first()
		if store is None:
			store = Store.objects.create(
				name_company='admin',
				legal_entity=legal_entity,
				store_type='main',
				is_main=True,
				is_active=True,
			)
		elif store.legal_entity_id is None:
			store.legal_entity = legal_entity
			store.save(update_fields=['legal_entity'])

		return store

	def load_demo_fixture(self, fixture_path, store):
		call_command('loaddata', fixture_path)
