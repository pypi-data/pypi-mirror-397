"""DynamoFL Model"""
import logging

from ..Request import _Request

try:
    from typing import Optional
except ImportError:
    from typing_extensions import Optional


class Model:
    """Model"""

    def __init__(  # pylint: disable=dangerous-default-value
        self,
        request,
        name: str,
        key: str,
        model_type: str,
        model_id: Optional[str] = None,
        config: object = {},
    ) -> None:
        self.key = key
        self.name = name
        self.config = config
        self.request = request
        self.type = model_type
        self.logger = logging.getLogger("Model")
        self.id = model_id

    @staticmethod
    def create_ml_model_and_get_id(
        request: _Request,
        name: str,
        key: str,
        model_type: str,
        config,
        size: Optional[int] = None,
    ):
        """Create an ML model and return its id.

        Remote Model Creation (IMPORTANT):
        - For REMOTE cloud providers (non-custom), the server requires:
          - config.authDataIds: List[int] (non-empty)
          - config.primaryAuthDataId: int (must be a member of authDataIds)
        - Do not include plaintext api keys in config. The server validates and injects provider API keys
          using the referenced auth_data entries.
        - For CUSTOM_MODEL provider, authDataIds are not required; use remoteApiAuthConfig as applicable.
        """
        params = {
            "key": key,
            "name": name,
            "config": config,
            "type": model_type,
            "size": size,
        }
        created_model = request._make_request(  # pylint: disable=protected-access
            "POST", "/ml-model", params=params
        )
        return created_model["_id"]
