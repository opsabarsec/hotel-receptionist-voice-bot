import os
import json
from supabase import create_client, Client

SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_API_KEY"
TABLE_NAME = "hotel_reservations"  # Make sure this matches your Supabase table


def load_json(filename):
    with open(filename, "r") as f:
        return json.load(f)


def insert_into_supabase(supabase: Client, reservations):
    data = supabase.table(TABLE_NAME).insert(reservations).execute()
    print("Insertion results:", data)


def main():
    reservations = load_json("hotel_requests.json")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    # reservations is a list of dicts; can also insert one at a time if needed
    insert_into_supabase(supabase, reservations)
    print("All reservations from JSON inserted into Supabase.")


if __name__ == "__main__":
    main()
