"""
StoreAutoMixin
==============
Inject ``request.store`` (set by ``StoreMiddleware``) onto the model
instance *before* the parent ``form_valid`` saves it.

Use this mixin on any create/update view whose model has a mandatory
``store`` FK that must be auto-set from the active session store —
never shown on the form.

Usage::

    class MyTransactionManageView(StoreAutoMixin, BaseManageHtmxFormView):
        model = MyTransaction
        form_class = MyTransactionForm
"""


class StoreAutoMixin:
	"""
	CBV mixin: sets ``form.instance.store`` from ``request.store`` before
	calling the parent ``form_valid``.  Works with both
	``BaseManageHtmxFormView`` and ``BaseManageHtmxPageFormView``.
	"""

	def form_valid(self, form):
		if self.request.store:
			form.instance.store = self.request.store
		return super().form_valid(form)
