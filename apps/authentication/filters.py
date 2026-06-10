

import django_filters
from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from apps.core.abstract_forms import AbstractFilterForm

User = get_user_model()


class UserFilterSet(django_filters.FilterSet):
	query = django_filters.CharFilter(method='universal_search', label='Search')
	is_superuser = django_filters.BooleanFilter(
		field_name='is_superuser',
		method='choice_filters',
		label='Superuser',
		widget=forms.CheckboxInput(),
	)
	is_staff = django_filters.BooleanFilter(
		field_name='is_staff',
		method='choice_filters',
		label='Staff',
		widget=forms.CheckboxInput,
	)
	is_active = django_filters.BooleanFilter(
		field_name='is_active',
		method='choice_filters',
		label='Active',
		widget=forms.CheckboxInput,
	)

	class Meta:
		model = User
		fields = ['is_active', 'is_staff', 'is_superuser', 'groups']
		form = AbstractFilterForm

	def universal_search(self, queryset, name, value):
		if not value:
			return queryset

		return queryset.filter(
			Q(email__icontains=value)
			| Q(first_name__icontains=value)
			| Q(last_name__icontains=value)
		)

	def choice_filters(self, queryset, name, value):
		if self.data.get('is_superuser') == 'on':
			queryset = queryset.filter(is_superuser=True)

		if self.data.get('is_staff') == 'on':
			queryset = queryset.filter(is_staff=True)

		if self.data.get('is_active') == 'on':
			queryset = queryset.filter(is_active=True)
		return queryset.distinct()

