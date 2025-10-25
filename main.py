import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.exceptions import HTTPBadRequest
from app.core.logres import init_logger
from app.api import api_router
from app.core.containers import Container

init_logger()

app = FastAPI(
    default_response_class=ORJSONResponse,
    title="chatgpt api",
    responses={
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "errmsg": "错误信息",
                        "detail": "错误详情"
                    }
                }
            }
        }
    },
)

container = Container()
app.container = container

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 自定义错误信息
@app.exception_handler(HTTPBadRequest)
async def custom_exception_handler(request: Request, exc: HTTPBadRequest):
    return ORJSONResponse(
        status_code=400,
        content={"errmsg": exc.errmsg, "detail": exc.detail},
    )



app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)