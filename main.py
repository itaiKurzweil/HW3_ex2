from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
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
