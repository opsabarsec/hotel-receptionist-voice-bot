"""This scripts contains the main API functions to call the bot and reservation_db modules.
Tech: FastAPI"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from bot_main import bot as bot_main_async  # main() coroutine with conversation logic
from reservation_db import load_json, insert_into_supabase
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
    await bot_main_async()
    # After the session, last JSON entry holds the reservation
    reservations = load_json("hotel_requests.json")
    if reservations:
        return reservations[-1]
    return JSONResponse(content={"status": "no reservation saved"}, status_code=204)


@app.post("/database")
def upload_to_supabase():
    """
    Inserts all reservations from hotel_requests.json to Supabase.
    """
    reservations = load_json("hotel_requests.json")
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        insert_into_supabase(supabase, reservations)
        return {"status": "success", "inserted_records": len(reservations)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# example use for the API
