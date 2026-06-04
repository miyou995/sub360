import logging
from datetime import date

import pandas as pd
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from apps.core.export import DataExporter

logger = logging.getLogger(__name__)


class ImportDataMixin:
	fields = None
	required_fields = None

	def get_import_file(self):
		return self.request.FILES.get('import_file')

	def get_type_of_fields_from_model(self):
		model = self.model
		if self.fields:
			field_names = self.fields
		else:
			all_fields = model._meta.get_fields()
			field_names = [
				f.name
				for f in all_fields
				if f.editable and (not f.is_relation or f.one_to_one or (f.many_to_one and f.related_model))
			]
		return {field_name: model._meta.get_field(field_name).get_internal_type() for field_name in field_names}

	def get_duplicate_check_fields(self):
		raise NotImplementedError('You must define `get_duplicate_check_fields` method in your view.')

	def get_required_fields(self):
		return self.required_fields or []

	def get_extra_columns(self):
		return []

	def process_field_value(self, field_name, field_type, row_value):
		if pd.isna(row_value) or row_value == '':
			return None

		if field_type == 'ForeignKey':
			field = self.model._meta.get_field(field_name)
			related_model = field.related_model
			try:
				if hasattr(related_model, 'name'):
					instance, _ = related_model.objects.get_or_create(name=row_value)
				else:
					text_fields = [
						f for f in related_model._meta.fields if f.get_internal_type() in ['CharField', 'TextField']
					]
					if text_fields:
						instance, _ = related_model.objects.get_or_create(**{text_fields[0].name: row_value})
					else:
						return None
				return instance
			except Exception as e:
				logger.error(f'Error processing foreign key {field_name}: {e}')
				return None

		if field_type == 'DateField':
			try:
				return pd.to_datetime(row_value, errors='coerce').date()
			except Exception as e:
				logger.error(f'Error processing date field {field_name}: {e}')
				return None

		if field_type == 'BooleanField':
			if isinstance(row_value, bool):
				return row_value
			return str(row_value).lower() in ['true', '1', 'yes', 'on', 'oui']

		if field_type in ['DecimalField', 'FloatField']:
			try:
				return float(row_value)
			except (ValueError, TypeError):
				return None

		if field_type in ['IntegerField', 'BigIntegerField', 'SmallIntegerField', 'PositiveIntegerField']:
			try:
				return int(row_value)
			except (ValueError, TypeError):
				return None

		return row_value

	def process_import_data(self, dbframe):
		field_mappings = self.get_type_of_fields_from_model()
		duplicate_fields = self.get_duplicate_check_fields()
		required_fields = self.get_required_fields()

		created_count = 0
		updated_count = 0
		skipped_rows = 0

		for index, row in dbframe.iterrows():
			instance_data = {}
			for file_column, field_type in field_mappings.items():
				if file_column not in row:
					continue
				custom_method = f'process_{file_column}'
				if hasattr(self, custom_method):
					processed_value = getattr(self, custom_method)(row[file_column])
				else:
					processed_value = self.process_field_value(file_column, field_type, row[file_column])
				if processed_value is not None:
					instance_data[file_column] = processed_value

			missing_required = [f for f in required_fields if f not in instance_data or instance_data[f] is None]
			if missing_required:
				skipped_rows += 1
				continue

			duplicate_filter = {f: instance_data[f] for f in duplicate_fields if instance_data.get(f)}
			existing_instance = self.model.objects.filter(**duplicate_filter).first() if duplicate_filter else None

			try:
				if existing_instance is None:
					instance = self.model.objects.create(**instance_data)
					created_count += 1
				else:
					for key, value in instance_data.items():
						setattr(existing_instance, key, value)
					existing_instance.save()
					instance = existing_instance
					updated_count += 1
			except Exception as e:
				logger.error(f'Error processing row {index}: {e}')
				skipped_rows += 1
				continue

			for extra_col in self.get_extra_columns():
				if extra_col not in row:
					continue
				custom_method = f'process_{extra_col}'
				if hasattr(self, custom_method):
					try:
						getattr(self, custom_method)(instance, row[extra_col], row)
					except Exception as e:
						logger.error(f"Error processing extra column '{extra_col}' for row {index}: {e}")

			self.process_multiple_related_fields(instance, row)

		model_name = self.model._meta.verbose_name_plural
		messages.success(self.request, f'{created_count} {model_name} created successfully.')
		if updated_count:
			messages.success(self.request, f'{updated_count} {model_name} updated successfully.')
		if skipped_rows:
			messages.warning(self.request, f'{skipped_rows} rows skipped (duplicates, missing data, or errors).')

	def process_multiple_related_fields(self, instance, row):
		pass

	def process_related_field(self, instance, row, config):
		related_model = config['model']
		foreign_key_field = config['foreign_key_field']
		value_field = config['value_field']
		column_prefix = config['column_prefix']
		related_columns = [col for col in row.index if col.lower().startswith(column_prefix)]
		for col in related_columns:
			if pd.notna(row[col]) and str(row[col]).strip():
				value = str(row[col]).strip()
				related_model.objects.get_or_create(**{foreign_key_field: instance, value_field: value})

	def get_related_instance(self, model, row, field_name):
		instance = None
		field_value = getattr(row, field_name, None)
		if pd.notna(field_value):
			try:
				lookup_field = 'id' if isinstance(field_value, (int, float)) else 'name__iexact'
				instance = model.objects.get(**{lookup_field: field_value})
			except ObjectDoesNotExist:
				instance = model.objects.create(name=field_value)
				messages.success(self.request, _(f'{model.__name__} {field_value} created successfully'))
		return instance

	def import_data(self, request):
		import_file = self.get_import_file()
		if import_file is None:
			messages.error(request, _('Please upload a file'))
			return redirect(self.get_failure_url())

		filename = import_file.name if hasattr(import_file, 'name') else ''
		ext = filename.rsplit('.', 1)[-1].lower()
		if ext not in ['csv', 'xls', 'xlsx']:
			messages.error(request, _('Unsupported file type. Please upload a CSV or Excel file.'))
			return redirect(self.get_failure_url())

		try:
			dbframe = pd.read_csv(import_file) if ext == 'csv' else pd.read_excel(import_file)
		except Exception as e:
			messages.error(request, _('Error reading file: ') + str(e))
			return redirect(self.get_failure_url())

		with transaction.atomic():
			try:
				self.process_import_data(dbframe)
			except Exception as e:
				logger.error(f'Error processing import data: {e}')
				messages.error(request, _('Error processing data: Contact Octopus Support'))
				return redirect(self.get_failure_url())
		return redirect(self.get_success_url())

	def get_failure_url(self):
		return self.request.headers.get('referer', '/')

	def get_success_url(self):
		return self.request.headers.get('referer', '/')

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, self.get_context_data(**kwargs))

	def post(self, request, *_, **__):
		return self.import_data(request)


class ExportDataMixin:
	export_functions = {
		'excel': 'export_to_excel',
		'csv': 'export_to_csv',
		'pdf': 'export_to_pdf',
	}
	fields = []

	def get_export_data(self):
		exported_data = []
		for obj in self.model.objects.all():
			row = []
			for field_name in self.fields:
				value = getattr(obj, field_name, '')
				field_object = None
				try:
					field_object = obj._meta.get_field(field_name)
				except Exception:
					pass
				if field_object and field_object.many_to_many:
					value = ', '.join(str(item) for item in getattr(obj, field_name).all())
				elif not isinstance(value, (str, int, float, bool, type(None))):
					value = str(value)
				row.append(value)
			exported_data.append(tuple(row))
		return exported_data

	def get_export_columns(self):
		return self.fields

	def export_data(self, request):
		extension = request.POST.get('extension')
		export_function = self.export_functions.get(extension)
		if export_function is None:
			messages.error(request, 'Please select a valid format to export')
			return redirect(self.get_failure_url())
		data = self.get_export_data()
		columns = self.get_export_columns()
		exporter = DataExporter(data, columns)
		messages.success(request, 'exported successfully')
		return getattr(exporter, export_function)(file_name=self.get_export_file_name())

	def get(self, request, *args, **kwargs):
		return redirect(request.path)

	def post(self, request, *args, **kwargs):
		return self.export_data(request)

	def get_failure_url(self):
		return self.request.path

	def get_export_file_name(self):
		return f'{self.model._meta.model_name}_export_{date.today()}'


class TableImportFieldsMixin:
	model = None
	fields = None
	extra_fields = None
	related_fields = {}
	template_name = 'tables/_table_import_fields.html'

	def get_list_related_fields(self):
		return [f'{field}_{i}' for field in self.related_fields for i in range(1, 3)]

	def get_type_of_fields_from_model(self):
		if self.fields:
			field_names = self.fields
		else:
			field_names = [f.name for f in self.model._meta.get_fields() if hasattr(f, 'get_internal_type')]

		field_info = []
		for field_name in field_names:
			try:
				field = self.model._meta.get_field(field_name)
				choices = []
				if hasattr(field, 'choices') and field.choices:
					choices = [{'value': c[0], 'label': c[1]} for c in field.choices]
				elif hasattr(field, 'related_model') and field.many_to_many:
					choices = [{'value': obj.pk, 'label': str(obj)} for obj in field.related_model.objects.all()]
				required = False
				if hasattr(field, 'blank'):
					required = not field.blank and not field.null
				elif hasattr(field, 'null'):
					required = not field.null
				field_info.append({
					'name': field.name,
					'verbose_name': getattr(field, 'verbose_name', field_name),
					'type': field.get_internal_type(),
					'required': required,
					'choices': choices,
					'help_text': getattr(field, 'help_text', ''),
				})
			except Exception:
				continue
		if self.extra_fields:
			field_info += self.extra_fields
		return field_info

	def get_context_data(self, **kwargs):
		return {
			'import_fields': self.get_type_of_fields_from_model(),
			'related_fields': self.get_list_related_fields(),
		}

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, self.get_context_data(**kwargs))
