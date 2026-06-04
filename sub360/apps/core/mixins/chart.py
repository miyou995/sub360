import logging
from datetime import datetime, timedelta

from django.contrib.auth.decorators import permission_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import View

logger = logging.getLogger(__name__)


class ChartMixin(View):
	model = None
	field_to_aggregate = None
	date_field = 'created_at'
	group_by_field = None
	aggregate_function = Sum
	permission = None
	template_name = 'snippets/chart_graph.html'
	chart_id = 'chart'
	chart_title = 'Chart'
	chart_type = 'bar'

	def get_queryset(self):
		if not self.model:
			raise ValueError('ChartMixin: model must be defined')
		return self.model.objects.all()

	def filter_by_date_range(self, queryset, start_date, end_date):
		if start_date and end_date:
			try:
				start = datetime.strptime(start_date, '%Y-%m-%d')
				end = (
					datetime.strptime(end_date, '%Y-%m-%d')
					+ timedelta(days=1)
					- timedelta(seconds=1)
				)
				return queryset.filter(**{f'{self.date_field}__range': [start, end]})
			except ValueError:
				logger.error(f'Invalid date format: {start_date}, {end_date}')
		return queryset

	def get_monthly_data(self, queryset):
		if not self.field_to_aggregate:
			raise ValueError('ChartMixin: field_to_aggregate must be set on the view.')
		current_year = timezone.now().year
		all_months = [datetime(current_year, month, 1) for month in range(1, 13)]
		monthly_counts = {month: 0.0 for month in all_months}
		try:
			monthly_data = (
				queryset.annotate(month=TruncMonth(self.date_field))
				.values('month')
				.annotate(total=self.aggregate_function(self.field_to_aggregate))
				.order_by('month')
			)
			for item in monthly_data:
				month_date = item['month']
				if month_date and month_date.year == current_year:
					monthly_counts[datetime(current_year, month_date.month, 1)] = float(
						item['total'] or 0
					)
		except Exception as e:
			logger.error(f'Monthly data aggregation error: {e}')
			raise
		return [month.strftime('%B') for month in all_months], [
			monthly_counts[m] for m in all_months
		]

	def get_grouped_data(self, queryset):
		if not self.group_by_field:
			raise ValueError(
				'ChartMixin: group_by_field must be defined for non-monthly charts'
			)
		try:
			counts = {}
			for item in queryset.values(self.group_by_field).annotate(
				total=self.aggregate_function(self.field_to_aggregate)
			):
				counts[item[self.group_by_field] or 'Unknown'] = item['total']
			return list(counts.keys()), [float(v) for v in counts.values()]
		except Exception as e:
			logger.error(f'Grouped data aggregation error: {e}')
			raise

	def get_context_data(self, labels, chart_data):
		return {
			'chart_labels': labels,
			'chart_data': chart_data,
			'id': self.chart_id,
			'title': self.chart_title,
			'chart_type': self.chart_type,
			'total': sum(chart_data),
			'room_totals': labels,
		}

	def get(self, request, *args, **kwargs):
		if self.permission:
			self.get = permission_required(self.permission)(self.get)
		try:
			queryset = self.filter_by_date_range(
				self.get_queryset(),
				request.GET.get('start_date'),
				request.GET.get('end_date'),
			)
			if self.group_by_field:
				labels, chart_data = self.get_grouped_data(queryset)
			else:
				labels, chart_data = self.get_monthly_data(queryset)
			return render(
				request, self.template_name, self.get_context_data(labels, chart_data)
			)
		except Exception as e:
			logger.error(f'Chart rendering error: {e}')
			raise
