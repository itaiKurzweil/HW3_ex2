import requests
import random
import string
from joblib import Parallel, delayed


BASE_URL = "https://hw3as2-app.icycoast-edc4c18b.westus2.azurecontainerapps.io"

def random_string(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def send_event():
    """Send a single event to the analytics server with random data."""
    user_id = random_string(6)
    event_name = random_string(6)

    payload = {
        "userid": user_id,
        "eventname": event_name
    }
    response = requests.post(f"{BASE_URL}/process_event/", json=payload)
    return response.status_code, response.text

def main():
    Parallel(n_jobs=10, backend="threading")(delayed(send_event)() for _ in range(100))
    print("Sent 1000 events in parallel.")

if __name__ == "__main__":
    main()

