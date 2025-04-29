from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from main.api.test_controller import testRouter
from main.api.migration_controller import migrationRouter


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(testRouter, prefix="/test")
app.include_router(migrationRouter, prefix="/migration")


@app.on_event("startup")
def list_routes():
    print("=== ROUTES LOADED ===")
    for route in app.router.routes:
        print(f"{route.methods} {route.path}")
