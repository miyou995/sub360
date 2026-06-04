from django.contrib.auth.mixins import PermissionRequiredMixin


class AutoPermissionMixin(PermissionRequiredMixin):
	"""
	Derives the required permission automatically from ``self.model``.

	- Set ``permission_action = 'delete'`` on delete views.
	- Leave ``permission_action = None`` on create/update views; the action is
	  auto-detected from the ``pk`` URL kwarg (``add`` when creating, ``change`` when updating).
	- Override ``permission_required`` directly for one-off custom permissions.
	"""

	permission_action = None  # 'add' | 'change' | 'delete', or None = auto-detect from pk
	permission_required = None

	def get_permission_required(self):
		if self.permission_required is not None:
			return (self.permission_required,)
		if not hasattr(self.model, '_meta'):
			return ()
		app = self.model._meta.app_label
		name = self.model._meta.model_name
		action = self.permission_action or ('change' if self.kwargs.get('pk') else 'add')
		return (f'{app}.{action}_{name}',)
