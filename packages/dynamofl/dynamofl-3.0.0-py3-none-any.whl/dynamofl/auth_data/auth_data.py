"""High-level client for User Auth Data endpoints.

This module provides a typed, well-documented wrapper around the `/user-auth`
API routes implemented in the server (`user-auth-data.controller.ts`).

Usage example:
    from dynamofl.auth_data.auth_data import UserAuthData
    from dynamofl.Request import _Request
    from dynamofl.entities import ProviderTypeEnum

    req = _Request(token=..., host="https://api.example.com")
    created = UserAuthData.create_auth_data_cloud(
        request=req,
        name="Primary OpenAI",
        provider_type=ProviderTypeEnum.OPENAI,
        api_key="sk-...",
    )
    print(created.authId, created.name)
"""
from __future__ import annotations

from typing import Dict, List, Optional

from ..entities.auth_data import AuthTypeEnum as AuthDataAuthTypeEnum
from ..entities.auth_data import (
    DeleteAuthDataResponseEntity,
    GetAuthDataByIdEntity,
    GetUserLevelAuthDataAndModelAssociationEntity,
    ProviderTypeEnum,
    UpdateAuthMappingsOnAuthDataResponseEntity,
    UserAuthDataRecordEntity,
)
from ..Request import _Request


class UserAuthData:
    """Client wrapper for User Auth Data APIs."""

    @staticmethod
    def get_user_level_auth_data_and_model_association(
        request: _Request,
        auth_type: Optional[AuthDataAuthTypeEnum] = None,
        provider_type: Optional[ProviderTypeEnum] = None,
    ) -> GetUserLevelAuthDataAndModelAssociationEntity:
        """Fetch user's auth-data grouped by provider along with AI system mappings.

        Mirrors:
            GET /user-auth/auth-data-and-model-association

        Args:
            request: Authenticated request client.
            auth_type: Optional filter for auth type (REMOTE_CLOUD or REMOTE_CUSTOM).
            provider_type: Optional provider filter (e.g., openai, azure).

        Returns:
            Parsed GetUserLevelAuthDataAndModelAssociationEntity.
        """
        params: Dict[str, str] = {}
        if auth_type:
            params["authType"] = str(auth_type.value)
        if provider_type:
            params["providerType"] = str(provider_type.value)
        resp = request._make_request(  # pylint: disable=protected-access
            "GET", "/user-auth/auth-data-and-model-association", params=params
        )
        return GetUserLevelAuthDataAndModelAssociationEntity.from_dict(resp)

    @staticmethod
    def get_auth_data_by_id(request: _Request, auth_id: int) -> GetAuthDataByIdEntity:
        """Fetch a single auth_data row and its AI system mappings for the user.

        Mirrors:
            GET /user-auth/auth-data/:authId
        """
        resp = request._make_request(  # pylint: disable=protected-access
            "GET", f"/user-auth/auth-data/{int(auth_id)}"
        )
        return GetAuthDataByIdEntity.from_dict(resp)

    @staticmethod
    def delete_auth_data_by_id(request: _Request, auth_id: int) -> DeleteAuthDataResponseEntity:
        """Delete a user's auth_data row by authId.

        Mirrors:
            DELETE /user-auth/auth-data/:authId
        """
        resp = request._make_request(  # pylint: disable=protected-access
            "DELETE", f"/user-auth/auth-data/{int(auth_id)}"
        )
        return DeleteAuthDataResponseEntity.from_dict(resp)

    @staticmethod
    def update_auth_mappings_on_auth_data(
        request: _Request,
        auth_id: int,
        ai_systems_to_add: Optional[List[str]] = None,
        ai_systems_to_remove: Optional[List[str]] = None,
    ) -> UpdateAuthMappingsOnAuthDataResponseEntity:
        """Add or remove AI system mappings for a given auth_data id.

        Mirrors:
            POST /user-auth/auth-data/:authId/mappings

        Args:
            request: Authenticated request client.
            auth_id: The auth_data id to update.
            ai_systems_to_add: Model ids to associate with this auth_data.
            ai_systems_to_remove: Model ids to remove association.
        """
        body: Dict[str, object] = {}
        if ai_systems_to_add:
            body["aiSystemsToAdd"] = list(ai_systems_to_add)
        if ai_systems_to_remove:
            body["aiSystemsToRemove"] = list(ai_systems_to_remove)
        resp = request._make_request(  # pylint: disable=protected-access
            "POST", f"/user-auth/auth-data/{int(auth_id)}/mappings", params=body
        )
        return UpdateAuthMappingsOnAuthDataResponseEntity.from_dict(resp)

    @staticmethod
    def create_auth_data_cloud(
        request: _Request,
        name: str,
        provider_type: ProviderTypeEnum,
        api_key: str,
    ) -> UserAuthDataRecordEntity:
        """Create a REMOTE_CLOUD auth_data row with a single API key.

        Mirrors:
            POST /user-auth/auth-data
        """
        body = {
            "authType": AuthDataAuthTypeEnum.REMOTE_CLOUD.value,
            "providerType": provider_type.value,
            "name": name,
            "authConfig": {"apiKey": api_key},
        }
        resp = request._make_request(  # pylint: disable=protected-access
            "POST", "/user-auth/auth-data", params=body
        )
        return UserAuthDataRecordEntity.from_dict(resp)

    @staticmethod
    def edit_auth_data(
        request: _Request,
        auth_id: int,
        name: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> UserAuthDataRecordEntity:
        """Edit a user's REMOTE_CLOUD auth_data name and/or API key.

        Mirrors:
            POST /user-auth/auth-data/:authId
        """
        body: Dict[str, object] = {}
        if name is not None:
            body["name"] = name
        if api_key is not None:
            body["authConfig"] = {"apiKey": api_key}
        resp = request._make_request(  # pylint: disable=protected-access
            "POST", f"/user-auth/auth-data/{int(auth_id)}", params=body
        )
        return UserAuthDataRecordEntity.from_dict(resp)
