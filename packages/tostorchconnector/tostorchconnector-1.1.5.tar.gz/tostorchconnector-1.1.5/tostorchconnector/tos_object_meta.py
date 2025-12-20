from typing import Optional

from tosnativeclient.tosnativeclient import ReadStream


class TosObjectMeta(object):
    def __init__(self, bucket: str, key: str, size: Optional[int] = None, etag: Optional[str] = None):
        self._bucket = bucket
        self._key = key
        self._size = size
        self._etag = etag
        self._read_stream: Optional[ReadStream] = None

    @property
    def bucket(self) -> str:
        return self._bucket

    @property
    def key(self) -> str:
        return self._key

    @property
    def size(self) -> Optional[int]:
        return self._size

    @property
    def etag(self) -> Optional[str]:
        return self._etag
