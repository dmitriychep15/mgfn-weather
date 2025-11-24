"""Common response models for API's."""

from urllib.parse import quote

from fastapi import status, Response
from pydantic import BaseModel, Field


class HTTPError(BaseModel):
    """Model of HTTP errors' responses for openapi.json."""

    detail: str = Field(description="Error message")


possible_error_codes = (
    status.HTTP_400_BAD_REQUEST,
    status.HTTP_404_NOT_FOUND,
    status.HTTP_500_INTERNAL_SERVER_ERROR,
    status.HTTP_503_SERVICE_UNAVAILABLE,
)
common_responses = {code: {"model": HTTPError} for code in possible_error_codes}


file_responses = {
    200: {
        "description": "Success",
        "content": {
            "application/octet-stream": {
                "schema": {"type": "string", "format": "binary"}
            },
        },
    }
}


def get_file_response(file: bytes, file_name: str) -> Response:
    """Returns API response for file."""
    return Response(
        file,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'''attachment; filename="{quote(file_name, encoding="utf-8")}"'''
        },
    )
