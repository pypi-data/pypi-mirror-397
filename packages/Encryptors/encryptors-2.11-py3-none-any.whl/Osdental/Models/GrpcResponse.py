from typing import Optional, Any
from pydantic import BaseModel

class GrpcResponse(BaseModel):

    def __init__(self, status: Any, message: str, data: Optional[Any] = None):
        self.status: Any = status
        self.message: str = message
        self.data: Optional[Any] = data