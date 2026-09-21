import json
import os
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image
from google import genai
from google.genai import types


# =====================================================
# LOAD .ENV
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(
    BASE_DIR / ".env"
)


# =====================================================
# GEMINI API KEY
# =====================================================

API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not configured."
    )


# =====================================================
# GEMINI CLIENT
# =====================================================

client = genai.Client(
    api_key=API_KEY
)

# =====================================================
# GEMINI RESPONSE SCHEMA
# =====================================================

DONATION_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "item": {
                        "type": "string"
                    },
                    "category": {
                        "type": "string"
                    },
                    "quantity": {
                        "type": "integer"
                    },
                    "confidence": {
                        "type": "number"
                    }
                },
                "required": [
                    "item",
                    "category",
                    "quantity",
                    "confidence"
                ]
            }
        }
    },
    "required": ["items"]
}


# =====================================================
# ANALYZE DONATION IMAGE
# =====================================================

def analyze_donation_image(image_path):

    try:

        image = Image.open(image_path)

        prompt = prompt = """
You are an AI assistant for an intelligent donation management system.

Analyze the uploaded image carefully and identify ALL visible
physical items that could reasonably be donated.

IMPORTANT:
Food donations must be analyzed carefully and separately.

=====================================================
GENERAL DETECTION RULES
=====================================================

1. Detect every clearly visible donation-relevant item.

2. Count identical visible items.

   Example:
   If the image contains 3 books:
   quantity = 3

3. Group identical items together.

4. Do NOT invent objects that are not visible.

5. Ignore:
   - People
   - Faces
   - Hands
   - Background objects
   - Decorative objects

6. Focus only on physical items that could reasonably
   be donated.

7. Use clear and simple item names.

8. Assign every detected item to the most appropriate category.

9. Confidence must be between 0 and 1.

10. If an item is partially visible but can still be identified
    with reasonable confidence, include it.

=====================================================
FOOD DETECTION
=====================================================

For food donations, identify the specific food item whenever
the image provides enough visual information.

Examples include:

- Rice Bag
- Wheat Bag
- Rice Packet
- Wheat Packet
- Dal Packet
- Pulses
- Flour Bag
- Flour Packet
- Sugar Bag
- Sugar Packet
- Cooking Oil
- Oil Bottle
- Cereal Packet
- Packaged Food
- Food Grain
- Other Food

IMPORTANT:

If a bag or packet clearly represents a food product,
identify the actual food type instead of returning only
"Food".

Example:

WRONG:
item = "Bag"
category = "Food"

BETTER:
item = "Rice Bag"
category = "Food"

Another example:

WRONG:
item = "Packet"
category = "Food"

BETTER:
item = "Wheat Packet"
category = "Food"

=====================================================
FOOD QUANTITY
=====================================================

Count physically visible bags, packets, bottles or containers.

Example:

Image contains:
3 rice bags
2 wheat bags
1 flour bag

Return:

Rice Bag -> quantity 3
Wheat Bag -> quantity 2
Flour Bag -> quantity 1

Do NOT estimate quantity from image area.

Only count separately visible items.

=====================================================
WEIGHT / SIZE
=====================================================

If the weight or size of a food package is clearly visible
from its label, use the item name to preserve that information.

Examples:

"25 kg Rice Bag"
"10 kg Wheat Bag"
"5 kg Flour Bag"

However:

DO NOT guess the weight if it is not clearly visible.

The quantity field must represent the number of visible
physical items, NOT kilograms.

Example:

One 25 kg rice bag:

quantity = 1

NOT:

quantity = 25

=====================================================
NON-FOOD ITEMS
=====================================================

Possible non-food categories include:

Clothing
Books
Education
Electronics
Furniture
Household
Toys
Other

=====================================================
CATEGORY RULES
=====================================================

Use exactly one of these categories:

Clothing
Books
Education
Electronics
Furniture
Household
Food
Toys
Other

Food-related items must use:

category = "Food"

=====================================================
FINAL RULES
=====================================================

- Return ONLY the requested JSON structure.
- Do not include explanations.
- Do not include markdown.
- Do not include text outside JSON.
"""

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[
                image,
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema=DONATION_SCHEMA
            )
        )

        raw_response = response.text

        data = json.loads(raw_response)

        return {
            "success": True,
            "items": data.get("items", [])
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }