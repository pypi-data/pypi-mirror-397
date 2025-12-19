from typing import Any, Dict


class MockUdfInput:
    def __init__(self, data: Any, as_kwargs: bool = False) -> None:
        """
        Mock input for UDF execution.

        Args:
            data: The input data
            as_kwargs: If True and data is a dict, pass it through as kwargs directly.
                      If False (default), wrap data in "bounds" parameter (for tile/bbox).
        """
        self._data = data
        self._as_kwargs = as_kwargs

    def as_udf_args(self) -> Dict[str, Any]:
        if self._as_kwargs and isinstance(self._data, dict):
            # Pass through the dict as kwargs directly for input list processing
            return self._data
        else:
            # Original behavior for tile/bbox
            kwargs = {}
            if self._data is not None:
                kwargs["bounds"] = self._data
            return kwargs
