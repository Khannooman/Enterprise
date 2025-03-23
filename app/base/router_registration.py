from fastapi import FastAPI
from app.routers.test_route import TestRouter
from app.routers.health_route import HealthRouter
from app.routers.docs_route import DocsRouter
from app.routers.user_route import UserRouter
from app.routers.customer_route import CustomerRouter


class RouterRegistration:
    def __init__(self, app: FastAPI):
        docs_router = DocsRouter()
        test_router = TestRouter()
        health_router = HealthRouter()
        user_router = UserRouter()
        customer_router = CustomerRouter()


        app.include_router(docs_router.router)
        app.include_router(test_router.router)
        app.include_router(health_router.router)
        app.include_router(user_router.router)
        app.include_router(customer_router.router)
