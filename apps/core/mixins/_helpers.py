import json
import logging

from django.contrib.admin.utils import NestedObjects
from django.db import router
from django.http import HttpResponse
from django.utils.text import capfirst

logger = logging.getLogger(__name__)

# Ordered stacked-modal ids. Level 0 is the base modal; each inline-create
# opens the next level. 3 levels covers all realistic nesting scenarios.
MODAL_STACK = ['kt_modal', 'kt_modal_stacked_2', 'kt_modal_stacked_3']


def normalize_modal_id(modal_id, default='kt_modal'):
	if modal_id in MODAL_STACK:
		return modal_id
	return default


def get_next_modal_id(current_modal_id):
	current_modal_id = normalize_modal_id(current_modal_id)
	current_idx = MODAL_STACK.index(current_modal_id)
	return MODAL_STACK[min(current_idx + 1, len(MODAL_STACK) - 1)]


def get_modal_content_id(modal_id):
	return f'{modal_id}_content'


def htmx_trigger_response(status: int, triggers: dict) -> HttpResponse:
	"""Return an HttpResponse with an HX-Trigger header built from a triggers dict."""
	return HttpResponse(status=status, headers={'HX-Trigger': json.dumps(triggers)})


def get_deleted_objects(objs):
	"""
	Find all objects related to ``objs`` that should also be deleted. ``objs``
	must be a homogeneous iterable of objects (e.g. a QuerySet).

	Return a nested list of strings suitable for display in the
	template with the ``unordered_list`` filter.
	"""
	try:
		obj = objs[0]
	except IndexError:
		return [], {}, set(), []
	else:
		using = router.db_for_write(obj._meta.model)
	collector = NestedObjects(using=using, origin=objs)
	collector.collect(objs)
	perms_needed = set()

	def format_callback(obj):
		opts = obj._meta
		return '%s: %s' % (capfirst(opts.verbose_name), obj)

	to_delete = collector.nested(format_callback)
	model_count = {
		model._meta.verbose_name_plural: len(objs)
		for model, objs in collector.model_objs.items()
	}
	protected = [format_callback(obj) for obj in collector.protected]
	return to_delete, model_count, perms_needed, protected
