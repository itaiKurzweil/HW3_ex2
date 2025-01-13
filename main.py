from fastapi import FastAPI, HTTPException , Body
from pydantic import BaseModel
from typing import Dict, List , Any
from datetime import datetime, timedelta
import sqlite3

# FastAPI app instance
app = FastAPI()

# Database setup
DATABASE = "analytics.db"

# Ensure the database and table are created
def initialize_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            eventtimestamputc TEXT NOT NULL,
            userid TEXT NOT NULL,
            eventname TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

initialize_db()

# Pydantic model for request body
class EventRequest(BaseModel):
    userid: str
    eventname: str

@app.post("/process_event", status_code=201)
async def process_event(event: EventRequest) -> Dict[str, Any]:
    """
    Save an event to the SQLite database.
    """
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()


        # Insert data into the database
        event_timestamp = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO events (eventtimestamputc, userid, eventname)
            VALUES (?, ?, ?)
        """, (event_timestamp, event.userid, event.eventname))
        conn.commit()
        conn.close()

        # Return success message
        return {"message": "Event processed successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing event: {e}")

@app.post("/get_reports", status_code=200)
async def get_reports(
    lastseconds: int = Body(..., embed=True),
    userid: str = Body(..., embed=True)
) -> Dict[str, List[Dict]]:
    """
    Retrieve all events for a given user within the last X seconds.
    """
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Calculate the time range
        now = datetime.utcnow()
        time_threshold = now - timedelta(seconds=lastseconds)
        time_threshold_str = time_threshold.isoformat()

        # Query the database for events
        cursor.execute("""
            SELECT eventtimestamputc, userid, eventname
            FROM events
            WHERE userid = ? AND eventtimestamputc >= ?
        """, (userid, time_threshold_str))
        rows = cursor.fetchall()
        conn.close()

        # Format the result
        events = [{"eventtimestamputc": row[0], "userid": row[1], "eventname": row[2]} for row in rows]
        return {"userid": userid, "events": events}

    except Exception as e:
        # Handle exceptions properly
        raise HTTPException(status_code=500, detail=f"Error retrieving reports: {e}")


