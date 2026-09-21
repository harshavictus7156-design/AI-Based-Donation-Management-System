import os
import json

from PIL import Image
from google import genai
from google.genai import types
from dotenv import load_dotenv


# =====================================================
# LOAD ENVIRONMENT
# =====================================================

load_dotenv()


# =====================================================
# GEMINI CLIENT
# =====================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not configured."
    )


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

    "required": [
        "items"
    ]
}


# =====================================================
# SCAN IMAGE
# =====================================================

def scan_image(image_path):

    try:

        # -------------------------------------------------
        # Open image
        # -------------------------------------------------

        image = Image.open(
            image_path
        )


        # -------------------------------------------------
        # Gemini prompt
        # -------------------------------------------------

        prompt = """

You are an AI assistant for an intelligent donation
management platform.

Analyze the uploaded image carefully and identify ALL
physical items that are visible and could reasonably
be donated.

IMPORTANT:

1. Detect MULTIPLE objects in the same image.

2. If the image contains 3 books, return:
   item = "Book"
   quantity = 3

3. Group identical items together.

4. Do NOT return the same type of item multiple times.

5. Count only objects that are visibly present.

6. Do not invent objects.

7. Ignore:
   - people
   - faces
   - hands
   - background objects
   - decorations that are not donation items

8. Focus on actual donation items.

9. Use simple item names.

10. Categorize each item using one of:

   Clothing
   Books
   Education
   Electronics
   Furniture
   Household
   Food
   Toys
   Medical
   Other

11. Confidence must be a number between 0 and 1.

12. Quantity must be a positive integer.

13. Return ONLY the requested JSON structure.

Example:

If the image contains:

3 blankets
2 books
1 laptop

return:

{
    "items": [
        {
            "item": "Blanket",
            "category": "Household",
            "quantity": 3,
            "confidence": 0.95
        },
        {
            "item": "Book",
            "category": "Books",
            "quantity": 2,
            "confidence": 0.94
        },
        {
            "item": "Laptop",
            "category": "Electronics",
            "quantity": 1,
            "confidence": 0.98
        }
    ]
}

"""


        # -------------------------------------------------
        # Gemini request
        # -------------------------------------------------

        response = client.models.generate_content(

            model="gemini-3.6-flash",

            contents=[
                image,
                prompt
            ],

            config=types.GenerateContentConfig(

                response_mime_type="application/json",

                response_json_schema=
                DONATION_SCHEMA

            )

        )


        # -------------------------------------------------
        # Parse response
        # -------------------------------------------------

        raw_response = response.text

        data = json.loads(
            raw_response
        )


        # -------------------------------------------------
        # Validate items
        # -------------------------------------------------

        items = data.get(
            "items",
            []
        )


        if not items:

            return {

                "success": False,

                "message":
                "No donation items were detected."

            }


        # -------------------------------------------------
        # Clean response
        # -------------------------------------------------

        cleaned_items = []


        for item in items:

            cleaned_items.append({

                "item":
                str(
                    item.get(
                        "item",
                        "Unknown Item"
                    )
                ),

                "category":
                str(
                    item.get(
                        "category",
                        "Other"
                    )
                ),

                "quantity":
                max(
                    1,
                    int(
                        item.get(
                            "quantity",
                            1
                        )
                    )
                ),

                "confidence":
                round(
                    float(
                        item.get(
                            "confidence",
                            0
                        )
                    ),
                    2
                )

            })


        # -------------------------------------------------
        # Return result
        # -------------------------------------------------

        return {

            "success": True,

            "items":
            cleaned_items

        }


    except Exception as e:

        print(
            "Gemini image scanning error:",
            str(e)
        )

        return {

            "success": False,

            "message":
            str(e)

        }