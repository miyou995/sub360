import json
import logging
from copy import deepcopy

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import NoReverseMatch
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from django.views.generic.edit import FormView
from django_htmx.http import HttpResponseClientRedirect

from apps.core.mixins._helpers import (
	get_modal_content_id,
	get_next_modal_id,
	htmx_trigger_response,
	normalize_modal_id,
)
from apps.core.mixins.permissions import AutoPermissionMixin

logger = logging.getLogger(__name__)


class BaseOptionsMixinView(View):
	"""Reload select/option lists after an inline create (HTMX)."""

	model = None
	template_name = 'snippets/options.html'

	def get(self, request, *args, **kwargs):
		options = self.model.objects.all()
		return render(request, self.template_name, {'options': options})


class BaseManageHtmxFormView(AutoPermissionMixin, FormView):
	template_name = 'snippets/_create_form.html'
	form_class = None
	model = None
	object = None
	success_message = ''
	hx_triggers = {}
	hx_get_triggers = {}
	parent_url_kwarg = ()
	extra_kwargs = {}
	permission_required = None
	dropzone_config = None

	def get(self, request, *args, **kwargs):
		self.object = self.get_object()
		return super().get(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		return super().post(request, *args, **kwargs)

	def get_object(self):
		pk = self.kwargs.get('pk')
		if pk and self.model:
			return self.model.objects.get(pk=pk)
		return None

	def render_to_response(self, context, **response_kwargs):
		response = super().render_to_response(context, **response_kwargs)
		triggers = deepcopy(self.hx_get_triggers)
		if self.request.htmx and self.request.method == 'GET':
			triggers['modal_resize'] = (
				self.model.modal_size()
				if self.model and hasattr(self.model, 'modal_size')
				else 'modal-lg mw-650px'
			)
			response['HX-Trigger'] = json.dumps(triggers)
		return response

	def get_current_modal_id(self):
		posted_modal_id = (
			self.request.POST.get('modal_id') if self.request.method == 'POST' else None
		)
		requested_modal_id = posted_modal_id or self.request.GET.get('modal_id')
		return normalize_modal_id(requested_modal_id)

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['instance'] = self.object
		kwargs['request'] = self.request
		for parent_url in self.parent_url_kwarg or []:
			if self.kwargs.get(parent_url):
				kwargs[parent_url] = self.kwargs.get(parent_url)
		for key, value in self.extra_kwargs.items():
			kwargs[key] = value

		current_modal_id = self.get_current_modal_id()
		next_modal_id = get_next_modal_id(current_modal_id)
		kwargs['modal_context'] = {
			'is_modal_context': True,
			'next_modal_id': next_modal_id,
			'next_modal_content_id': get_modal_content_id(next_modal_id),
		}
		return kwargs

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		if (
			self.model
			and hasattr(self.model, 'get_create_url')
			and callable(getattr(self.model, 'get_create_url'))
		):
			parent_kwargs = {
				k: self.kwargs[k]
				for k in (self.parent_url_kwarg or [])
				if k in self.kwargs
			}
			try:
				context['create_url'] = self.model.get_create_url(**parent_kwargs)
			except TypeError:
				context['create_url'] = self.model.get_create_url()

		if self.object:
			context[self.model.__name__.lower()] = self.object
			if hasattr(self.object, 'get_update_url') and callable(
				self.object.get_update_url
			):
				context['update_url'] = self.object.get_update_url()

		if 'formsets' not in context:
			context['formsets'] = self.get_formsets(instance=self.object)

		if self.dropzone_config:
			post_key = self.dropzone_config.get('post_key', 'uploaded_files')
			dz_model = self.dropzone_config.get('model')
			uploaded_ids = (
				self.request.POST.getlist(post_key)
				if self.request.method == 'POST'
				else []
			)
			context['dropzone_uploaded_ids'] = uploaded_ids
			context['dropzone_uploaded_files'] = (
				dz_model.objects.filter(id__in=uploaded_ids)
				if dz_model and uploaded_ids
				else []
			)
		current_modal_id = self.get_current_modal_id()
		context['modal_id'] = current_modal_id
		context['modal_content_id'] = get_modal_content_id(current_modal_id)
		context['form_verbose_name'] = (
			self.model._meta.verbose_name if self.form_class else None
		)
		return context

	# ------------------------------------------------------------------ formsets

	def get_formsets(self, instance=None):
		"""
		Override in subclasses to define formsets.
		Return a dict: {'prefix': FormSet(request.POST or None, instance=instance, prefix='prefix')}
		"""
		return {}

	def save_formsets(self, formsets):
		for formset in formsets.values():
			formset.save()

	def save_form_with_formsets(self, form, instance, formsets):
		with transaction.atomic():
			instance = form.save(commit=True)
			self.save_formsets(formsets)
			self.handle_dropzone(instance)
		return instance

	# ------------------------------------------------------------------ dropzone

	def handle_dropzone(self, instance):
		if not self.dropzone_config:
			return
		field_name = self.dropzone_config.get('field_name')
		dz_model = self.dropzone_config.get('model')
		post_key = self.dropzone_config.get('post_key', 'uploaded_files')
		uploaded_ids = self.request.POST.getlist(post_key)
		if not (uploaded_ids and field_name and dz_model):
			return
		queryset = dz_model.objects.filter(id__in=uploaded_ids)
		field = getattr(instance, field_name, None)
		if field is None:
			return
		if hasattr(field, 'add'):
			field.add(*queryset)
		else:
			for obj in queryset:
				setattr(obj, field_name, instance)
				obj.save()

	# ------------------------------------------------------------------ form hooks

	def form_valid(self, form):
		instance = form.save(commit=False)
		if not self.kwargs.get('pk') and hasattr(self.model, 'created_by'):
			instance.created_by = self.request.user

		formsets = self.get_formsets(instance=instance)
		if not all(fs.is_valid() for fs in formsets.values()):
			return self.form_invalid(form, formsets=formsets)

		instance = self.save_form_with_formsets(form, instance, formsets)

		if self.kwargs.get('pk'):
			messages.success(
				self.request,
				f'{self.model._meta.model_name} ' + _('mis à jour avec succès.'),
			)
		else:
			messages.success(
				self.request, f'{self.model._meta.model_name} ' + _('créé avec succès.')
			)

		if self.request.POST.get('reload_page'):
			return HttpResponseClientRedirect(self.request.META.get('HTTP_REFERER'))

		if self.request.htmx:
			triggers = deepcopy(self.hx_triggers)
			validated_modal_id = normalize_modal_id(
				self.request.POST.get('modal_id'), default=None
			)
			if validated_modal_id:
				triggers['closeModal'] = validated_modal_id
			if self.model:
				refresh_event = f'refresh_{self.model._meta.model_name}'
				triggers.setdefault(refresh_event, None)
			return htmx_trigger_response(204, triggers)

		return HttpResponseClientRedirect(self.request.META.get('HTTP_REFERER'))

	def _emit_form_errors(self, form, formsets=None):
		for field, errors in form.errors.items():
			for error in errors:
				if field == '__all__':
					messages.error(self.request, str(error))
				else:
					label = form.fields[field].label if field in form.fields else field
					messages.error(self.request, f'{label}: {error}')
		for formset in (formsets or {}).values():
			for error in formset.non_form_errors():
				messages.error(self.request, str(error))
			for formset_errors in formset.errors:
				for field, errors in formset_errors.items():
					for error in errors:
						messages.error(self.request, str(error))

	def form_invalid(self, form, formsets=None):
		self._emit_form_errors(form, formsets)
		render_formsets = formsets if formsets is not None else {}
		return self.render_to_response(
			self.get_context_data(form=form, formsets=render_formsets)
		)


class BaseManageHtmxPageFormView(BaseManageHtmxFormView):
	template_name = 'snippets/_create_form_page.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['is_modal_context'] = False
		return context

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['modal_context'] = {
			'is_modal_context': False,
			'next_modal_id': 'kt_modal',
			'next_modal_content_id': 'kt_modal_content',
		}
		return kwargs

	def form_invalid(self, form, formsets=None):
		self._emit_form_errors(form, formsets)

		if self.request.htmx:
			response = HttpResponse(status=204)
			response['HX-Redirect'] = self.request.path
			return response

		render_formsets = (
			formsets
			if formsets is not None
			else self.get_formsets(instance=self.object)
		)
		return self.render_to_response(
			self.get_context_data(form=form, formsets=render_formsets), status=400
		)

	def form_valid(self, form):
		instance = form.save(commit=False)
		if hasattr(self.model, 'created_by') and not self.kwargs.get('pk'):
			instance.created_by = self.request.user

		formsets = self.get_formsets(instance=instance)
		if not all(fs.is_valid() for fs in formsets.values()):
			return self.form_invalid(form, formsets=formsets)

		instance = self.save_form_with_formsets(form, instance, formsets)

		model_name = self.model._meta.model_name
		if self.kwargs.get('pk'):
			messages.success(
				self.request, f'{model_name} ' + _('mis à jour avec succès.')
			)
		else:
			messages.success(self.request, f'{model_name} ' + _('créé avec succès.'))

		action = self.request.POST.get('submit_action', 'save')

		if action == 'save_continue' and hasattr(instance, 'get_update_url'):
			try:
				return redirect(instance.get_update_url())
			except NoReverseMatch:
				if hasattr(instance, 'get_absolute_url'):
					return redirect(instance.get_absolute_url())
				logger.exception('Could not reverse update URL for %s', instance)

		if action == 'save_add_another' and hasattr(self.model, 'get_create_url'):
			return redirect(self.model.get_create_url())

		if hasattr(self.model, 'get_list_url'):
			return redirect(self.model.get_list_url())

		if hasattr(instance, 'get_absolute_url'):
			return redirect(instance.get_absolute_url())

		return redirect(self.request.META.get('HTTP_REFERER', '/'))


class BaseHtmxInlineCreateView(BaseManageHtmxFormView):
	hx_triggers = {}
