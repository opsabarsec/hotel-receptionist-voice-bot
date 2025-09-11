"""This scripts contains the main API functions to call the bot, reader and reservation_db modules.
Tech: FastAPI"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from reader import extract_hotel_info
from bot_main import bot as bot_main_async  # main() coroutine with conversation logic
from reservation_db import insert_into_supabase
from supabase import create_client, Client

app = FastAPI()

SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_API_KEY"


@app.post("/bot")
async def bot_async_conversation():
    """
    Runs the async conversation flow via bot_main.main().
    Returns the most recently saved reservation (from JSON file).
    """
    # Run the async bot conversation
    conversation_text = await bot_main_async()
    print("Conversation ended.")
    # use extract_hotel_info from the text
    reservation = extract_hotel_info(conversation_text)

    # Convert reservation object to JSON
    reservation_json = reservation.model_dump()

    # Upload to Supabase
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        insert_into_supabase(supabase, [reservation_json])
        print("Reservation uploaded to Supabase.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase upload failed: {e}")

    return JSONResponse(
        content={"reservation": reservation.model_dump(), "status_code": 200}
    )
