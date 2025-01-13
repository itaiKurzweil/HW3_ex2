from fastapi import FastAPI, HTTPException , Body
from pydantic import BaseModel
from typing import Dict, List , Any
from datetime import datetime, timedelta
import sqlite3

# FastAPI app instance
app = FastAPI()

# Pydantic model for request body
class EventRequest(BaseModel):
    userid: str
    eventname: str

class EventResponse(BaseModel):
    lastseconds: int
    userid: str

# Database setup
DATABASE = "analytics.db"

# Ensure the database and table are created
def initialize_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def generate_table():
    conn = initialize_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        eventtimestamputc TEXT NOT NULL,
        userid TEXT NOT NULL,
        eventname TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

@app.post("/process_event")
async def process_event(event: EventRequest) -> Dict[str, Any]:
    event_timestamp = datetime.utcnow().isoformat()

    # Insert data into the database
    query = """
    INSERT INTO events (eventtimestamputc, userid, eventname)
    VALUES (?, ?, ?);
    """

    conn = initialize_db()
    cursor = conn.cursor()
    cursor.execute(query, (event_timestamp, event.userid, event.eventname))
    conn.commit()
    conn.close()

    # Return success message
    return {"message": "Event processed successfully"}

@app.post("/get_reports")
async def get_reports(request: EventRequest) -> Dict[str, Any]:

    # Calculate the time range
    now = datetime.utcnow()
    time_threshold = now - timedelta(seconds=request.lastseconds)
    time_threshold_str = time_threshold.isoformat()

    query = """
    SELECT * FROM events
    WHERE userid = ? AND eventtimestamputc >= ?;
    """

    conn = initialize_db()
    cursor = conn.cursor()
    cursor.execute(query, (request.userid, time_threshold_str))
    rows = cursor.fetchall()
    conn.close()

    events = [{"eventtimestamputc": row["eventtimestamputc"], "userid": row["userid"], "eventname": row["eventname"]} for row in rows]

    return {"events": events}



