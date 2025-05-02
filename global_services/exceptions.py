from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    # Let DRF generate the standard error response first
    response = exception_handler(exc, context)

    if response is not None:
        # If DRF handled it (e.g., ValidationError), format it nicely
        error_message = ""
        if isinstance(response.data, dict):
            for key, value in response.data.items():
                if isinstance(value, list) and value:
                    error_message = value[0]
                else:
                    error_message = str(value)
        else:
            error_message = str(response.data)

        return Response(
            {"error": error_message},
            status=response.status_code
        )

    # If DRF could not handle it, it's a server error (500)
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)

    return Response(
        {"error": "An unexpected error occurred. Please try again later."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def error_response(message, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({"error": message}, status=status_code)
