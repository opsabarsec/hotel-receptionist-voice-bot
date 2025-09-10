import asyncio
from agents.realtime import RealtimeAgent, RealtimeRunner
from agents_mcp import Agent  # <--- Required for MCP support!
from pydantic import BaseModel, Field
from datetime import datetime
import json


# Define the Pydantic model for hotel requests
class HotelRequest(BaseModel):
    Available: bool = Field(
        ..., description="True if room is available, False otherwise"
    )
    CheckInDate: str = Field(..., description="Check-in date (YYYY-MM-DD)")
    CheckoutDate: str = Field(..., description="Check-out date (YYYY-MM-DD)")
    NumberOfGuests: int = Field(..., description="Number of guests for the reservation")
    guest_name: str = Field(..., description="Name of the guest")
    room_type: str = Field(..., description="Requested room type")
    special_requests: str = Field("", description="Any special requests")


def save_request_to_json(request: HotelRequest, filename: str = "hotel_requests.json"):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    data.append(request.model_dump())
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


async def bot():
    # ---- INTEGRATE MCP (Supabase, WhatsApp) ----
    agent = RealtimeAgent(
        name="Hotel Receptionist",
        instructions=(
            "You are a friendly hotel receptionist. "
            "Your job is to collect from the guest: name, check-in and check-out dates, "
            "preferred room type, number of guests, and any special requests. "
            "Confirm the reservation details succinctly.\n"
            "You also have access to Supabase and WhatsApp tools via MCP for handling data and sending confirmations."
        ),
        # <<<< ADD THIS: list MCP servers here! >>>>
        mcp_servers=["supabase", "whatsapp"],
    )
    # --------------------------------------------

    runner = RealtimeRunner(
        starting_agent=agent,
        config={
            "model_settings": {
                "model_name": "gpt-realtime",
                "voice": "alloy",
                "modalities": ["text", "audio"],
                "input_audio_transcription": {"model": "whisper-1"},
            },
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 200,
            },
        },
    )

    # Start the voice session
    session = await runner.run()
    async with session:
        print("Hotel receptionist agent ready for voice input.")
        reservation = {}
        async for event in session:
            if event.type == "conversation.item.input_audio_transcription.completed":
                print(f"User: {event.transcript}")
                # Here you need your logic to extract structured info from transcript (NLP or tool call)
                # For demo, let's use a placeholder:
                reservation = {
                    "guest_name": "John Smith",
                    "check_in": "2025-09-21",
                    "check_out": "2025-09-25",
                    "room_type": "double",
                    "num_guests": 2,
                    "special_requests": "Late check-in",
                }

            elif event.type == "response.audio_transcript.done":
                print(f"Receptionist: {event.transcript}")

            # When agent confirms all booking info, fill the form
            if reservation:
                record = HotelRequest(**reservation)
                save_request_to_json(record)
                print("Reservation saved in JSON.")

                # -------- Demonstrate Tool use (Template) -------------
                # To use the MCP tools, you can send a system-message or instruction format like:
                # await session.send_message("Save this reservation to Supabase and notify guest on WhatsApp.")
                # Or use session.tool_call(...) per your SDK if supported


if __name__ == "__main__":
    asyncio.run(bot())
