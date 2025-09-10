import sys
import os
import pytest
from httpx import AsyncClient

# Ensure src is importable
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
from bot_main import app


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    # Adjust based on your root endpoint logic


@pytest.mark.asyncio
async def test_create_booking():
    booking_data = {
        "Available": True,
        "CheckInDate": "2025-11-01",
        "CheckoutDate": "2025-11-02",
        "NumberOfGuests": 2,
        "guest_name": "Test User",
        "room_type": "single",
        "special_requests": "None",
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/book", json=booking_data)
    assert response.status_code in (200, 201)
    json_resp = response.json()
    assert json_resp.get("guest_name") == "Test User"


# Add more endpoint tests as needed, such as getting bookings, updating, listing, etc.
