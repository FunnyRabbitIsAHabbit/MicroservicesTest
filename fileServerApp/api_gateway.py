import os
from typing import Any, Mapping

import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

import file_server

app = FastAPI()


@app.get(path="/")
async def main() -> Mapping:
    return {"message": "Hello, world!", "status_code": 200, "ok": True}


@app.get(path="/files", response_model=None)
async def get_file_by_filepath(
        filename: str) -> Any:
    return StreamingResponse(content=file_server.serve_file(filepath=filename))


if __name__ == "__main__":
    uvicorn.run(app=app,
                host=os.environ.get("HOST"),
                port=int(os.environ.get("PORT")))
