from uuid import uuid4
from typing import Callable

from ids_peak_afl.ids_peak_afl import FinishedCallback, Controller

# A type alias for the unique ID generated for each registration
CallbackId = str

# A type alias for the function signature of a callback
CallbackFunction = Callable[[], None]


class ControllerFinishedCallback(FinishedCallback):
    """
    Manages the registration, unregistration, and execution of callbacks.

    .. seealso::
       :class:``ids_peak_afl.ids_peak_afl.FinishedCallback``
    """

    def __init__(self, controller: Controller):
        """
        Initializes the callback manager.

        :param controller: The controller instance to associate with.
        """
        super().__init__(controller)
        self._callbacks: dict[CallbackId, CallbackFunction] = {}
        self._controller = Controller

    def register(self, callback: CallbackFunction) -> CallbackId:
        """
        Registers a callback and returns a unique identifier for it.

        :param callback: The callback to register.
        :returns: A unique identifier for the registered callback.
        """
        # Generate a unique ID (UUID) for this registration
        callback_id: CallbackId = str(uuid4())
        self._callbacks[callback_id] = callback
        return callback_id

    def unregister(self, callback_id: CallbackId) -> bool:
        """
        Unregisters a callback using its unique identifier.

        :param callback_id: The unique identifier of the callback to remove.
        :returns: True if the callback was successfully removed,
                  False otherwise.
        """
        if callback_id in self._callbacks:
            del self._callbacks[callback_id]
            return True
        return False

    def callback(self) -> None:
        """
        Executes all registered callbacks.

        .. note::
           Exceptions raised by individual callbacks are caught and ignored.
        """
        for callback in self._callbacks.values():
            try:
                callback()
            except Exception:
                pass
