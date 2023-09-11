import json
import os
from typing import Mapping, Any

import aiofiles

CURRENT_DIRECTORY: os.PathLike | str = os.getcwd()
OWN_RESOURCES: os.PathLike | str = os.path.join(CURRENT_DIRECTORY, "resources")

with open(os.path.join(OWN_RESOURCES, "config.json")) as json_file_io:
    CONFIG: Mapping = json.load(fp=json_file_io)

BUFFER_SIZE_PICTURES: int = CONFIG["photo_buffering_buffer_size_bytes"]


async def serve_file(filepath: os.PathLike | str) -> Any:
    actual_path: os.PathLike | str = os.path.join(OWN_RESOURCES, filepath)

    async with aiofiles.open(file=actual_path, mode="rb", buffering=BUFFER_SIZE_PICTURES) as file_io:
        async for buffer_bulk in file_io:
            yield buffer_bulk
