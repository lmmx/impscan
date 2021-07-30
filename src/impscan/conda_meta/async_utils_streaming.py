from __future__ import annotations

import asyncio
from functools import partial

from aiostream import stream
from httpx import AsyncClient, Response

from ..db.db_utils import CondaPackageDB
from .streaming_formats import CondaArchiveStream

__all__ = ["fetch", "process_archive", "async_fetch_urlset", "fetch_urls"]


async def fetch(
    session: AsyncClient,
    archive: CondaArchiveStream,
    can_raise: bool = False,
    n_retries: int = 3,
) -> Response | None:
    if archive.is_zstd:
        # archive.client = session # override initialised client
        # Do it synchronously, is that allowed ?
        archive.inflate_archive(db=session.db)
        response = None
    else:
        # (Retries due to httpx client bug documented in issue 6 of beeb issue tracker)
        for i in range(n_retries):
            try:
                response = await session.get(archive.url)
            except (ConnectTimeout, ProtocolError) as e:  # ProtocolError as e:
                print(f"Error occurred {e}, retrying", file=stderr)
                if i == n_retries - 1:
                    raise  # Persisted after all retries, so throw it, don't proceed
                # Otherwise retry, connection was terminated due to httpx bug
            else:
                break  # exit the for loop if it succeeds
    if can_raise:
        response.raise_for_status()
    return response


async def process_archive(
    resp: Response | None, lst: list[CondaArchiveStream], db=CondaPackageDB, pbar=None
):
    if resp is None:
        # Already processed synchronously
        if pbar:
            pbar.update()
    else:
        # Map the response back to the CondaArchiveStream it came from in the package listings
        archive = next(a for a in lst if a.url == resp.url)
        # Save the archive for inflating later (using multiprocessing on entire listing)
        # archive.frozen_archive = await resp.aread()
        archive.inflate_archive(db=db)
        print({resp.url: resp})
        if pbar:
            pbar.update()


async def async_fetch_urlset(
    archives: list[CondaArchiveStream], db: CondaPackageDB, pbar=None
):
    async with AsyncClient() as session:
        session.db = db  # For now, do zst streams synchronously, entering to DB
        ws = stream.repeat(session)
        xs = stream.zip(ws, stream.iterate(archives))
        ys = stream.starmap(
            xs, fetch, ordered=False, task_limit=20
        )  # 30 is similar IDK
        process = partial(process_archive, lst=archives, db=db, pbar=pbar)
        zs = stream.map(ys, process)
        return await zs


def fetch_archives(archives: list[CondaArchiveStream], db: CondaPackageDB, pbar=None):
    print("----------------- Fetching archives -------------------")
    # urlset = map(lambda a: a.url, archives)  # regenerate with map
    return asyncio.run(async_fetch_urlset(archives=archives, db=db, pbar=pbar))
