import os
import re
import inspect
from models import db
from pydantic import BaseModel
from fastapi.routing import APIRoute
from fastapi_jwt_auth import AuthJWT
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi_jwt_auth.exceptions import AuthJWTException
from application.helpers.core import send_log_slack_message
from application.helpers.connections import Redis_Con_Sync
from application.helpers.sentry import init_sentry


def load_extensions(app):

    @app.on_event("startup")
    def startup():
        send_log_slack_message(f'MarketPlace API has started')


    @app.on_event("shutdown")
    def shutdown():
        send_log_slack_message(f'!!!! MarketPlace API has stopped!!!')
        
        if not db.is_closed():
            db.close()


    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse({'status':'error','message':exc.detail},exc.status_code)


    @app.exception_handler(AuthJWTException)
    def authjwt_exception_handler(_,exc: AuthJWTException):
        return JSONResponse(
            status_code=401,
            content={"status":"error","message": exc.message}
        )

    class Settings(BaseModel):
        authjwt_secret_key: str = '3CWen$Jc51Ui'
        authjwt_access_token_expires: int = os.environ['ACCESS_TOKEN_EXPIRES']
        authjwt_refresh_token_expires: int = os.environ['REFRESH_TOKEN_EXPIRES']
        authjwt_denylist_enabled: bool = True
        authjwt_denylist_token_checks: set = {"access","refresh"}


    @AuthJWT.load_config
    def get_config():
        return Settings()
    
    @AuthJWT.token_in_denylist_loader
    def check_if_token_in_denylist(decrypted_token):
        jti = decrypted_token['jti']
        entry = Redis_Con_Sync().red.get(jti)
        return entry and entry.decode() == 'true'
    
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="Marketplace API",
            version="1.0.0",
            description="TestGrow Marketplace API",
            routes=app.routes
        )
        
        
        openapi_schema["components"]["securitySchemes"] = {
            "Bearer Auth": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token"
            }
        }

        # Get all routes where jwt_optional() or jwt_required
        api_router = [route for route in app.routes if isinstance(route, APIRoute)]

        for route in api_router:
            path = getattr(route, "path")
            endpoint = getattr(route,"endpoint")
            methods = [method.lower() for method in getattr(route, "methods")]

            for method in methods:
                # access_token
                if (
                    re.search("jwt_required", inspect.getsource(endpoint)) or
                    re.search("fresh_jwt_required", inspect.getsource(endpoint)) or
                    re.search("jwt_optional", inspect.getsource(endpoint))
                ):
                    openapi_schema["paths"][path][method]["security"] = [
                        {
                            "Bearer Auth": []
                        }
                    ]

        app.openapi_schema = openapi_schema
        return app.openapi_schema


    app.openapi = custom_openapi
    init_sentry()