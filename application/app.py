import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from application.helpers.extensions import load_extensions
from .helpers.core import load_environment
from .router import products,categories,contact,auth,options,sellers,account,favorites


def register_routers(app):
    """Register app routers."""
    app.include_router(auth.router,prefix='/v1')
    app.include_router(sellers.router,prefix='/v1')
    app.include_router(products.router,prefix='/v1')
    app.include_router(contact.router,prefix='/v1')
    app.include_router(options.router,prefix='/v1')
    app.include_router(account.router,prefix='/v1')
    app.include_router(favorites.router,prefix='/v1')
    app.include_router(categories.router,prefix='/v1')
    
    

def create_app() -> FastAPI:
    """App factory. """
    app = FastAPI(title='TestGrow')

    load_environment()
    load_extensions(app)
    register_routers(app)

    return app

app = create_app()

