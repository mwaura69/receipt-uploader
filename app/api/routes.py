from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List
import os
from app.database.models import Receipt, ReceiptCreate
from app.ocr.parser import ReceiptParser
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows only your frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage
receipts = []

@app.post("/receipts/upload")
async def upload_receipt(file: UploadFile = File(...)):
    logger.info(f"Upload endpoint hit")
    logger.info(f"File received: {file.filename}")
    logger.info(f"Content type: {file.content_type}")

    file_path = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    parser = ReceiptParser()
    text = parser.extract_text(file_path)
    receipt_data = parser.parse_receipt(text)

    receipt = Receipt(
        id=len(receipts) + 1,
        date=receipt_data.get("date") or datetime.now(),
        merchant=receipt_data.get("merchant"),
        total_amount=receipt_data.get("total_amount"),
        items=receipt_data.get("items"),
        image_path=file_path
    )

    receipts.append(receipt)
    return {"success": True, "parsed_data": receipt}

@app.get("/receipts/", response_model=List[Receipt])
def get_receipts():
    return receipts

@app.get("/receipts/total/")
def get_total_expenditure():
    total = sum(receipt.total_amount for receipt in receipts)
    return {"total_expenditure": total}

@app.get("/receipts/{receipt_id}", response_model=Receipt)
def get_receipt(receipt_id: int):
    for receipt in receipts:
        if receipt.id == receipt_id:
            return receipt
    raise HTTPException(status_code=404, detail="Receipt not found")
