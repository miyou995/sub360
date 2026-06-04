import json
import logging

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import ProtectedError, RestrictedError
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, View
from django_htmx.http import HttpResponseClientRedirect

from apps.core.mixins._helpers import get_deleted_objects, htmx_trigger_response
from apps.core.mixins.permissions import AutoPermissionMixin

logger = logging.getLogger(__name__)


class DeleteMixinHTMX(AutoPermissionMixin, DeleteView):
	template_name = 'snippets/htmx_delete_modal.html'
	htmx_additional_event = None
	permission_action = 'delete'

	def build_htmx_trigger_headers(self):
		trigger_dict = {'closeModal': 'delete_modal', 'refresh_table': None}
		if self.htmx_additional_event:
			if isinstance(self.htmx_additional_event, str):
				trigger_dict[self.htmx_additional_event] = None
			elif isinstance(self.htmx_additional_event, dict):
				trigger_dict.update(self.htmx_additional_event)
			else:
				raise ValueError('htmx_additional_event must be None, str, or dict')
		return {'HX-Trigger': json.dumps(trigger_dict)}

	@transaction.atomic()
	def post(self, request, *args, **kwargs):
		try:
			obj = self.get_object()
			is_detail_page = hasattr(
				obj, 'get_absolute_url'
			) and obj.get_absolute_url() in request.META.get('HTTP_REFERER', '')
			obj.delete()
			messages.success(
				self.request,
				f'{self.model._meta.model_name} ' + _('supprimé avec succès.'),
			)
			if is_detail_page and hasattr(self.model, 'get_list_url'):
				return HttpResponseClientRedirect(self.model.get_list_url())
			return HttpResponse(status=200, headers=self.build_htmx_trigger_headers())

		except (ProtectedError, RestrictedError, ValidationError) as exc:
			model_name = self.model._meta.model_name
			if isinstance(exc, ValidationError):
				error_text = ' '.join(exc.messages)
			else:
				error_text = _(
					f'Impossible de supprimer cet {model_name} : il est utilisé ailleurs.'
				)
			messages.error(request, error_text)
			return htmx_trigger_response(
				204,
				{
					'closeModal': 'delete_modal',
					'refresh_table': None,
					self.htmx_additional_event: None,
				},
			)

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, {'object': self.get_object()})


class BulkDeleteMixinHTMX(AutoPermissionMixin, View):
	permission_action = 'delete'
	htmx_additional_event = None
	model = None
	template_name = 'popups/select_row_delete_popup.html'

	def get_selected_items(self, method='GET'):
		data = self.request.GET if method == 'GET' else self.request.POST
		return self.model.objects.filter(id__in=data.getlist('selected_rows'))

	def get_context_data(self, **kwargs):
		context = {}
		context['model_name'] = self.model._meta.model_name if self.model else None
		queryset = self.get_selected_items()
		context['queryset'] = queryset
		to_delete, model_count, perms_needed, protected = get_deleted_objects(queryset)
		context['deleted_objects'] = [to_delete]
		context['model_count'] = dict(model_count).items()
		context['perms_lacking'] = perms_needed
		context['protected'] = protected
		return context

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, self.get_context_data())

	def post(self, request, *args, **kwargs):
		queryset = self.get_selected_items(method='POST')
		if queryset.exists():
			count = queryset.count()
			queryset.delete()
			messages.success(request, f'Supprimé avec succès {count} élément(s).')
			return htmx_trigger_response(
				204,
				{
					'refresh_table': None,
					'closeModal': 'kt_modal',
					self.htmx_additional_event: None,
				},
			)
		messages.warning(request, _('vous devez sélectionner au moins une ligne'))
		return HttpResponse(status=204)
