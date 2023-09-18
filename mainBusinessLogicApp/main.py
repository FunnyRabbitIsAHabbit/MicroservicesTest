import asyncio
import json
import os
from typing import Mapping, Type

import aiofiles
import aiohttp

# Assume you know the filename that the external service has the file registered with
FILENAME_OF_FILE_TO_REQUEST: str = "app.jpg"
# -----------------------------------------------------------------------------------

# Need to save files somewhere ------------------------------------------------
# Also configs are here -------------------------------------------------------
CURRENT_DIRECTORY: os.PathLike | str = os.getcwd()
OWN_RESOURCES: os.PathLike | str = os.path.join(CURRENT_DIRECTORY, "resources")
DOWNLOADED_PICS_FOLDER: os.PathLike | str = os.path.join(CURRENT_DIRECTORY, "pics")
# -----------------------------------------------------------------------------

# Testing purposes, I guess --------------------------
HOST_TO_REQUEST: str = os.environ.get("EXTERNAL_HOST")
PORT_TO_REQUEST: int = int(os.environ.get("EXTERNAL_PORT"))
# ----------------------------------------------------


with open(os.path.join(OWN_RESOURCES, "config.json")) as json_file_io:
    CONFIG: Mapping = json.load(fp=json_file_io)

BUFFER_SIZE_PICTURES: int = CONFIG["photo_buffering_buffer_size_bytes"]


async def create_new_session() -> aiohttp.ClientSession:
    session: aiohttp.ClientSession = aiohttp.ClientSession(trust_env=True,
                                                           base_url=f"http://{HOST_TO_REQUEST}:{PORT_TO_REQUEST}")
    return session


async def request_and_save_file(filename: os.PathLike = None) -> str | os.PathLike:
    filename: str = filename or FILENAME_OF_FILE_TO_REQUEST

    async with await create_new_session() as session:
        get_url: str = f"/files?filename={filename}"

        async with session.request(method="GET", url=get_url) as buffer_stream:
            new_path: str | os.PathLike = os.path.join(DOWNLOADED_PICS_FOLDER, filename)
            async with aiofiles.open(file=new_path, mode="wb+") as new_file:

                all_bytes_size: int = 0
                count_chunks: int = 0
                buffer_limit_lower, buffer_limit_upper = buffer_stream.content.get_read_buffer_limits()
                buffer_limit: int = max(max(BUFFER_SIZE_PICTURES, buffer_limit_lower),
                                        min(BUFFER_SIZE_PICTURES, buffer_limit_upper))

                async for buffer_bulk in buffer_stream.content.iter_chunked(n=buffer_limit):
                    all_bytes_size += len(buffer_bulk)
                    count_chunks += 1
                    await new_file.write(buffer_bulk)

                print(f"Bytes received: {all_bytes_size}. In {count_chunks} chunks. Per chunk: {buffer_limit} bytes")

                return os.path.split(new_file.name)[-1]


async def main():
    await asyncio.sleep(3)
    filename: os.PathLike | str = await request_and_save_file()
    print(filename)


if __name__ == "__main__":
    asyncio.run(main())
