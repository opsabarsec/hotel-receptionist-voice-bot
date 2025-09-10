"""This scripts contains the main API functions to call the bot and reservation_db modules.
Tech: FastAPI, Uvicorn"""

from fastapi import FastAPI
import uvicorn
from bot_main import bot
from reservation_db import HotelRequest, save_request_to_json
import asyncio

app = FastAPI()

# src/bot_main.py

# src/reservation_db.py
