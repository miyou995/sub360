from django import forms
from django.forms.utils import flatatt
from django.forms.widgets import TextInput
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


class QuillWidget(forms.Widget):
	"""
	A rich-text widget backed by Quill 2.x.
	Renders a hidden <textarea> (for form data) and a <div> for the Quill editor.
	Quill JS/CSS are loaded via the Media class from the project static files.
	"""

	class Media:
		css = {'all': ('apps/quill.snow.css',)}
		js = ('apps/quill.js', 'apps/quill_widget.js')

	def render(self, name, value, attrs=None, renderer=None):
		attrs = attrs or {}
		textarea_id = attrs.get('id', f'id_{name}')
		editor_id = f'quill_editor_{textarea_id}'
		safe_value = escape(value or '')
		textarea_attrs = {
			'id': textarea_id,
			'name': name,
			'style': 'display:none;',
			'class': 'quill-hidden-input',
		}
		editor_attrs = {
			'id': editor_id,
			'class': 'quill-editor-container',
			'data-textarea-id': textarea_id,
		}

		html = (
			f'<textarea{flatatt(textarea_attrs)}>{safe_value}</textarea>'
			f'<div{flatatt(editor_attrs)}></div>'
		)
		return mark_safe(html)

	def value_from_datadict(self, data, files, name):
		return data.get(name)


class BooleanAllSelect(forms.Select):
	def __init__(self, *args, **kwargs):
		choices = [('', _('Tout')), ('true', _('Oui')), ('false', _('Non'))]
		super().__init__(
			attrs={
				'class': 'form-select filter-select',
				'data-control': 'select2',
				'data-hide-search': 'true',
			},
			choices=choices,
			*args,
			**kwargs,
		)


class CreatableSelect(forms.Select):
	"""
	A Tom Select widget that allows creating new options on the fly.

	Usage:
	    widget = CreatableSelect(
	        attrs={
	            "class": "form-select form-control form-control-solid",
	            "placeholder": _("Select or create..."),
	        }
	    )
	"""

	def __init__(
		self,
		*args,
		hx_endpoint='',
		hx_trigger_name=None,
		**kwargs,
	):
		self.hx_endpoint = hx_endpoint
		self.hx_trigger_name = hx_trigger_name or 'refresh-options'
		super().__init__(*args, **kwargs)

	def render(self, name, value, attrs=None, renderer=None):
		# Add Tom Select classes and data attributes
		attrs = attrs or {}
		# Build class string
		class_parts = []
		if 'class' in attrs:
			class_parts.append(attrs['class'])
		class_parts.extend(
			['tom-select', 'form-select', 'form-control', 'form-control-solid']
		)
		attrs['class'] = ' '.join(class_parts)

		# Add data attributes for Tom Select
		attrs['data-create'] = 'true'
		attrs['data-allow-empty'] = 'true'

		return super().render(name, value, attrs, renderer)


class RichSelect(forms.Select):
	"""
	A Select widget that adds data-kt-rich-content-* attributes to each <option>
	based on the model instance.
	"""

	def __init__(
		self, *args, data_icon_field=None, data_subcontent_field=None, **kwargs
	):
		self.data_icon_field = data_icon_field
		self.data_subcontent_field = data_subcontent_field
		super().__init__(*args, **kwargs)

	def create_option(
		self, name, value, label, selected, index, subindex=None, attrs=None
	):
		option_dict = super().create_option(
			name,
			value,
			label,
			selected,
			index,
			subindex=subindex,
			attrs=attrs,
		)

		# only proceed if this is a ModelChoiceField
		if hasattr(self.choices, 'queryset') and value:
			# try to get the actual model instance
			instance = None

			if hasattr(value, 'instance'):
				instance = value.instance
			else:
				# fallback: extract raw PK and re-fetch
				raw_pk = getattr(value, 'value', value)
				try:
					instance = self.choices.queryset.get(pk=raw_pk)
				except Exception:
					instance = None

			if instance:
				if self.data_subcontent_field:
					sub = getattr(instance, self.data_subcontent_field, '')
					option_dict['attrs']['data-kt-rich-content-subcontent'] = sub
				if self.data_icon_field:
					icon = getattr(instance, self.data_icon_field, '')
					option_dict['attrs']['data-kt-rich-content-icon'] = icon

		return option_dict


class SwitchWidget(forms.CheckboxInput):
	"""A custom CheckboxInput widget styled as a toggle switch, using the filter's label dynamically."""

	def __init__(self, *args, **kwargs):
		attrs = kwargs.get('attrs', {})
		attrs.update({'class': 'form-check-input'})
		super().__init__(attrs=attrs, *args, **kwargs)
		# Label will be set dynamically in render based on filter context
		self.filter_label = None

	def render(self, name, value, attrs=None, renderer=None):
		"""Render the switch widget with the filter's label."""
		# Get the base checkbox HTML
		checkbox_html = super().render(name, value, attrs, renderer)

		# Determine if the checkbox is checked
		# is_checked = bool(value) if value is not None else False

		# Use the filter's label if available, fallback to a default
		label_text = self.filter_label or _('Changer')

		# Append " (On)" or " (Off)" to indicate state

		# Render the switch HTML
		return format_html(
			'<label class="form-check form-switch form-check-custom form-check-solid">'
			'{}'
			'<span class="form-check-label fw-semibold text-muted me-2">{}</span>'
			'</label>',
			checkbox_html,
			label_text,
		)


class StatusAllSelect(forms.Select):
	def __init__(self, *args, **kwargs):
		super().__init__(
			attrs={
				'class': 'form-select filter-select',
				'data-control': 'select2',
				'data-hide-search': 'true',
			},
			*args,
			**kwargs,
		)


class PasswordMeterWidget(forms.PasswordInput):
	"""
	A PasswordInput widget that renders the full Metronic password-meter
	structure, including the visibility toggle and score highlights.

	Usage::

	    password = forms.CharField(widget=PasswordMeterWidget())
	"""

	is_password_meter = True

	def __init__(self, attrs=None):
		default_attrs = {'class': 'form-control bg-transparent', 'autocomplete': 'off'}
		if attrs:
			default_attrs.update(attrs)
		super().__init__(attrs=default_attrs)

	def render(self, name, value, attrs=None, renderer=None):
		input_html = super().render(name, value, attrs, renderer)
		return format_html(
			'<div class="mb-1" data-kt-password-meter="true">'
			'<div class="position-relative mb-3">'
			'{}'
			'<span class="btn btn-sm btn-icon position-absolute translate-middle top-50 end-0 me-n2"'
			' data-kt-password-meter-control="visibility">'
			'<i class="ki-outline ki-eye-slash fs-2"></i>'
			'<i class="ki-outline ki-eye fs-2 d-none"></i>'
			'</span>'
			'</div>'
			'<div class="d-flex align-items-center mb-3" data-kt-password-meter-control="highlight">'
			'<div class="flex-grow-1 bg-secondary bg-active-success rounded h-5px me-2"></div>'
			'<div class="flex-grow-1 bg-secondary bg-active-success rounded h-5px me-2"></div>'
			'<div class="flex-grow-1 bg-secondary bg-active-success rounded h-5px me-2"></div>'
			'<div class="flex-grow-1 bg-secondary bg-active-success rounded h-5px"></div>'
			'</div>'
			'</div>',
			input_html,
		)


class MultipleFileInput(forms.ClearableFileInput):
	allow_multiple_selected = True


class MultipleFileField(forms.FileField):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault('widget', MultipleFileInput())
		super().__init__(*args, **kwargs)

	def clean(self, data, initial=None):
		single_file_clean = super().clean
		if isinstance(data, (list, tuple)):
			result = [single_file_clean(d, initial) for d in data]
		else:
			result = [single_file_clean(data, initial)]
		return result


class DialerWidget(TextInput):
	def __init__(
		self, attrs=None, currency=True, min_val=1, max_val=24, step=1, prefix=''
	):
		default_attrs = {
			'data-kt-dialer': 'true',
			'data-kt-dialer-currency': str(currency).lower(),
			'data-kt-dialer-min': min_val,
			'data-kt-dialer-max': max_val,
			'data-kt-dialer-step': step,
			'data-kt-dialer-prefix': prefix,
			'readonly': 'readonly',
			'class': 'form-control',
			'data-kt-dialer-control': 'input',
		}
		if attrs:
			default_attrs.update(attrs)
		super().__init__(default_attrs)

	def render(self, name, value, attrs=None, renderer=None):
		# Render the normal input box
		input_html = super().render(name, value or 1, attrs, renderer)

		# Wrap it inside the custom dialer HTML
		html = f"""
        <div class="input-group w-md-300px"
             data-kt-dialer="true"
             data-kt-dialer-currency="{self.attrs.get('data-kt-dialer-currency')}"
             data-kt-dialer-min="{self.attrs.get('data-kt-dialer-min')}"
             data-kt-dialer-max="{self.attrs.get('data-kt-dialer-max')}"
             data-kt-dialer-step="{self.attrs.get('data-kt-dialer-step')}"
             data-kt-dialer-prefix="{self.attrs.get('data-kt-dialer-prefix')}">

            <button class="btn btn-icon btn-outline btn-active-color-primary"
                    type="button" data-kt-dialer-control="decrease">
                <i class="ki-duotone ki-minus fs-2"></i>
            </button>

            {input_html}

            <button class="btn btn-icon btn-outline btn-active-color-primary"
                    type="button" data-kt-dialer-control="increase">
                <i class="ki-duotone ki-plus fs-2"></i>
            </button>
        </div>
        """
		return mark_safe(html)
