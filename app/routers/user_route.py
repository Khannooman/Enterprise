import logging
from fastapi import APIRouter, HTTPException
from app.constants.route_paths import RoutePaths
from app.constants.route_tags import RouteTags
from app.controllers.database_controller import DatabaseController
from app.enums.env_keys import EnvKeys
from app.models.response_model import ResponseModel
from app.models.user_model import UserCreateModel, UserUpdateModel, UserLoginRequestModel
from threading import Lock
from app.utils.utility_manager import UtilityManager
from datetime import timedelta
import datetime
from datetime import datetime as dt
import jwt

class UserRouter(UtilityManager):
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            logging.info("-----: Creating new instance of: UserRouter:-----")
            with cls._lock:
                if not cls._instance:  # Double-checked locking
                    cls._instance = super(UserRouter, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "router"):  # prevent reinitialization
            self.survey_manager = DatabaseController()
            self.router = APIRouter(prefix=RoutePaths.API_PREFIX)
            self.setup_routes()
            self.SECRET_KEY = self.get_env_variable(EnvKeys.SECRET_KEY.value)
            self.ALGORITHM = self.get_env_variable(EnvKeys.ALGORITHM.value)
            self.ACCESS_TOKEN_EXPIRE_MINUTES = int(self.get_env_variable(EnvKeys.ACCESS_TOKEN_EXPIRE_MINUTES.value))

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = dt.now(datetime.timezone.utc) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def setup_routes(self):
        @self.router.post(RoutePaths.USER, tags=[RouteTags.USER])
        @self.catch_api_exceptions
        async def create_user(user: UserCreateModel):
            """Create a new user"""
            user_data = self.survey_manager.create_user(
                username=user.username,
                password=user.password,
                email=user.email,
                phone_number=user.phone_number,
                company_name=user.company_name,
                addressline1=user.addressline1,
                city=user.city,
                state=user.state,
                pincode=user.pincode,
                country=user.country,
                addressline2=user.addressline2,
                landmark=user.landmark,
                return_json=True
            )
            print(user_data)
            return ResponseModel(
                message="User Created Successfully",
                data=user_data
            )

        @self.router.get(RoutePaths.USER, tags=[RouteTags.USER], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def get_users():
            """Get all users"""
            users = self.survey_manager.get_all_users()
            return ResponseModel(
                message="Fetched Successfully!",
                data=users
            )

        @self.router.get(RoutePaths.USER_WITH_ID, tags=[RouteTags.USER], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def get_user(user_id: str):
            """Get a single user by ID"""
            user = self.survey_manager.get_user(user_id=user_id, return_json=True)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return ResponseModel(
                message="User found",
                data=user
            )

        @self.router.put(RoutePaths.USER_WITH_ID, tags=[RouteTags.USER], response_model=ResponseModel)
        @self.catch_api_exceptions        
        async def update_user(user_id: str, user_update: UserUpdateModel):
            """Update a user"""
            updated_user = self.survey_manager.update_user(
                user_id=user_id,
                username=user_update.username,
                email=user_update.email,
                phone_number=user_update.phone_number,
                company_name=user_update.company_name,
                addressline1=user_update.addressline1,
                addressline2=user_update.addressline2,
                landmark=user_update.landmark,
                city=user_update.city,
                state=user_update.state,
                pincode=user_update.pincode,
                country=user_update.country,
                return_json=True
            )
            return ResponseModel(
                message="User updated successfully",
                data={
                    "user_id": user_id,
                    "response": updated_user
                }
            )

        @self.router.delete(RoutePaths.USER_WITH_ID, tags=[RouteTags.USER], response_model=ResponseModel)
        @self.catch_api_exceptions        
        async def delete_user(user_id: str):
            """Delete a user"""
            self.survey_manager.delete_user(user_id=user_id)
            return ResponseModel(
                message="User deleted successfully",
                data={"user_id": user_id}
            )

        @self.router.post(RoutePaths.LOGIN, tags=[RouteTags.AUTH], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def login(login_data: UserLoginRequestModel):
            """Authenticate user and return token"""
            # Note: Your DatabaseController doesn't have a verify_user method,
            # so we'll use get_user_by_username and manual password verification
            query = "SELECT * FROM users WHERE email = :email"
            user = self.survey_manager.db.execute_query(
                query,
                params={"email": login_data.email},
                fetch_one=True,
                return_json=True
            )
            
            if not user or not self.survey_manager.verify_password(login_data.password, user["password"]):
                raise HTTPException(status_code=401, detail="Invalid credentials")

            # Create access token
            access_token = self.create_access_token(
                data={"sub": user["user_id"]}
            )
            result = {
                "user_id": user["user_id"],
                "username": user["username"],
                "access_token": access_token,
                "token_type": "bearer"
            }
            return ResponseModel(
                message="Login successful",
                data=result
            )