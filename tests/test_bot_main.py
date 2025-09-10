import sys
import os
import json
import pytest

# Add the src folder to sys.path so Python can find bot_main.py
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, src_path)

from bot_main import HotelRequest, save_request_to_json


def test_hotel_request_model():
    record = HotelRequest(
        Available=True,
        CheckInDate="2025-09-21",
        CheckoutDate="2025-09-25",
        NumberOfGuests=2,
        guest_name="John Smith",
        room_type="double",
        special_requests="Late check-in",
    )
    assert record.Available is True
    assert record.CheckInDate == "2025-09-21"
    assert record.NumberOfGuests == 2
    assert record.special_requests == "Late check-in"


def test_save_request_to_json(tmp_path):
    test_file = tmp_path / "test_hotel_requests.json"
    request = HotelRequest(
        Available=True,
        CheckInDate="2025-09-21",
        CheckoutDate="2025-09-25",
        NumberOfGuests=2,
        guest_name="Alice",
        room_type="suite",
        special_requests="Ocean view",
    )
    save_request_to_json(request, filename=str(test_file))
    with open(test_file, "r") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["guest_name"] == "Alice"
    assert data[0]["room_type"] == "suite"
