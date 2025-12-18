"""DynamoFL Remote Model"""
import shortuuid

from ..entities.model import RemoteModelEntity
from ..models.model import Model
from ..Request import _Request

try:
    from typing import Optional
except ImportError:
    from typing_extensions import Optional


class RemoteModel(Model):
    """RemoteModel

    NOTE: Remote model creation flow has changed.
    - First create auth_data for your cloud provider (e.g., OpenAI, Azure) using the SDK's auth_data APIs.
    - Then create a REMOTE model by providing authDataIds and a primaryAuthDataId in the config.
    - Direct API keys (apiKey) should not be sent on model creation; the server resolves keys from auth_data.
    """

    def __init__(
        self,
        request,
        name: str,
        key: str,
        model_id: str,
        config,
    ) -> None:
        self.request = request
        super().__init__(
            request=request,
            name=name,
            key=key,
            config=config,
            model_type="REMOTE",
            model_id=model_id,
        )

    @staticmethod
    def create(
        request: _Request,
        name: str,
        key: str,
        config: object,
    ) -> RemoteModelEntity:
        """Create the ML model and return its entity.

        IMPORTANT:
        - For REMOTE cloud providers (non-custom), config MUST include:
          - authDataIds: List[int] (non-empty)
          - primaryAuthDataId: int (must be one of authDataIds)
        - Do NOT include apiKey in config; the server validates and injects API keys using auth_data.
        - See server-side validation in create-ml-model.dto.ts and ml-model.service.ts.
        """
        model_id = Model.create_ml_model_and_get_id(
            request=request, name=name, key=key, model_type="REMOTE", config=config, size=None
        )
        return RemoteModelEntity(
            id=model_id,
            name=name,
            key=key,
            config=config,
            api_host=request.host,
        )

    @staticmethod
    def create_azure_model(
        request: _Request,
        name: str,
        api_instance: str,
        model_endpoint: str,
        auth_data_ids: list[int],
        primary_auth_data_id: int,
        api_version: Optional[str] = None,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        """Create an Azure REMOTE model.

        NOTE:
        - New flow requires authDataIds and primaryAuthDataId in config. API keys should be managed via auth_data.
        """
        config = {
            "remoteModelApiProvider": "azure",
            "remoteModelApiInstance": api_instance,
            "remoteModelEndpoint": model_endpoint,
            "apiVersion": api_version,
            "authDataIds": auth_data_ids,
            "primaryAuthDataId": primary_auth_data_id,
        }

        model_entity_key = shortuuid.uuid() if not key else key

        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)

    @staticmethod
    def create_lambdalabs_model(
        request: _Request,
        name: str,
        api_instance: str,
        model_endpoint: str,
        auth_data_ids: list[int],
        primary_auth_data_id: int,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        """Create a LambdaLabs REMOTE model.

        NOTE:
        - Provide authDataIds and primaryAuthDataId in config; do not pass apiKey directly to the server.
        """
        config = {
            "remoteModelApiProvider": "lambdalabs",
            "remoteModelApiInstance": api_instance,
            "remoteModelEndpoint": model_endpoint,
            "authDataIds": auth_data_ids,
            "primaryAuthDataId": primary_auth_data_id,
        }
        model_entity_key = shortuuid.uuid() if not key else key

        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)

    @staticmethod
    def create_openai_model(
        request: _Request,
        name: str,
        api_instance: str,
        auth_data_ids: list[int],
        primary_auth_data_id: int,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        """Create an OpenAI REMOTE model.

        NOTE:
        - Required on server: authDataIds and primaryAuthDataId. API key is sourced from auth_data.
        """
        config = {
            "remoteModelApiProvider": "openai",
            "remoteModelApiInstance": api_instance,
            "authDataIds": auth_data_ids,
            "primaryAuthDataId": primary_auth_data_id,
        }
        model_entity_key = shortuuid.uuid() if not key else key

        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)

    @staticmethod
    def create_anthropic_model(
        request: _Request,
        name: str,
        api_instance: str,
        auth_data_ids: list[int],
        primary_auth_data_id: int,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        """Create an Anthropic REMOTE model.

        NOTE:
        - authDataIds and primaryAuthDataId are mandatory on server for REMOTE providers.
        - Avoid sending apiKey directly; use auth_data entries instead.
        """
        config = {
            "remoteModelApiProvider": "anthropic",
            "remoteModelApiInstance": api_instance,
            "authDataIds": auth_data_ids,
            "primaryAuthDataId": primary_auth_data_id,
        }
        model_entity_key = shortuuid.uuid() if not key else key

        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)

    @staticmethod
    def create_gemini_model(
        request: _Request,
        name: str,
        api_instance: str,
        auth_data_ids: list[int],
        primary_auth_data_id: int,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        """Create a Gemini REMOTE model.

        NOTE:
        - Use auth_data-first flow: include authDataIds and primaryAuthDataId in config.
        """
        config = {
            "remoteModelApiProvider": "gemini",
            "remoteModelApiInstance": api_instance,
            "authDataIds": auth_data_ids,
            "primaryAuthDataId": primary_auth_data_id,
        }
        model_entity_key = shortuuid.uuid() if not key else key

        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)

    @staticmethod
    def create_bedrock_model(
        request: _Request,
        name: str,
        api_instance: str,
        auth_data_ids: list[int],
        primary_auth_data_id: int,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        """Create an AWS Bedrock REMOTE model.

        NOTE:
        - New flow requires authDataIds and primaryAuthDataId (do not send apiKey directly).
        """
        config = {
            "remoteModelApiProvider": "bedrock",
            "remoteModelApiInstance": api_instance,
            "authDataIds": auth_data_ids,
            "primaryAuthDataId": primary_auth_data_id,
        }
        model_entity_key = shortuuid.uuid() if not key else key

        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)

    @staticmethod
    def create_mistral_model(
        request: _Request,
        name: str,
        api_instance: str,
        auth_data_ids: list[int],
        primary_auth_data_id: int,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        """Create a Mistral REMOTE model.

        NOTE:
        - authDataIds and primaryAuthDataId must be supplied in config on server side.
        - Do not provide apiKey directly; use auth_data management.
        """
        config = {
            "remoteModelApiProvider": "mistral",
            "remoteModelApiInstance": api_instance,
            "authDataIds": auth_data_ids,
            "primaryAuthDataId": primary_auth_data_id,
        }
        model_entity_key = shortuuid.uuid() if not key else key

        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)

    @staticmethod
    def create_togetherai_model(
        request: _Request,
        name: str,
        api_instance: str,
        auth_data_ids: list[int],
        primary_auth_data_id: int,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        """Create a TogetherAI REMOTE model.

        NOTE:
        - Server requires authDataIds and primaryAuthDataId for non-custom REMOTE providers.
        - Keys are resolved from auth_data; do not send apiKey directly.
        """
        config = {
            "remoteModelApiProvider": "togetherai",
            "remoteModelApiInstance": api_instance,
            "authDataIds": auth_data_ids,
            "primaryAuthDataId": primary_auth_data_id,
        }
        model_entity_key = shortuuid.uuid() if not key else key

        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)

    @staticmethod
    def create_databricks_model(
        request: _Request,
        name: str,
        model_endpoint: str,
        auth_data_ids: list[int],
        primary_auth_data_id: int,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        """Create a Databricks REMOTE model.

        NOTE:
        - Supply authDataIds and primaryAuthDataId in config (server enforces this).
        - apiKey should not be sent directly in config; it's retained here for legacy convenience.
        """
        config = {
            "remoteModelApiProvider": "databricks",
            "remoteModelEndpoint": model_endpoint,
            "authDataIds": auth_data_ids,
            "primaryAuthDataId": primary_auth_data_id,
        }
        model_entity_key = shortuuid.uuid() if not key else key
        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)

    @staticmethod
    def create_custom_model(
        request: _Request,
        name: str,
        remote_model_endpoint: str,
        remote_api_auth_config: dict,
        request_transformation_expression: Optional[str] = None,
        response_transformation_expression: Optional[str] = None,
        response_type: Optional[str] = "string",
        batch_size: Optional[int] = 1,
        multi_turn_support: Optional[bool] = True,
        enable_retry: Optional[bool] = False,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        """Create a Custom REMOTE model.

        NOTE:
        - Custom model flow is exempt from the authDataIds requirement.
        - Authentication, if any, should be provided via remoteApiAuthConfig and will be encrypted server-side.
        """
        config = {
            "remoteModelApiProvider": "custom_model",
            "remoteModelEndpoint": remote_model_endpoint,
            "remoteApiAuthConfig": remote_api_auth_config,
            "customApiLMConfig": {
                "request_transformation_expression": request_transformation_expression,
                "response_transformation_expression": response_transformation_expression,
                "response_type": response_type,
                "batch_size": batch_size,
                "multi_turn_support": multi_turn_support,
                "enable_retry": enable_retry,
            },
        }
        model_entity_key = shortuuid.uuid() if not key else key
        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)

    @staticmethod
    def create_guardrail_model(
        request: _Request,
        name: str,
        api_key: str,
        model_endpoint: str,
        policy_id: str,
        key: Optional[str] = None,
    ) -> RemoteModelEntity:
        config = {
            "remoteModelApiProvider": "guardrail",
            "remoteModelEndpoint": model_endpoint,
            "metadata": {
                "policy_id": policy_id,
            },
            "apiKey": api_key,
        }
        model_entity_key = shortuuid.uuid() if not key else key
        return RemoteModel.create(request=request, name=name, key=model_entity_key, config=config)
