from pycarta.admin.types import UserType, PermissionsRole
from pydantic import BaseModel, Field, field_serializer

from pycarta.admin.types.util import enum_to_str


class ConfigurationKey(BaseModel):
    project: str


class PermissionConfiguration(BaseModel):
    user_type: UserType = Field(alias="userType")
    permission_level: PermissionsRole = Field(alias="permissionLevel")

    _user_type_serializer = field_serializer('user_type')(enum_to_str)
    _permission_level_serializer = field_serializer('permission_level')(enum_to_str)


class Configuration(BaseModel):
    storage_backend: str = Field(alias="storageBackend")
    permissions: dict[str, PermissionConfiguration]


class ProjectConfiguration(ConfigurationKey, Configuration):
    pass


class ProjectFiles(ConfigurationKey):
    files: list[str]
