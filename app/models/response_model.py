from pydantic import BaseModel, Field
from typing import Any, List, Optional, Union, Dict
from app.utils.get_current_timestamp import get_current_timestamp_str

class APICallStatus:
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'

class StatusCodes:
    INTERNAL_SERVER_ERROR_500 = 500
    NOT_FOUND_404 = 404
    NOT_ALLOWED_400 = 400
    BAD_REQUEST_400 = 400
    BAD_RESQUEST_403 = 303
    OK_200 = 200
    CREATED_201 = 201

class ResponseModel(BaseModel, APICallStatus, StatusCodes):
    message: str = "Executed Successfully!"
    status_code: int = StatusCodes.OK_200
    status: Optional[str] = APICallStatus.SUCCESS
    timestamp: str = get_current_timestamp_str()
    data: Any = None
    error: Optional[str] = None
    response_time: Optional[float] = None
    additionals: Any = None

class AnalyticsResponseParser(BaseModel):
    """Prove Inside and chart data"""

    text_response: str = Field(description="Analytics text response")
    chart: Union[Dict, str] = Field(description="Echart data for response")




