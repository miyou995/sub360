from django.forms.renderers import TemplatesSetting


class CustomFormRenderer(TemplatesSetting):
	field_template_name = 'forms/field.html'
