from pydantic import BaseModel, Field
from pydantic_ai import Agent
from typing import Optional
import os
from datetime import datetime, timedelta


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


# Create the PydanticAI agent
hotel_agent = Agent(
    "openai:gpt-4o",
    result_type=HotelRequest,
    system_prompt="""
    You are a hotel reservation assistant that extracts booking information from text.
    
    Instructions:
    1. Extract all relevant hotel booking information from the provided text
    2. For dates, use YYYY-MM-DD format
    3. If specific dates aren't mentioned, infer reasonable dates based on context (e.g., "next week", "tomorrow")
    4. If availability isn't explicitly mentioned, assume Available=True
    5. If guest count isn't specified, assume 1 guest
    6. Extract the most likely room type mentioned (standard, deluxe, suite, etc.)
    7. Include any special requests, dietary requirements, or preferences mentioned
    8. If guest name isn't provided, use "Guest" as default
    
    Be intelligent about extracting information even if it's not perfectly structured.
    """,
)


async def extract_hotel_info(text: str, api_key: Optional[str] = None) -> HotelRequest:
    """
    Extract hotel booking information from text using GPT-4o via PydanticAI.

    Args:
        text (str): The input text containing hotel booking information
        api_key (str, optional): OpenAI API key through OPENAI_API_KEY env var

    Returns:
        HotelRequest: Parsed hotel booking information

    Raises:
        ValueError: If API key is not provided or found in environment
        Exception: If extraction fails
    """

    # Set API key if provided
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    elif not os.getenv("OPENAI_API_KEY"):
        raise ValueError(
            "OpenAI API key must be provided either as parameter or OPENAI_API_KEY environment variable"
        )

    try:
        # Run the agent to extract information
        result = await hotel_agent.run(text)
        return result.data

    except Exception as e:
        raise Exception(f"Failed to extract hotel information: {str(e)}")

    # Example usage


if __name__ == "__main__":
    # Example text inputs
    sample_texts = [
        """
        Hi, I'm John Smith and I'd like to book a deluxe room for 2 guests. 
        We're checking in on December 15th, 2024 and checking out on December 18th, 2024.
        We have a special request for a room with a view and late checkout if possible.
        """,
        """
        Booking request for Sarah Johnson, 1 guest, standard room.
        Arrival: 2024-01-10, Departure: 2024-01-12.
        Please arrange for vegetarian meals and airport pickup.
        """,
        """
        Need a suite for next weekend, 4 people, family vacation.
        The guest name is Michael Brown. We'll need cribs for 2 children.
        """,
    ]

    # Note: You'll need to set your OpenAI API key
    # os.environ['OPENAI_API_KEY'] = 'your-api-key-here'

    for i, text in enumerate(sample_texts, 1):
        try:
            print(f"\nExample {i}:")
            print(f"Input: {text.strip()}")

            # Extract information (uncomment when you have API key)
            # result = extract_hotel_info_sync(text)
            # print(f"Extracted: {result}")
            # print(f"JSON: {result.model_dump_json(indent=2)}")

        except Exception as e:
            print(f"Error: {e}")
