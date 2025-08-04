import pytesseract
from PIL import Image
import re
from datetime import datetime
from dateutil.parser import parse

class ReceiptParser:
    @staticmethod
    def extract_text(image_path):
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text

    @staticmethod
    def parse_receipt(text):
        lines = text.split('\n')
        data = {
            'merchant': '',
            'date': None,
            'total_amount': 0.0,
            'items': []
        }

        # Extract merchant name (usually first few lines)
        data['merchant'] = lines[0].strip()

        # Find date
        for line in lines:
            try:
                date_match = parse(line, fuzzy=True)
                data['date'] = date_match
                break
            except:
                continue

        # Find total amount
        for line in lines:
            if any(keyword in line.lower() for keyword in ['total', 'sum', 'amount']):
                amounts = re.findall(r'\d+\.\d{2}', line)
                if amounts:
                    data['total_amount'] = float(amounts[-1])

        # Extract items (this is a simple implementation)
        items_started = False
        for line in lines:
            if re.search(r'\d+\.\d{2}', line):
                items_started = True
                amount = re.findall(r'\d+\.\d{2}', line)[-1]
                item_name = re.sub(r'\d+\.\d{2}', '', line).strip()
                if item_name and amount:
                    data['items'].append({
                        'name': item_name,
                        'price': float(amount)
                    })

        return data