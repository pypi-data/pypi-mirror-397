from typing import TypeVar, Generic

from pydantic import BaseModel, Field, ConfigDict
from abc import ABC
from datetime import datetime

GenericNative = TypeVar('GenericNative')


class NativeId(BaseModel, Generic[GenericNative]):
    id: str
    version: int | None = Field(default=None)


class FormDataNative:

    @staticmethod
    def create(id_: str, version: int | None = None):
        return NativeId[FormDataNative](id=id_, version=version)


class FormSchemaNative:
    @staticmethod
    def create(id_: str, version: int | None = None):
        return NativeId[FormSchemaNative](id=id_, version=version)


class FormHierarchyNative:
    @staticmethod
    def create(id_: str, version: int | None = None):
        return NativeId[FormHierarchyNative](id=id_, version=version)


class FormDbItem(BaseModel, Generic[GenericNative]):
    native_id: NativeId[GenericNative] | None = Field(alias="nativeId", default=None)

    model_config = ConfigDict(
        populate_by_name=True,
    )


class CreatorInfo(BaseModel):
    username: str
    email: str
    given_name: str = Field(alias="givenName")
    family_name: str = Field(alias="familyName")

    model_config = ConfigDict(
        populate_by_name=True,
    )


class FormSchemaLinks(FormDbItem[FormSchemaNative]):
    parents: list[str]


class FormSchemaPreview(FormDbItem[FormSchemaNative]):
    title: str


class FormSchema(FormSchemaPreview):
    form_schema: dict = Field(alias='schema')


class FormDataMeta(FormDbItem[FormDataNative]):
    label: str = Field(default=None)
    form_schema: FormSchemaPreview = Field(alias='schema')
    created: datetime | None
    creator: CreatorInfo | None


class FormData(BaseModel):
    meta: FormDataMeta
    data: dict

    @property
    def display_name(self):
        return self.meta.label or self.meta.form_schema.title


class FormDataPreview(FormDbItem[FormDataNative]):
    label: str | None = Field(default=None)
    title: str


class FormFolderPreview(FormDbItem[FormHierarchyNative]):
    label: str


class FormFolder(FormFolderPreview):
    children: list[FormFolderPreview] = Field(default=[])
    form_schema: list[FormSchemaPreview] = Field(alias='schema', default=None)
    data: list[FormDataPreview] = Field(default=None)


class DataKeyInfo(FormDataPreview):
    created: datetime
    foreign_keys: list[str] = Field(alias="fks")


type SimpleNativeInput[GenericNative] = tuple[str, NativeId[GenericNative], FormDbItem[GenericNative], None]

type NativeInput[GenericNative] = tuple[SimpleNativeInput, FormData]


def coerce_native[GenericNative](input_: NativeInput) -> NativeId[GenericNative] | None:
    if input_ is None:
        return None

    if isinstance(input_, NativeId):
        return input_

    if isinstance(input_, str):
        return NativeId[GenericNative](id=input_)

    if isinstance(input_, FormDbItem):
        return input_.native_id

    if isinstance(input_, FormData):
        return input_.meta.native_id

    raise TypeError("Unknown Forms DB input")


def get_native_id(input_: NativeInput):
    native = coerce_native(input_)
    return native.id if native is not None else None



