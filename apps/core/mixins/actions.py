import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.views.generic.edit import FormView

from apps.core.mixins._helpers import htmx_trigger_response
from apps.core.mixins.permissions import AutoPermissionMixin

logger = logging.getLogger(__name__)

_NO_ROWS_TRIGGERS = {'closeModal': 'kt_modal', 'refresh_table': True}
_SUCCESS_TRIGGERS = {'refresh_table': None, 'closeModal': 'kt_modal'}


class BaseActionView(AutoPermissionMixin, FormView):
	htmx_additional_event = None
	model = None
	template_name = 'snippets/_actions_modal.html'
	form_class = None
	parent_url_kwarg = None
	action_class_method = None

	def get_parent_object(self):
		if self.parent_url_kwarg:
			return get_object_or_404(self.model, pk=self.kwargs.get(self.parent_url_kwarg))
		return None

	def get_selected_items(self, method='GET'):
		data = self.request.GET if method == 'GET' else self.request.POST
		return self.model.objects.filter(id__in=data.getlist('selected_rows'))

	def get_form_kwargs(self):
		kwargs = {}
		parent = self.get_parent_object()
		if parent:
			kwargs['parent'] = parent
		if self.request.method in ('POST', 'PUT'):
			kwargs.update({'data': self.request.POST, 'files': self.request.FILES})
		return kwargs

	def process_action(self):
		raise NotImplementedError('You must define `process_action` method in your view.')

	def get(self, request, *args, **kwargs):
		items = self.get_selected_items('GET')
		if not items.exists():
			messages.warning(request, 'Vous devez sélectionner au moins une ligne')
			return htmx_trigger_response(204, _NO_ROWS_TRIGGERS)
		return self.render_to_response(self.get_context_data())

	def post(self, request, *args, **kwargs):
		items = self.get_selected_items('POST')
		if not items.exists():
			messages.warning(request, 'Vous devez sélectionner au moins une ligne')
			return htmx_trigger_response(204, _NO_ROWS_TRIGGERS)

		result = self.process_action()
		if result is not None and result.get('errors'):
			messages.error(self.request, result['errors'])
			return render(
				request,
				self.template_name,
				{'form': self.form_class(request.POST), 'selected_items': items},
			)

		messages.success(self.request, result['success'])
		return htmx_trigger_response(200, _SUCCESS_TRIGGERS)
