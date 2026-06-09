
# Tables for the accounts app.
import django_tables2 as tables
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.core.columns import (
	ActionColumn,
	CustomCheckBoxColumn,
	ManyToManyBadgeColumn,
)

User = get_user_model()


class UserHTMxTable(tables.Table):
	checked_row = CustomCheckBoxColumn(accessor='pk', orderable=False)
	counter = tables.TemplateColumn(
		'{{ row_counter|add:1 }}', orderable=False, verbose_name='N°'
	)
	email = tables.Column(
		accessor='email', verbose_name=_('Email'), orderable=True, linkify=True
	)
	full_name = tables.Column(
		accessor='full_name',
		verbose_name=_('Nom complet'),
		orderable=True,
		linkify=True,
	)

	tags = ManyToManyBadgeColumn(
		accessor='tags',
		verbose_name=_('Tags'),
		separator=' ',
		orderable=True,
		attrs={'td': {'class': 'w-300px p-2 vertical-align-middle'}},
	)
	actions = ActionColumn()

	class Meta:
		fields = (
			'checked_row',
			'counter',
			'full_name',
			'email',
			'tags',
			'is_active',
			'is_staff',
			'actions',
		)
		model = User
		template_name = 'tables/bootstrap_htmx.html'
