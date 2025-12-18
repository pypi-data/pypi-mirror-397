from typing import Iterable, Type


def chunkify(o, batch_size = 3):
    def list_chunkify(l):
        offset = 0

        while offset < len(l):
            upper = offset + batch_size \
                    if offset + batch_size < len(l) \
                    else len(l)
            yield(l[offset:upper])
            offset += batch_size

    def iter_chunkify(l):
        chunk = []
        for _ in l:
            chunk.append(_)
            if len(chunk) == batch_size:
                yield(chunk)
                chunk = []
        if chunk:
            yield chunk

    if isinstance(o, list):
        chunker = list_chunkify
    elif isinstance(o, Iterable):
        chunker = iter_chunkify
    else :
        raise TypeError(f"Unable to chunk {o} is not iterable")


    for _ in chunker(o):
        yield(_)
