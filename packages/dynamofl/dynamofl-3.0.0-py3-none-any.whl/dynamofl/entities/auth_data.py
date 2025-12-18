"""Auth Data entities for DynamoFL SDK.

These dataclasses model the request/response payloads used by the
`/user-auth` API on the server, keeping field names aligned with the
backend DTOs for clarity.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class AuthTypeEnum(str, Enum):
    """Authentication configuration type."""

    REMOTE_CLOUD = "REMOTE_CLOUD"
    REMOTE_CUSTOM = "REMOTE_CUSTOM"


class ProviderTypeEnum(str, Enum):
    """Supported provider types for remote cloud or custom models."""

    AZURE = "azure"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MISTRAL = "mistral"
    TOGETHERAI = "togetherai"
    LAMBDALABS = "lambdalabs"
    DATABRICKS = "databricks"
    BEDROCK = "bedrock"
    GEMINI = "gemini"
    CUSTOM_MODEL = "custom_model"


@dataclass
class AuthConfigRemoteCloudEntity:
    """Auth configuration for remote cloud providers.

    The API key is typically masked in responses.
    """

    apiKey: Optional[str] = None

    @staticmethod
    def from_dict(data: Optional[Dict[str, Any]]) -> "AuthConfigRemoteCloudEntity":
        data = data or {}
        return AuthConfigRemoteCloudEntity(apiKey=data.get("apiKey"))


@dataclass
class AiSystemMetadataEntity:
    """Subset of model metadata associated with an AI system mapping."""

    name: str
    key: str
    type: Optional[str] = None
    source: Optional[str] = None
    modelType: Optional[str] = None

    @staticmethod
    def from_dict(data: Optional[Dict[str, Any]]) -> Optional["AiSystemMetadataEntity"]:
        if not data:
            return None
        return AiSystemMetadataEntity(
            name=data.get("name", ""),
            key=data.get("key", ""),
            type=data.get("type"),
            source=data.get("source"),
            modelType=data.get("modelType"),
        )


@dataclass
class AuthAiSystemMappingEntity:
    """Represents a mapping between an auth configuration and an AI system."""

    mappingId: int
    mAiSystemId: str
    name: str
    isPrimary: bool
    createdAt: str
    updatedAt: str
    aiSystemMetadata: Optional[AiSystemMetadataEntity] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "AuthAiSystemMappingEntity":
        return AuthAiSystemMappingEntity(
            mappingId=int(data.get("mappingId")),
            mAiSystemId=str(data.get("mAiSystemId")),
            name=str(data.get("name")),
            isPrimary=bool(data.get("isPrimary")),
            createdAt=str(data.get("createdAt")),
            updatedAt=str(data.get("updatedAt")),
            aiSystemMetadata=AiSystemMetadataEntity.from_dict(data.get("aiSystemMetadata")),
        )


@dataclass
class UserAuthDataRecordEntity:
    """A single user auth_data record."""

    authId: int
    name: str
    authType: AuthTypeEnum
    providerType: ProviderTypeEnum
    authConfig: Dict[str, Any]
    createdAt: str
    updatedAt: str
    mUserId: Optional[str] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "UserAuthDataRecordEntity":
        return UserAuthDataRecordEntity(
            authId=int(data.get("authId")),
            name=str(data.get("name")),
            authType=AuthTypeEnum(str(data.get("authType"))),
            providerType=ProviderTypeEnum(str(data.get("providerType"))),
            # Keep the shape as-is; server returns camelCase keys in JSON
            authConfig=dict(data.get("authConfig") or {}),
            createdAt=str(data.get("createdAt")),
            updatedAt=str(data.get("updatedAt")),
            mUserId=data.get("mUserId"),
        )


@dataclass
class GetAuthDataByIdEntity:
    """Response for GET /user-auth/auth-data/:authId"""

    authData: UserAuthDataRecordEntity
    mappings: List[AuthAiSystemMappingEntity]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "GetAuthDataByIdEntity":
        return GetAuthDataByIdEntity(
            authData=UserAuthDataRecordEntity.from_dict(data.get("authData") or {}),
            mappings=[
                AuthAiSystemMappingEntity.from_dict(item) for item in (data.get("mappings") or [])
            ],
        )


@dataclass
class AuthDataAssociationItemBaseEntity:
    """Base fields for grouped association item in user-level listing."""

    authId: int
    name: str
    createdAt: str
    updatedAt: str
    aiSystems: List[AuthAiSystemMappingEntity] = field(default_factory=list)

    @staticmethod
    def _from_common(data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "authId": int(data.get("authId")),
            "name": str(data.get("name")),
            "createdAt": str(data.get("createdAt")),
            "updatedAt": str(data.get("updatedAt")),
            "aiSystems": [
                AuthAiSystemMappingEntity.from_dict(item) for item in (data.get("aiSystems") or [])
            ],
        }


@dataclass
class AuthDataAssociationItemRemoteCloudEntity(AuthDataAssociationItemBaseEntity):
    """Grouped association item for remote cloud with camelCase authConfig."""

    authConfig: AuthConfigRemoteCloudEntity = field(default_factory=AuthConfigRemoteCloudEntity)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "AuthDataAssociationItemRemoteCloudEntity":
        common = AuthDataAssociationItemBaseEntity._from_common(data)
        return AuthDataAssociationItemRemoteCloudEntity(
            **common,
            authConfig=AuthConfigRemoteCloudEntity.from_dict(data.get("authConfig")),
        )


@dataclass
class AuthDataAssociationItemRemoteCustomEntity(AuthDataAssociationItemBaseEntity):
    """Grouped association item for remote custom with free-form authConfig."""

    authConfig: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "AuthDataAssociationItemRemoteCustomEntity":
        common = AuthDataAssociationItemBaseEntity._from_common(data)
        return AuthDataAssociationItemRemoteCustomEntity(
            **common, authConfig=dict(data.get("authConfig") or {})
        )


@dataclass
class AuthProviderGroupRemoteCloudEntity:
    """Provider group: remote cloud."""

    provider: str
    authData: List[AuthDataAssociationItemRemoteCloudEntity]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "AuthProviderGroupRemoteCloudEntity":
        return AuthProviderGroupRemoteCloudEntity(
            provider=str(data.get("provider")),
            authData=[
                AuthDataAssociationItemRemoteCloudEntity.from_dict(item)
                for item in (data.get("authData") or [])
            ],
        )


@dataclass
class AuthProviderGroupRemoteCustomEntity:
    """Provider group: remote custom."""

    provider: str
    authData: List[AuthDataAssociationItemRemoteCustomEntity]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "AuthProviderGroupRemoteCustomEntity":
        return AuthProviderGroupRemoteCustomEntity(
            provider=str(data.get("provider")),
            authData=[
                AuthDataAssociationItemRemoteCustomEntity.from_dict(item)
                for item in (data.get("authData") or [])
            ],
        )


@dataclass
class UserMetadataEntity:
    """User metadata returned in user-level listing."""

    _id: str
    email: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "UserMetadataEntity":
        return UserMetadataEntity(_id=str(data.get("_id", "")), email=str(data.get("email", "")))


@dataclass
class GetUserLevelAuthDataAndModelAssociationEntity:
    """Response for GET /user-auth/auth-data-and-model-association"""

    userMetadata: UserMetadataEntity
    remoteCloud: List[AuthProviderGroupRemoteCloudEntity]
    remoteCustom: List[AuthProviderGroupRemoteCustomEntity]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "GetUserLevelAuthDataAndModelAssociationEntity":
        return GetUserLevelAuthDataAndModelAssociationEntity(
            userMetadata=UserMetadataEntity.from_dict(data.get("userMetadata") or {}),
            remoteCloud=[
                AuthProviderGroupRemoteCloudEntity.from_dict(item)
                for item in (data.get("remoteCloud") or [])
            ],
            remoteCustom=[
                AuthProviderGroupRemoteCustomEntity.from_dict(item)
                for item in (data.get("remoteCustom") or [])
            ],
        )


@dataclass
class UpdateAuthMappingsOnAuthDataResponseEntity:
    """Response for POST /user-auth/auth-data/:authId/mappings"""

    added: List[str]
    removed: List[str]
    promotions: Dict[str, Optional[int]]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "UpdateAuthMappingsOnAuthDataResponseEntity":
        return UpdateAuthMappingsOnAuthDataResponseEntity(
            added=list(data.get("added") or []),
            removed=list(data.get("removed") or []),
            promotions=dict(data.get("promotions") or {}),
        )


@dataclass
class DeleteAuthDataResponseEntity:
    """Response for DELETE /user-auth/auth-data/:authId"""

    deleted: bool
    message: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "DeleteAuthDataResponseEntity":
        return DeleteAuthDataResponseEntity(
            deleted=bool(data.get("deleted")), message=str(data.get("message", ""))
        )
