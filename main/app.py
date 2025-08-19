from gevent import monkey
monkey.patch_all()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from main.api import (
    file_upload_controller,
    migration_controller,
    test_controller,
    runs_controller,
)
app = FastAPI(title="DB Benchmark API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(test_controller.testRouter, tags=["tests"], prefix="/test")
app.include_router(runs_controller.router,   tags=["runs"])
app.include_router(migration_controller.migrationRouter, prefix="/migration")
app.include_router(file_upload_controller.uploadRouter)

@app.on_event("startup")
def list_routes():
    print("=== ROUTES LOADED ===")
    for route in app.router.routes:
        print(f"{route.methods} {route.path}")