from enum import Enum
from typing import Union

from pydantic import BaseModel, Field
from datetime import datetime
from pycarta.admin.types.resource_type import ResourceType


class FileStatus(Enum):
    INIT = "init"
    CACHED = "cached"
    STORED = "stored"


class Stats(BaseModel):
    created_by: str = Field(alias="createdBy")
    created: datetime

    updated_by: str = Field(alias="updatedBy")
    updated: datetime

    last_touched: datetime | None = Field(alias="lastTouched", default=None)
    filename: str
    size: int | None = Field(default=None)


class Permissions(BaseModel):
    carta_id: str = Field(alias="cartaId")
    carta_type: ResourceType | None = Field(alias="cartaType", default=None)
    i_project_id: str | None = Field(alias="projectId", default=None)

    @property
    def project_id(self):
        if self.i_project_id is not None:
            return self.i_project_id
        if self.carta_type == ResourceType.PROJECT:
            return self.carta_id
        raise ValueError("Project id cannot be determined for the given file")



class DriverErrorLog(BaseModel):
    t: datetime
    message: str


class Driver(BaseModel):
    driver_url: str | None = Field(alias="driverUrl", default=None)
    pending_action: bool = Field(alias="pendingAction")
    error: DriverErrorLog | None = Field(default=None)
    token: str | None = Field(default=None)
    storage_metadata: dict | None = Field(alias="metadata", default=None)


class UploadMetadata(BaseModel):
    expires: datetime
    multipart: str | None = Field(default=None)
    by_user: str | None = Field(alias="byUser", default=None)
    by_driver: str | None = Field(alias="byDriver", default=None)
    previous_status: FileStatus | None = Field(alias="previousStatus", default=None)


class FileKey(BaseModel):
    file: str

    @classmethod
    def parse(cls, key: Union[str, "FileKey"]) -> "FileKey":
        if isinstance(key, str):
            return FileKey(file=key)
        return key


class CartaFsFile(FileKey):
    stats: Stats
    permissions: Permissions
    driver: Driver
    upload: UploadMetadata | None = Field(default=None)
    status: FileStatus
    cached: bool

