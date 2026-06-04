from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.models import BaseInlineFormSet


class SelectWithCreateMixin:
	"""
	Automatically inject create URL if the related model
	defines `get_create_url()`.
	"""

	enable_auto_create_url = True

	def apply_create_urls(self):
		if not self.enable_auto_create_url:
			return

		for name, field in self.fields.items():
			widget = field.widget

			if isinstance(field, forms.ModelChoiceField):
				if field.queryset is None:
					continue
				model = field.queryset.model

				if (
					hasattr(model, 'get_inline_create_url')
					and callable(model.get_inline_create_url)
					and hasattr(model, 'get_options_fragment_url')
					and callable(model.get_options_fragment_url)
				):
					try:
						widget.attrs.update(
							{
								'data_create_url': model.get_inline_create_url(),
								'hx-get': model.get_options_fragment_url(),
								'hx-target': 'this',  # manually compute ID
								'hx-swap': 'innerHTML',
								'hx-trigger': f'refresh_{model._meta.model_name} from:body delay:100',
							}
						)
					except Exception as e:
						import logging

						logger = logging.getLogger(__name__)
						logger.warning(
							f'Failed to configure inline create for {model.__name__}: {e}'
						)
						continue


class AutoSelect2Mixin:
	select2_threshold = 10
	enable_select2 = True

	def apply_select2(self):
		if not self.enable_select2:
			return

		for field in self.fields.values():
			widget = field.widget

			if isinstance(widget, (forms.Select, forms.SelectMultiple)):
				widget.attrs['data-control'] = 'select2'
				# Default hide search
				widget.attrs['data-hide-search'] = 'true'

				# Only check threshold if ModelChoiceField
				if isinstance(field, forms.ModelChoiceField):
					if field.queryset.count() > self.select2_threshold:
						widget.attrs['data-hide-search'] = 'false'


class UIFormMixin:
	input_css_class = 'form-control'
	select_css_class = 'form-select'
	checkbox_css_class = 'form-check-input'
	col_class = 'col-12 col-md-6 mb-4'

	def _append_class(self, field, css_class):
		existing = field.widget.attrs.get('class', '')
		field.widget.attrs['class'] = f'{existing} {css_class}'.strip()

	def apply_style(self):
		for field in self.fields.values():
			field.widget.attrs.setdefault('field_group_class', self.col_class)
			widget = field.widget
			if isinstance(
				widget,
				(
					forms.TextInput,
					forms.EmailInput,
					forms.PasswordInput,
					forms.NumberInput,
				),
			):
				self._append_class(field, self.input_css_class)

			elif isinstance(widget, forms.Textarea):
				self._append_class(field, self.input_css_class)
				rows = widget.attrs.get('rows')
				if rows is None or str(rows) == '10':  # Django default
					widget.attrs['rows'] = 3
				# Django default is string "10". User usually passes int 10.

			elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
				self._append_class(field, self.select_css_class)

			elif isinstance(widget, forms.CheckboxInput):
				self._append_class(field, self.checkbox_css_class)
			else:
				self._append_class(field, self.input_css_class)


class FormUIMixin(SelectWithCreateMixin, AutoSelect2Mixin, UIFormMixin):
	"""
	Bundles all UI setup mixins and shared initialisation logic.
	Shared by both AbstractForm and AbstractModelForm so there is
	a single place to add new auto-styling behaviour.
	"""

	def _setup_ui(self, modal_context=None):
		self.apply_style()
		self.apply_select2()
		self.apply_create_urls()
		if modal_context:
			self.apply_modal_context(modal_context)

	def apply_modal_context(self, modal_context):
		"""Stamp modal-level attrs onto every widget that has a create URL."""
		for field in self.fields.values():
			if field.widget.attrs.get('data_create_url'):
				field.widget.attrs.update(
					{
						'data_is_modal_context': modal_context['is_modal_context'],
						'data_next_modal_id': modal_context['next_modal_id'],
						'data_next_modal_content_id': modal_context[
							'next_modal_content_id'
						],
					}
				)


class AbstractForm(forms.Form, FormUIMixin):
	"""
	Base class for plain (non-model) forms.

	Automatically applies Bootstrap CSS classes, Select2 widget config,
	and inline-create URL injection to all fields — identical behaviour
	to AbstractModelForm, just without the model binding.

	Usage::

	        class ChangeOwnerForm(AbstractForm):
	            target_user = forms.ModelChoiceField(queryset=User.objects.all())
	"""

	def __init__(self, *args, **kwargs):
		# Modal context is injected by BaseManageHtmxFormView so field.html
		# can render the + button at the correct stacked modal level.
		modal_context = kwargs.pop('modal_context', None)
		self.request = kwargs.pop('request', None)

		super().__init__(*args, **kwargs)
		self._setup_ui(modal_context)


class AbstractModelForm(forms.ModelForm, FormUIMixin):
	"""
	Base ModelForm for all model-backed forms.

	Tenant isolation
	----------------
	When a ``store`` kwarg is passed (injected automatically by
	``TenantAwareViewMixin.get_form_kwargs``):

	1. The store is stored as ``self.store`` for subclass use.
	2. ``ModelChoiceField`` querysets whose model is a ``TenantModel``
	   subclass are automatically filtered to ``store``.  This prevents
	   cross-tenant data leakage without any per-form boilerplate.
	3. On new (unsaved) instances, ``instance.store`` is pre-populated so
	   forms that include ``store`` as a hidden/excluded field work correctly.

	Subclasses only need to override queryset scoping when the field's model
	is NOT a TenantModel (e.g. a public Tag) or when additional filters beyond
	``store`` are required.
	"""

	def __init__(self, *args, **kwargs):
		# Modal context is injected by BaseManageHtmxFormView so field.html
		# can render the + button at the correct stacked modal level.
		self.request = kwargs.pop('request', None)
		modal_context = kwargs.pop('modal_context', None)
		super().__init__(*args, **kwargs)
		self._setup_ui(modal_context)


class AbstractFilterForm(AbstractForm):
	"""
	Base form for django-filter FilterSets.
	Applies all Bootstrap/Select2 styling but suppresses the inline-create
	'+' button that AbstractForm injects for ModelChoiceFields.
	"""

	enable_auto_create_url = False
	col_class = 'col-12 mb-4'


class NestedInlineFormSet(BaseInlineFormSet):
	"""
	Inline formset that attaches nested child formsets to each form.

	Usage::

		# 1. Define the inner (child) formset with inlineformset_factory
		ChildFormSet = forms.inlineformset_factory(Parent, Child, ...)

		# 2. Define the outer formset using this class as the base
		ParentFormSet = forms.inlineformset_factory(
			GrandParent, Parent, formset=NestedInlineFormSet, ...
		)
		ParentFormSet.nested_formset_class = ChildFormSet
		ParentFormSet.nested_prefix = 'children'

	Each form in the outer formset will have a ``.nested`` attribute containing
	the child formset instance.  ``is_valid()`` and ``save()`` cascade
	automatically into nested formsets.
	"""

	nested_formset_class = None
	nested_prefix = 'nested'

	def __init__(self, data=None, files=None, instance=None, **kwargs):
		super().__init__(data=data, files=files, instance=instance, **kwargs)
		self._cached_empty = None
		self._attach_nested_formsets()

	# ── Property override to return cached empty form with nested ────────
	@property
	def empty_form(self):
		if self._cached_empty is not None:
			return self._cached_empty
		return BaseFormSet.empty_form.fget(self)

	# ── Build & attach nested formsets ───────────────────────────────────
	def _attach_nested_formsets(self):
		if not self.nested_formset_class:
			return

		bound_data = self.data if self.is_bound else None
		bound_files = self.files if self.is_bound else None

		# Attach a nested formset to every real form
		for i, form in enumerate(self.forms):
			prefix = f'{self.prefix}-{i}-{self.nested_prefix}'
			form.nested = self.nested_formset_class(
				data=bound_data,
				files=bound_files,
				instance=form.instance,
				prefix=prefix,
			)

		# Build the cached empty_form with a special nested formset that
		# uses ``__nested__`` instead of ``__prefix__`` so JS can handle
		# two levels of placeholder replacement without collision.
		empty_prefix = f'{self.prefix}-__prefix__-{self.nested_prefix}'
		parent_cls = self.nested_formset_class

		class _TemplateFormSet(parent_cls):
			"""Nested formset whose empty_form uses __nested__ placeholder."""

			@property
			def empty_form(self):
				form = self.form(
					auto_id=self.auto_id,
					prefix=self.add_prefix('__nested__'),
					empty_permitted=True,
					use_required_attribute=False,
					**self.get_form_kwargs(None),
					renderer=self.renderer,
				)
				self.add_fields(form, None)
				return form

		empty = BaseFormSet.empty_form.fget(self)
		empty.nested = _TemplateFormSet(prefix=empty_prefix)
		self._cached_empty = empty

	# ── Validation cascades into nested formsets ─────────────────────────
	def is_valid(self):
		result = super().is_valid()
		for form in self.forms:
			if not hasattr(form, 'nested'):
				continue
			if (
				self.can_delete
				and hasattr(form, 'cleaned_data')
				and self._should_delete_form(form)
			):
				continue
			if not form.nested.is_valid():
				result = False
		return result

	# ── Save cascades into nested formsets ───────────────────────────────
	def save(self, commit=True):
		result = super().save(commit=commit)
		for form in self.forms:
			if not hasattr(form, 'nested'):
				continue
			if (
				self.can_delete
				and hasattr(form, 'cleaned_data')
				and self._should_delete_form(form)
			):
				continue
			if form.instance.pk:
				form.nested.instance = form.instance
				form.nested.save(commit=commit)
		return result
