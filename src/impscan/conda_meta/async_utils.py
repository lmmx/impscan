from __future__ import annotations

import asyncio
from functools import partial

from aiostream import stream
from httpx import AsyncClient, Response

from .formats import CondaArchive

__all__ = ["fetch", "process_archive", "async_fetch_urlset", "fetch_urls"]


async def fetch(session: AsyncClient, url: str, can_raise: bool = False) -> Response:
    response = await session.get(url)
    if can_raise:
        response.raise_for_status()
    return response


async def process_archive(resp: Response, lst: list[CondaArchive], pbar=None):
    # Map the response back to the CondaArchive it came from in the package listings
    archive = next(a for a in lst if a.url == resp.url)
    # raise NotImplementedError  # breakpoint here
    # Save the archive for inflating later (using multiprocessing on entire listing)
    archive.frozen_archive = await resp.aread()
    print({resp.url: resp})
    if pbar:
        pbar.update()


async def async_fetch_urlset(urls, archives: list[CondaArchive], pbar=None):
    async with AsyncClient() as session:
        ws = stream.repeat(session)
        xs = stream.zip(ws, stream.iterate(urls))
        ys = stream.starmap(
            xs,
            fetch,
            ordered=False,
            task_limit=20,
        )  # 30 is similar IDK
        process = partial(process_archive, lst=archives, pbar=pbar)
        zs = stream.map(ys, process)
        return await zs


def fetch_archives(archives: list[CondaArchive], pbar=None):
    print("----------------- Fetching archives -------------------")
    urlset = map(lambda a: a.url, archives)  # regenerate with map
    return asyncio.run(async_fetch_urlset(urlset, archives, pbar))
