from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from schemas.user_schemas import UserLogin
from config import JWT_SECRET
from endpoints.auth import auth_router
from endpoints.game_process import game_router
from endpoints.users import users_router


app = FastAPI()

app.include_router(auth_router)
app.include_router(game_router)
app.include_router(users_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


class Settings(BaseModel):
    authjwt_secret_key: str = JWT_SECRET
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = False
    authjwt_refresh_cookie_path: str = "api/auth"
    authjwt_access_cookie_path: str = "/"
    authjwt_cookie_samesite: str = "lax"
    authjwt_access_token_expires: int = 3600


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.get('/protected')
def protected(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    return {"user": current_user}