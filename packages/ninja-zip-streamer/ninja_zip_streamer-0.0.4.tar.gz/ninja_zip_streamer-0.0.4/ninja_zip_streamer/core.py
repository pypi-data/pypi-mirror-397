"""Core functions and classes."""

import os
import mmap
from pathlib import Path
from functools import partial
import requests
from stream_unzip import stream_unzip
from ninja_zip_streamer.utils import get_session, get_logger_for

log = get_logger_for(__name__)
DEFAULT_CHUNK_SIZE = 1024 * 32


def from_local_file(local_file_path: str, chunk_size: int = DEFAULT_CHUNK_SIZE):
    """Generates chunks from a local file."""
    log.debug(
        "Generating chunks of size %s from local file %s", chunk_size, local_file_path
    )
    disk_fd = os.open(local_file_path, os.O_RDONLY | os.O_DIRECT)
    with os.fdopen(disk_fd, "rb+", 0) as f:
        while True:
            m = mmap.mmap(-1, chunk_size)
            if not f.readinto(m):
                break
            yield m.read(chunk_size)


def from_remote_file(
    url: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    verify: bool = True,
    headers: dict[str, str] | None = None,
    timeout: int = 30,
    session: requests.Session | None = None,
):
    """Stream chunks from a remote file."""
    log.debug("Generating chunks of size %s from remote file %s", chunk_size, url)
    sess = session or get_session()
    sess.headers.update(headers or {})
    with sess.get(url, verify=verify, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        yield from r.iter_content(chunk_size=chunk_size)


def extract(  # pylint: disable=too-many-locals
    pth_or_url: str, out_dir: str, only_suffixes: list[str] | None = None, **kwargs
) -> list[str]:
    """Extract files from an archive (remote or local file)."""
    if only_suffixes:
        log.info("Extracting only files with this suffixes: %s", only_suffixes)

    # Decompress chunks and write files in O_DIRECT mode
    out_local_files = []
    chunks_func = (
        partial(from_remote_file, url=pth_or_url)
        if pth_or_url.lower().startswith(("https://", "http://"))
        else partial(from_local_file, local_file_path=pth_or_url)
    )
    for file_name, file_size, unzipped_chunks in stream_unzip(chunks_func(**kwargs)):
        name = file_name.decode("utf-8")
        if only_suffixes and not name.endswith(tuple(only_suffixes)):
            log.debug("The file %s does not match the provided suffix list", name)
            # This is required to continue
            for _ in unzipped_chunks:
                pass
            continue
        out = os.path.join(out_dir, name)
        if file_size == 0:
            log.info("Directory %s", out)
        else:
            log.info("Writing file %s (size is %s)", out, file_size)
            Path(os.path.dirname(out)).mkdir(parents=True, exist_ok=True)
            f = os.open(out, os.O_RDWR | os.O_CREAT | os.O_DIRECT)
            out_buf = None
            for chunk in unzipped_chunks:
                out_buf = out_buf + chunk if out_buf else chunk
                # Write contiguous buffer aligned to 512 bytes
                bsz = 512 * (len(out_buf) // 512)
                if bsz > 0:
                    m = mmap.mmap(-1, bsz)
                    m.write(out_buf[:bsz])
                    os.write(f, m)
                # Keep remaining bytes (i.e. not written)
                out_buf = out_buf[bsz:]

            # Write remaining bytes, if any
            if out_buf and len(out_buf) > bsz:
                n = mmap.mmap(-1, 512)
                n.write(out_buf)
                os.write(f, n)
            os.close(f)
            out_local_files.append(out)
    return out_local_files
