import traceback

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from main.api.migration_controller import migrationRouter
from main.api.test_controller import testRouter
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import traceback
app = FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(migrationRouter, prefix="/migration")
app.include_router(testRouter, prefix="/test")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("🔥🔥🔥 GLOBAL CATCH EXCEPTION 🔥🔥🔥")
    print("Exception:", str(exc))
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )
