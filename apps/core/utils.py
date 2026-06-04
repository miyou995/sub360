from django.utils.text import slugify

days_mapping = {
	'MONDAY': 'LU',
	'TUESDAY': 'MA',
	'WEDNESDAY': 'ME',
	'THURSDAY': 'JE',
	'FRIDAY': 'VE',
	'SATURDAY': 'SA',
	'SUNDAY': 'DI',
}


def get_unique_slug(instance, field_name='name'):
	"""
	Generate a unique slug for the given instance based on the specified field.
	"""
	base_slug = slugify(getattr(instance, field_name), allow_unicode=True)

	#     "\n \n \n Generating unique slug for instance:",
	#     instance,
	#     "Base slug:",
	#     base_slug,
	# )

	existing_slugs = instance.__class__.objects.filter(
		slug__startswith=base_slug
	).values_list('slug', flat=True)

	# if base_slug not in existing_slugs:
	# return base_slug

	counter = 1
	unique_slug = f'{base_slug}-{counter}'

	while unique_slug in existing_slugs:
		counter += 1
		unique_slug = f'{base_slug}-{counter}'
	return unique_slug
