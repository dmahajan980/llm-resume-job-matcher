from typing import Any, Callable
import traceback


def wrap_tool_result(func: Callable) -> Any:
    """
    Wrap the result of a tool function in a JSON schema.
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            result = func(*args, **kwargs)
            return {
                "success": True,
                "data": result,
            }
        except Exception as e:
            error_message = str(e)
            error_type = type(e).__name__
            error_traceback = traceback.format_exc()

            return {
                "success": False,
                "error": {
                    "message": error_message,
                    "type": error_type,
                    "traceback": error_traceback,
                },
            }

    return wrapper
