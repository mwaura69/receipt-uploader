from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Receipt(BaseModel):
    id: int
    date: datetime
    merchant: str
    total_amount: float
    items: List[dict]
    image_path: Optional[str]

class ReceiptCreate(BaseModel):
    merchant: str
    total_amount: float
    items: List[dict]
    image_path: Optional[str]