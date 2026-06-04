import logging

from django.urls import NoReverseMatch

logger = logging.getLogger(__name__)


class BreadcrumbMixin:
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		model = self.model or self.get_queryset().model
		try:
			list_url = model.get_list_url() if hasattr(model, 'get_list_url') else None
			if list_url:
				context['parent_url'] = list_url
		except NoReverseMatch:
			pass

		detail_page = self.object if hasattr(self, 'object') else None
		context['page_title'] = (
			detail_page if detail_page else model._meta.verbose_name_plural
		)
		context['title'] = f'{context["page_title"]}'
		if detail_page:
			context['title'] = f'{model._meta.verbose_name} - {context["page_title"]}'
			context['parent_page'] = model._meta.verbose_name_plural
		return context
