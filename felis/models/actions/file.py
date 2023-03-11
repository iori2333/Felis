from pydantic import BaseModel

from .base import BaseAction


class UploadFileRequest(BaseAction):
    type: str
    name: str
    url: str
    headers: dict[str, str]
    path: str
    data: bytes
    sha256: str


class UploadFileResponse(BaseModel):
    file_id: str


class UploadFileFragmentedRequest:

    class Prepare(BaseAction):
        stage: str
        name: str
        total_size: int

    class Upload(BaseAction):
        stage: str
        file_id: str
        offset: int
        data: bytes

    class Complete(BaseAction):
        stage: str
        file_id: str
        sha256: str


class UploadFileFragmentedResponse:

    class Prepare(BaseModel):
        file_id: str

    class Complete(BaseModel):
        file_id: str


class FileRequest(BaseAction):
    file_id: str
    type: str


class FileResponse(BaseModel):
    name: str
    url: str
    headers: dict[str, str]
    path: str
    data: bytes
    sha256: str


class FileFragmentedRequest:

    class Prepare(BaseAction):
        stage: str
        file_id: str

    class Download(BaseAction):
        stage: str
        file_id: str
        offset: int
        size: int


class FileFragmentedResponse:

    class Prepare(BaseModel):
        name: str
        total_size: int
        sha256: str

    class Download(BaseModel):
        data: bytes
