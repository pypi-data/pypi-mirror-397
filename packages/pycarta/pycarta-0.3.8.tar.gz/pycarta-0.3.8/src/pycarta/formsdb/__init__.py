from __future__ import annotations

from typing import cast

from ..auth.agent import CartaAgent
from requests import Session, Response
from .types import FormFolder, FormSchema, FormSchemaLinks, FormData, DataKeyInfo, FormHierarchyNative, \
    SimpleNativeInput, coerce_native, get_native_id, FormSchemaNative, FormDataNative, NativeInput


class API_UNSET:
    pass


class FormsDb:

    def __init__(self, credentials: CartaAgent, project_id: str, *,
                 host=None) -> None:
        super().__init__()
        self.credentials = credentials
        self.host = host or f"{credentials.host}/service/carta/formsdb"  # or "http://localhost:3001" #
        self.project_id = project_id
        self.session = Session()
        self.session.headers['Authorization'] = f"Bearer {credentials.token}"

        self.folder = self.Folder(self)
        self.schema = self.Schema(self)
        self.data = self.Data(self)

    def _request(self, method, path, **extra) -> Response:

        if 'json' in extra and isinstance(extra['json'], dict):
            extra['json'] = {k: v for k, v in extra['json'].items() if not isinstance(v, API_UNSET)}

        response = self.session.request(
            method,
            url=f"{self.host}/{self.project_id}{path}",
            **extra
        )

        if response.ok:
            return response

        if response.status_code == 404:
            raise FileNotFoundError()

        if response.status_code == 400:
            raise ValueError(response.json())

        response.raise_for_status()

    class Folder:

        def __init__(self, form_db: FormsDb):
            self.form_db = form_db

        def get(self, *, folder_id: SimpleNativeInput[FormHierarchyNative] = None, path=None, show_data=False,
                show_schema=False) -> FormFolder | None:

            folder_id = get_native_id(folder_id)

            try:
                response = self.form_db._request('GET', '/folder', params={
                    "data": show_data,
                    "schema": show_schema,
                    "id": folder_id,
                    "path": path
                })

                return FormFolder(**response.json()['folder'])
            except FileNotFoundError:
                return None

        def create(self, *, label: str = None, parent: SimpleNativeInput[FormHierarchyNative] = API_UNSET(),
                   path: str = API_UNSET()) -> FormFolder:

            if not isinstance(parent, API_UNSET):
                parent = get_native_id(parent)
                if label is None:
                    raise ValueError("'label' is required when not creating a folder by path")
            elif isinstance(path, API_UNSET):
                raise ValueError("Path or Parent must be defined")

            response = self.form_db._request('POST', '/folder', json={
                "label": label,
                "parent": parent,
                "path": path
            })

            return FormFolder(**response.json()['folder'])

        def delete(self, *, folder_id: SimpleNativeInput[FormHierarchyNative] = API_UNSET(),
                   path=API_UNSET()) -> FormFolder | None:

            if not isinstance(folder_id, API_UNSET):
                folder_id = get_native_id(folder_id)

            try:
                response = self.form_db._request('DELETE', '/folder', json={
                    "id": folder_id,
                    "path": path
                })

                return FormFolder(**response.json()['folder'])
            except FileNotFoundError:
                return None

    class Schema:

        def __init__(self, form_db: FormsDb):
            self.form_db = form_db

        def get(self, schema_id: SimpleNativeInput[FormSchemaNative]):
            schema_id = coerce_native(schema_id)

            response = self.form_db._request('GET', f'/schema/{schema_id.id}', params={"version": schema_id.version})

            return FormSchema(**response.json()['form'])

        def create(self, title: str, schema: dict, *, path: str = API_UNSET(),
                   parent: SimpleNativeInput[FormHierarchyNative] = API_UNSET()):

            if isinstance(path, API_UNSET):
                if isinstance(parent, API_UNSET):
                    raise ValueError("Must have one of path or parent")
                else:
                    parent = get_native_id(parent)

            response = self.form_db._request('POST', '/schema', json={
                "title": title,
                "schema": schema,
                "path": path,
                "parent": parent
            })

            return FormSchema(**response.json()['form'])

        def remove(self, schema_id: SimpleNativeInput[FormSchemaNative]):
            schema_id = get_native_id(schema_id)

            response = self.form_db._request('DELETE', f"/schema/{schema_id}")

            return response.json()['form']

        def update(self, schema_id: SimpleNativeInput[FormSchemaNative], *, title: str = API_UNSET(),
                   schema: dict = API_UNSET()):
            schema_id = get_native_id(schema_id)

            if isinstance(title, API_UNSET) and isinstance(schema, API_UNSET):
                raise ValueError("Nothing to update")

            response = self.form_db._request('PUT', f"/schema/{schema_id}", json={
                'title': title,
                'schema': schema
            })

            return FormSchema(**response.json()['form'])

        def link(self, schema_id: SimpleNativeInput[FormSchemaNative], *, paths: list[str] = None,
                 parents: list[SimpleNativeInput[FormHierarchyNative]] = None):
            schema_id = get_native_id(schema_id)

            if (paths is None or len(paths) == 0) and (parents is None or len(parents) == 0):
                raise ValueError("Must have one of path or parent")

            if parents is not None:
                parents = cast(list[str],
                               [get_native_id(parent) for parent in parents])

            response = self.form_db._request('PUT', f"/schema/{schema_id}/parents", json={
                "parents": parents,
                "paths": paths
            })

            return FormSchemaLinks(**response.json()['form'])

    class Data:

        def __init__(self, form_db: FormsDb):
            self.form_db = form_db

        def get(self, form_id: NativeInput[FormDataNative]):
            form_id = coerce_native(form_id)

            response = self.form_db._request('GET', f'/data/{form_id.id}',
                                             params={
                                                 'version': form_id.version
                                             })

            return FormData(**response.json()['data'])

        def create(self, source_schema: SimpleNativeInput[FormSchemaNative], data: dict,
                   *,
                   path: str = API_UNSET(),
                   parent: SimpleNativeInput[FormHierarchyNative] = API_UNSET):

            source_schema = coerce_native(source_schema)

            if not isinstance(parent, API_UNSET):
                parent = get_native_id(parent)

            response = self.form_db._request('POST', f'/data', json={
                "sourceSchema": source_schema.id,
                "sourceVersion": source_schema.version,
                "data": data,
                "parent": parent,
                "path": path
            })

            return FormData(**response.json()['data'])

        def update(self, form_id: NativeInput[FormDataNative], *,
                   data: dict = API_UNSET(),
                   source_version: int = API_UNSET()):

            form_id = get_native_id(form_id)

            if isinstance(data, API_UNSET) and isinstance(source_version, API_UNSET):
                raise ValueError("Nothing to update")

            response = self.form_db._request('PUT', f'/data/{form_id}', json={
                "data": data,
                "sourceVersion": source_version
            })

            js = response.json()

            return FormData(**js['data'])

        def keys(self):
            response = self.form_db._request('GET', f'/data/keys')

            js = response.json()

            return [DataKeyInfo(**info) for info in js['keys']]

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
