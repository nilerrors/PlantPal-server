from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

from . import config, auth, plants
from .prisma import prisma


app = FastAPI(
    title='Management',
    description='Plant Watering Management System',
    version='1.0.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    print("Prisma Connected")
    await prisma.connect()

@app.on_event("shutdown")
async def shutdown():
    print("Prisma Disconnected")
    await prisma.disconnect()


@AuthJWT.load_config
def get_config():
    return config.Settings()

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


app.include_router(auth.router, tags=["authentication"])
app.include_router(plants.router, tags=["plants"])
