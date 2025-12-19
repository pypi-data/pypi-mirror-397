from functools import wraps

from phantomwright_driver.async_api import Page as AsyncPage
from phantomwright_driver.sync_api import Page as SyncPage

def do_patch() -> None:
    """ Aysnc / Sync version of evaluate override"""
    _original_sync_evaluate = SyncPage.evaluate


    @wraps(_original_sync_evaluate)
    def _hooked_sync_evaluate(self, *args, **kwargs):
        # Ensure isolated_context defaults to False if not provided
        kwargs.setdefault("isolated_context", False)
        return _original_sync_evaluate(self, *args, **kwargs)


    SyncPage.evaluate = _hooked_sync_evaluate

    _original_sync_evaluate_handle = SyncPage.evaluate_handle


    @wraps(_original_sync_evaluate_handle)
    def _hooked_sync_evaluate_handle(self, *args, **kwargs):
        # Ensure isolated_context defaults to False if not provided
        kwargs.setdefault("isolated_context", False)
        return _original_sync_evaluate_handle(self, *args, **kwargs)


    SyncPage.evaluate_handle = _hooked_sync_evaluate_handle

    _original_async_evaluate = AsyncPage.evaluate


    @wraps(_original_async_evaluate)
    async def _hooked_async_evaluate(self, *args, **kwargs):
        # Ensure isolated_context defaults to False if not provided
        kwargs.setdefault("isolated_context", False)
        return await _original_async_evaluate(self, *args, **kwargs)


    AsyncPage.evaluate = _hooked_async_evaluate

    _original_async_evaluate_handle = AsyncPage.evaluate_handle


    @wraps(_original_async_evaluate_handle)
    async def _hooked_async_evaluate_handle(self, *args, **kwargs):
        # Ensure isolated_context defaults to False if not provided
        kwargs.setdefault("isolated_context", False)
        return await _original_async_evaluate_handle(self, *args, **kwargs)


    AsyncPage.evaluate_handle = _hooked_async_evaluate_handle
