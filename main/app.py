# from gevent import monkey
# monkey.patch_all()
#
# from fastapi.middleware.cors import CORSMiddleware
# from main.api.file_upload_controller import uploadRouter
# from main.api.migration_controller import migrationRouter
# from main.api.test_controller import testRouter
# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse
# import traceback
#
# app = FastAPI(debug=True)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# app.include_router(migrationRouter, prefix="/migration")
# app.include_router(testRouter, prefix="/test")
# app.include_router(uploadRouter)
#
# @app.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc: Exception):
#     print("🔥🔥🔥 GLOBAL CATCH EXCEPTION 🔥🔥🔥")
#     print("Exception:", str(exc))
#     traceback.print_exc()
#     return JSONResponse(
#         status_code=500,
#         content={"detail": f"Internal Server Error: {str(exc)}"},
#     )
#
# @app.on_event("startup")
# def list_routes():
#     print("=== ROUTES LOADED ===")
#     for route in app.router.routes:
#         print(f"{route.methods} {route.path}")
#
#
#

from api import file_upload_controller, migration_controller
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import test_controller, runs_controller   # ודא __init__.py ב־api
from main.api.migration_controller import migrationRouter
from main.api.test_controller import testRouter

app = FastAPI(title="DB Benchmark API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(runs_controller.router, tags=["runs"])
app.include_router(migrationRouter, prefix="/migration")
app.include_router(file_upload_controller.uploadRouter)
app.include_router(testRouter, prefix="/test")


@app.on_event("startup")
def list_routes():
    print("=== ROUTES LOADED ===")
    for route in app.router.routes:
        print(f"{route.methods} {route.path}")