from django import template
from django.templatetags.static import static
from django.utils.html import format_html

register = template.Library()


def _crm_assets():
	# Optimization: whilst the script has no behaviour outside of debug mode,
	# don't include it.

	return format_html(
		'<script src="{}" defer></script>',
		static('octopus_crm/octopus.js'),
	)


@register.simple_tag(takes_context=True)
def octopus_crm_js_assets(context):
	return _crm_assets()
