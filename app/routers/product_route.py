import logging
from fastapi import APIRouter, HTTPException
from app.constants.route_paths import RoutePaths
from app.constants.route_tags import RouteTags
from app.controllers.database_controller import DatabaseController
from app.models.response_model import ResponseModel
from app.models.product_model import ProductCreateModel, ProductUpdateModel, StockEntryModel  # Assuming these are in product_model.py
from threading import Lock
from app.utils.utility_manager import UtilityManager

class ProductRouters(UtilityManager):
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            logging.info("-----: Creating new instance of: ProductRouter:-----")
            with cls._lock:
                if not cls._instance:  # Double-checked locking
                    cls._instance = super(ProductRouters, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "router"):  # Prevent reinitialization
            self.product_manager = DatabaseController()
            self.router = APIRouter(prefix=RoutePaths.API_PREFIX)
            self.setup_routes()

    def setup_routes(self):
        @self.router.post(RoutePaths.PRODUCT, tags=[RouteTags.PRODUCT], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def create_product(product: ProductCreateModel):
            """Create a new product"""
            product_data = self.product_manager.create_product(
                user_id=product.user_id,
                product=product.product,
                selling_price=product.selling_price,
                mrp=product.mrp,
                quantity=product.quantity,
                weight=product.weight,
                batch_number=product.batch_number,
                expiry_date=product.expiry_date,
                distributer_landing=product.distributer_landing,
                return_json=True
            )
            return ResponseModel(
                message="Product Created Successfully",
                data=product_data
            )

        @self.router.post(RoutePaths.PRODUCT_STOCK, tags=[RouteTags.PRODUCT], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def add_stock_entry(product_id: str, user_id: str, stock: StockEntryModel):
            """Add stock to an existing product"""
            updated_product = self.product_manager.add_stock_entry(
                product_id=product_id,
                user_id=user_id,
                quantity=stock.quantity,
                return_json=True
            )
            return ResponseModel(
                message="Stock Added Successfully",
                data=updated_product
            )

        @self.router.get(RoutePaths.PRODUCT, tags=[RouteTags.PRODUCT], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def get_all_products(user_id: str):
            """Get all products for a user"""
            products = self.product_manager.get_all_products(user_id=user_id, return_json=True)
            return ResponseModel(
                message="Products Fetched Successfully",
                data=products
            )

        @self.router.get(RoutePaths.PRODUCT_WITH_ID, tags=[RouteTags.PRODUCT], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def get_product(product_id: str, user_id: str):
            """Get a single product by ID and user_id"""
            product = self.product_manager.get_product(product_id=product_id, user_id=user_id, return_json=True)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            return ResponseModel(
                message="Product found",
                data=product
            )

        @self.router.put(RoutePaths.PRODUCT_WITH_ID, tags=[RouteTags.PRODUCT], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def update_product(product_id: str, user_id: str, product_update: ProductUpdateModel):
            """Update a product"""
            updated_product = self.product_manager.update_product(
                product_id=product_id,
                user_id=user_id,
                product=product_update.product,
                weight=product_update.weight,
                batch_number=product_update.batch_number,
                expiry_date=product_update.expiry_date,
                quantity=product_update.quantity,
                mrp=product_update.mrp,
                distributer_landing=product_update.distributer_landing,
                selling_price=product_update.selling_price,
                return_json=True
            )
            return ResponseModel(
                message="Product updated successfully",
                data={
                    "product_id": product_id,
                    "user_id": user_id,
                    "response": updated_product
                }
            )

        @self.router.delete(RoutePaths.PRODUCT_WITH_ID, tags=[RouteTags.PRODUCT], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def delete_product(product_id: str, user_id: str):
            """Delete a product"""
            self.product_manager.delete_product(product_id=product_id, user_id=user_id)
            return ResponseModel(
                message="Product deleted successfully",
                data={"product_id": product_id, "user_id": user_id}
            )