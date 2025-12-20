import logging
from functools import partial
from typing import Union, Iterator, Tuple, Optional
import os
from . import TosObjectReader
from .tos_client import TosClient, ReaderType
from .tos_object_meta import TosObjectMeta
from .tos_object_reader import TosObjectStream

log = logging.getLogger(__name__)


class TosObjectIterable(object):
    def __init__(self, bucket: str, prefix: str, prefetch: bool, client: TosClient):
        self._bucket = bucket
        self._prefix = prefix
        self._list_background_buffer_count = 3
        self._prefetch = prefetch
        self._client = client

    def __iter__(self) -> Iterator[TosObjectMeta]:
        return iter(TosObjectIterator(self._bucket, self._prefix, self._list_background_buffer_count, self._prefetch,
                                      self._client))


class TosObjectIterator(object):
    def __init__(self, bucket: str, prefix: str, list_background_buffer_count: int, prefetch: bool, client: TosClient):
        self._bucket = bucket
        self._prefix = prefix
        self._list_background_buffer_count = list_background_buffer_count
        self._prefetch = prefetch
        self._client = client
        self._delimiter: Optional[str] = None
        self._continuation_token: Optional[str] = None

        self._list_stream = None
        self._object_metas = None
        self._read_streams = None
        self._index = 0
        self._is_truncated = True

    def close(self) -> None:
        if self._list_stream is not None:
            self._list_stream.close()

    def __iter__(self) -> Iterator[TosObjectMeta]:
        return self

    def __next__(self) -> TosObjectMeta:
        if self._client.use_native_client:
            if self._list_stream is None:
                self._list_stream = self._client.gen_list_stream(self._bucket, self._prefix, max_keys=1000,
                                                                 delimiter=self._delimiter,
                                                                 continuation_token=self._continuation_token,
                                                                 list_background_buffer_count=self._list_background_buffer_count,
                                                                 prefetch=self._prefetch)

            if self._object_metas is None or self._index >= len(self._object_metas):
                self._object_metas = None
                self._index = 0
                while 1:
                    try:
                        (objects, read_streams) = next(self._list_stream)
                    except:
                        self.close()
                        raise
                    self._continuation_token = self._list_stream.current_continuation_token()
                    self._object_metas = objects.contents
                    self._read_streams = read_streams
                    if self._object_metas is not None and len(self._object_metas) > 0:
                        break

            object_meta = self._object_metas[self._index]
            read_stream = None
            if self._read_streams is not None:
                read_stream = self._read_streams[self._index]
            self._index += 1
            # this is very critical use the original bucket
            object_meta = TosObjectMeta(self._bucket, object_meta.key, object_meta.size, object_meta.etag)
            object_meta._read_stream = read_stream
            return object_meta

        while self._object_metas is None or self._index >= len(self._object_metas):
            if not self._is_truncated:
                raise StopIteration
            self._object_metas, self._is_truncated, self._continuation_token = self._client.list_objects(
                self._bucket,
                self._prefix,
                max_keys=1000,
                continuation_token=self._continuation_token,
                delimiter=self._delimiter)
            self._index = 0

        object_meta = self._object_metas[self._index]
        self._index += 1
        return object_meta


def parse_tos_url(url: str) -> Tuple[str, str]:
    if not url:
        raise ValueError('url is empty')

    if url.startswith('tos://'):
        url = url[len('tos://'):]

    if not url:
        raise ValueError('bucket is empty')

    url = url.split('/', maxsplit=1)
    if len(url) == 1:
        bucket = url[0]
        prefix = ''
    else:
        bucket = url[0]
        prefix = url[1]

    if not bucket:
        raise ValueError('bucket is empty')
    return bucket, prefix


def default_trans(obj: TosObjectReader) -> TosObjectReader:
    return obj


def gen_dataset_from_urls(urls: Union[str, Iterator[str]], _: TosClient) -> Iterator[TosObjectMeta]:
    if isinstance(urls, str):
        urls = [urls]
    return (TosObjectMeta(bucket, key) for bucket, key in [parse_tos_url(url) for url in urls])


def gen_dataset_from_prefix(prefix: str, prefetch: bool, client: TosClient) -> Iterator[TosObjectMeta]:
    bucket, prefix = parse_tos_url(prefix)
    return iter(TosObjectIterable(bucket, prefix, prefetch, client))


def trans_to_tos_object_reader(object_meta: TosObjectMeta, client: TosClient, reader_type: Optional[ReaderType] = None,
                               buffer_size: Optional[int] = None) -> TosObjectReader:
    object_stream = None
    if object_meta._read_stream is not None and not object_meta._read_stream.is_closed():
        if object_meta.size is None or object_meta.etag is None:
            get_object_meta = partial(client.head_object, object_meta.bucket, object_meta.key)
        else:
            get_object_meta = lambda: TosObjectMeta(object_meta.bucket, object_meta.key, object_meta.size,
                                                    object_meta.etag)
        object_stream = TosObjectStream(object_meta.bucket, object_meta.key, get_object_meta, client)
        if reader_type is not None and reader_type == ReaderType.RANGED:
            object_stream._random_object_stream = object_meta._read_stream
        else:
            object_stream._sequential_object_stream = object_meta._read_stream
    return client.get_object(object_meta.bucket, object_meta.key, object_meta.etag, object_meta.size,
                             reader_type=reader_type, buffer_size=buffer_size,
                             object_stream=object_stream)


def path_or_str_to_str(path: Union[str, os.PathLike]) -> str:
    return path if isinstance(path, str) else str(path)
