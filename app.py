from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from main.api.migration_controller import migrationRouter
from main.api.test_controller import testRouter

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(migrationRouter, prefix="/migration")
app.include_router(testRouter, prefix="/test")
