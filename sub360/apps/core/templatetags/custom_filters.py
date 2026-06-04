from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
	try:
		return float(value) * float(arg)
	except (ValueError, TypeError):
		return 0


@register.filter
def divide(value, arg):
	try:
		return float(value) / float(arg)
	except (ValueError, TypeError, ZeroDivisionError):
		return 0


@register.filter
def format_attrs(attrs):
	"""
	Convert a dictionary of attributes to a string suitable for HTML attributes,
	excluding the 'class' attribute.
	"""
	# if not isinstance(attrs, dict) or not attrs:
	#     return ''
	attrs_dict = dict(attrs) if not isinstance(attrs, dict) else attrs
	return ' '.join(
		f'{key}="{value}"'
		for key, value in attrs_dict.items()
		if value is not None and key != 'class'
	)


@register.simple_tag
def get_verbose_field_name(instance, field_name):
	"""Returns verbose_name for a field of a model instance."""
	return instance._meta.get_field(field_name).verbose_name


@register.simple_tag
def get_model_verbose_name(model):
	"""Returns verbose_name for a model class."""
	return model._meta.verbose_name


@register.simple_tag
def format_change_state_url(lead, target_state):
	"""
	Format the URL for changing the state of a lead.
	"""
	return lead.get_change_state_url(target_state)


# @register.simple_tag
# def get_permission_required(self):
# 		return f'leads.change_{self._meta.model_name.lower()}'
	


@register.filter
def to_words(value):
	from apps.core.utils import number_to_words_fr

	try:
		return number_to_words_fr(float(value))
	except (ValueError, TypeError):
		return value


@register.simple_tag
def get_list_of_states():
	from apps.leads.models import State

	return State.objects.all()

@register.simple_tag
def get_list_of_bill_types():
	from apps.billing.models import BillTypeConfig
	return BillTypeConfig.objects.filter(is_active=True).order_by('ordering', 'label')
