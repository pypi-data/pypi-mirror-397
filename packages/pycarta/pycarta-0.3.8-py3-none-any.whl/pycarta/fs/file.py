import base64
import mimetypes
import os.path
import time
import traceback
from typing import BinaryIO, Callable

import requests
from pydantic import BaseModel, Field, ValidationError
from requests import HTTPError, Response

from pycarta.fs import CARTA_FS_SERVICE_PATH
from pycarta import CartaAgent
from .multipart_upload import Maximum_Single_Upload, upload_parameters, Estimated_Upload_Speed, MiB
from .types.exception import FileUnavailableException
from .types.file import CartaFsFile, FileKey


class _InitUploadResponse(BaseModel):
    file_meta: CartaFsFile = Field(alias="meta")
    upload_url: str | list[str] = Field(alias="uploadUrl")


class _InitDownloadResponse(BaseModel):
    file_meta: CartaFsFile = Field(alias="meta")
    download_url: str | list[str] = Field(alias="downloadUrl")


def _initiate_upload(filename: str, project: str, agent: CartaAgent,
                     parts: int = None, upload_time: int = None) -> _InitUploadResponse:

    try:
        response = (
            agent.post(CARTA_FS_SERVICE_PATH + '/files/upload', json={
                "filename": filename,
                "project": project,
                "parts": parts,
                "uploadTime": upload_time
            })
        )
        return _InitUploadResponse(**response.json())
    except HTTPError as http_error:
        requests_response: Response = http_error.response
        if requests_response.status_code == 409:
            response_json = requests_response.json()
            response = None
            try:
                # response may or may not include the file
                response = _InitUploadResponse(**response_json)
            except ValidationError:
                pass
            raise FileUnavailableException(message=response_json['message'], file=response)
        raise


def _initiate_update(file: str, agent: CartaAgent,
                     parts: int = None, upload_time: int = None,
                     ) -> _InitUploadResponse:

    try:
        response = (
            agent.put(CARTA_FS_SERVICE_PATH + f'/files/{file}', json={
                "parts": parts,
                "uploadTime": upload_time
            })
        )
        return _InitUploadResponse(**response.json())
    except HTTPError as http_error:
        requests_response: Response = http_error.response
        if requests_response.status_code == 409:
            response_json = requests_response.json()
            response = None
            try:
                # response may or may not include the file
                response = _InitDownloadResponse(**response_json)
            except ValidationError:
                pass
            raise FileUnavailableException(message=response_json['message'], file=response)
        raise


def _initiate_download(file: str, agent: CartaAgent):
    try:
        response = agent.get(CARTA_FS_SERVICE_PATH + f'/files/{file}/download')

        return _InitDownloadResponse(**response.json())
    except HTTPError as http_error:
        requests_response: Response = http_error.response
        if requests_response.status_code == 409:
            response_json = requests_response.json()
            response = None
            try:
                # response may or may not include the file
                response = _InitDownloadResponse(**response_json)
            except ValidationError:
                pass
            raise FileUnavailableException(message=response_json['message'], file=response)
        raise


def _complete_multipart_upload(file: str, parts: list[(int, str)], agent: CartaAgent = None):
    if not agent:
        from pycarta import get_agent
        agent = get_agent()

    parts.sort(key=lambda x: x[0])
    etag_bytes = map(lambda x: bytes.fromhex(x[1].strip('"')), parts)
    etag_encoded = base64.b64encode(b"".join(etag_bytes)).decode('utf-8')

    response = (
        agent.post(CARTA_FS_SERVICE_PATH + f'/files/{file}/complete', json={"parts": etag_encoded})
    )


class _ProgressFileObject:
    def __init__(
            self, file_object: BinaryIO, start: int, size: int, file_length: int,
            callback: Callable[[int], None] = None):
        self.file_object = file_object
        self.callback = callback or self._noop
        self.start = start
        self.total_size = min(size, file_length - start)
        self.bytes_read = 0

    @classmethod
    def _noop(cls, uploaded: int, total: int):
        pass

    def read(self, size=-1):
        if self.bytes_read >= self.total_size:
            return None
        size = min(size, self.total_size - self.bytes_read)
        self.file_object.seek(self.start + self.bytes_read)
        chunk = self.file_object.read(size)
        self.bytes_read += len(chunk)
        self.callback(self.bytes_read)
        return chunk

    def __iter__(self):
        return self

    def __next__(self):
        if self.bytes_read < self.total_size:
            to_read = 16 * 1024
            to_read = min(to_read, self.total_size - self.bytes_read)
            return self.read(to_read)

        raise StopIteration

    def __len__(self):
        return self.total_size

    def seek(self, offset, from_what=0):
        if from_what == 0:
            return self.file_object.seek(offset + self.start, 0) - self.start
        if from_what == 2:
            return self.file_object.seek(self.start + self.total_size + offset) - self.start
        return self.file_object.seek(offset, from_what) - self.start

    def tell(self):
        file_tell = self.file_object.tell()
        return file_tell - self.start

    def __getattr__(self, attr):
        print(attr)
        return getattr(self.file_object, attr)


def _upload_to_cache(
        upload_url: str, file_handle: (str, BinaryIO, int), part: int,
        callback: Callable[[int], None] = None
):
    uploader = _ProgressFileObject(
        file_handle[1],
        part * Maximum_Single_Upload,
        Maximum_Single_Upload,
        file_handle[2], callback)

    response = requests.put(
        url=upload_url,
        data=uploader,
        headers={'Content-Type': file_handle[0]}
    )

    return response.headers.get('ETag')


def upload(upload_file: str | BinaryIO,
           file_size: int = None,
           file_name: str = None,
           mime_type: str = None,
           file:  FileKey | str = None,
           project: str = None,
           on_progress_factory: Callable[[int], Callable[[int], None]] = None,
           agent: CartaAgent = None):
    """
    Upload a file to Carta FS

    Args:
        upload_file (str | BinaryIO): path to file or Binary stream to be uploaded.
        project (str): UUID of the project associated with this file. Only required when uploading a new file.
        file (str | FileKey): UUID or File Object. Only required when updating an existing file.
        file_name (str): Name of the file as it will appear in Carta FS.
        file_size (int): Size in bytes of the file. Required for stream. Ignored with path.
        mime_type (str): Type of data in the file.
        on_progress_factory (Callable[[int], Callable[[int], None]]): Callback that takes the file_size and returns a function that then takes the number of bytes uploaded
        agent (CartaAgent): Carta Authentication agent
    """
    if not agent:
        from pycarta import get_agent
        agent = get_agent()

    if isinstance(upload_file, str):
        file_size = os.path.getsize(upload_file)

        if mime_type is None:
            mime_type = mimetypes.guess_type(upload_file)[0]
        if file_name is None:
            file_name = os.path.basename(upload_file)

    mime_type = mime_type or "application/octet-stream"

    if file_size is None or file_name is None:
        raise ValueError("arguments 'file_size' and 'file_name' must be provided when uploading from a stream")

    progress_callback = on_progress_factory(file_size) if on_progress_factory is not None else lambda x: None

    (parts, duration) = upload_parameters(file_size)
    if file is not None:
        file = FileKey.parse(file)
        upload_response = _initiate_update(
            file=file.file,
            parts=parts,
            upload_time=duration,
            agent=agent
        )
    elif project is not None:
        upload_response = _initiate_upload(
            filename=file_name,
            project=project,
            parts=parts,
            upload_time=duration,
            agent=agent
        )
    else:
        raise ValueError("One of 'file' or 'project' must be set")

    if not isinstance(upload_response.upload_url, list):
        upload_response.upload_url = [upload_response.upload_url]

    close_stream = False
    if isinstance(upload_file, str):
        upload_file = open(upload_file, 'rb')
        close_stream = True

    etags = []
    progress_callback(0)
    for i, upload_part in enumerate(upload_response.upload_url):
        def _progress_callback(singular_progress):
            progress_callback(i * Maximum_Single_Upload + singular_progress)
        e_tag = _upload_to_cache(upload_part, (mime_type, upload_file, file_size), i, callback=_progress_callback)
        etags.append((i, e_tag))

    if close_stream:
        upload_file.close()

    if parts > 1:
        _complete_multipart_upload(upload_response.file_meta.file, etags, agent)

    progress_callback(file_size)

    return FileKey(file=upload_response.file_meta.file)


def download(
        file: FileKey | str,
        to: str | BinaryIO,
        agent: CartaAgent = None,
        retries: int = 5,
        on_progress_factory: Callable[[int], Callable[[int], None]] = None
):
    if not agent:
        from pycarta import get_agent
        agent = get_agent()

    file = FileKey.parse(file)

    download_url: str | None = None
    tries = 0

    while download_url is None:
        try:
            response = _initiate_download(file.file, agent)
            if response.download_url:
                download_url = response.download_url
                break
        except FileUnavailableException as e:
            tries += 1
            if tries >= retries:
                raise
            # If the file is unavailable, wait the time it would take to upload on 500 MiB/s connection
            #   or 1 second and try again
            time.sleep(max((e.file.file_meta.stats.size or 0) / (Estimated_Upload_Speed * 500), 1))

    with requests.get(download_url, stream=True) as download_data:
        content_length = int(download_data.headers.get("Content-Length", 1))
        progress_callback = on_progress_factory(content_length) if on_progress_factory is not None else lambda x: None

        close_stream = False
        if isinstance(to, str):
            to = open(to, 'wb')
            close_stream = True

        progress_callback(0)
        chunk_size = MiB * 8
        for idx, chunk in enumerate(download_data.iter_content(chunk_size=chunk_size)):
            progress_callback(idx * chunk_size)
            to.write(chunk)

        progress_callback(content_length)

        if close_stream:
            to.close()


def get_info(file: FileKey | str, agent: CartaAgent = None):
    """Retrieve Carta FS metadata related to a file"""
    file = FileKey.parse(file)

    if not agent:
        from pycarta import get_agent
        agent = get_agent()

    response = (
        agent.get(CARTA_FS_SERVICE_PATH + f'/files/{file.file}')
    )

    resp_json = response.json()

    return CartaFsFile(**resp_json)


def move_file(file: FileKey | str, driver_url: str,
              retries: int = 5,
              agent: CartaAgent = None):
    """
    Move a file to a different storage driver
    """
    file = FileKey.parse(file)
    tries = 0

    if not agent:
        from pycarta import get_agent
        agent = get_agent()
    file_info = None
    while True:
        try:
            response = (
                agent.post(CARTA_FS_SERVICE_PATH + f'/files/{file.file}/move', json={"driverUrl": driver_url})
            )
            break
        except HTTPError as http_error:
            requests_response: Response = http_error.response
            if requests_response.status_code == 409:
                tries += 1
                if tries >= retries:
                    raise

                if file_info is None:
                    file_info = get_info(file, agent)

                time.sleep(max((file_info.stats.size or 0) / (Estimated_Upload_Speed * 500), 1))
            raise

    resp_json = response.json()

    return CartaFsFile(**resp_json['meta'])
