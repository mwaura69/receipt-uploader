from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List
import os
from app.database.models import Receipt, ReceiptCreate
from app.ocr.parser import ReceiptParser
from datetime import datetime

app = FastAPI()

# In-memory storage (replace with database in production)
receipts = []

@app.post("/receipts/upload/")
async def upload_receipt(file: UploadFile = File(...)):
    # Save the uploaded file
    file_path = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Process the receipt
    parser = ReceiptParser()
    print(parser)
    text = parser.extract_text(file_path)
    receipt_data = parser.parse_receipt(text)
    
    # Create receipt object
    receipt = Receipt(
        id=len(receipts) + 1,
        date=receipt_data['date'] or datetime.now(),
        merchant=receipt_data['merchant'],
        total_amount=receipt_data['total_amount'],
        items=receipt_data['items'],
        image_path=file_path
    )
    
    receipts.append(receipt)
    return receipt

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