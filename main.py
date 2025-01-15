from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, List, Any
from datetime import datetime, timedelta
import sqlite3

# FastAPI app instance
app = FastAPI()


class EventRequest(BaseModel):
    userid: str
    eventname: str

class ReportRequest(BaseModel):
    userid: str
    lastseconds: int


DATABASE = "analytics.db"

def initialize_db():
    """Returns a connection to the SQLite database with row_factory set."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def generate_table():
    """Create the 'events' table if it doesn't exist."""
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


@app.on_event("startup")
def startup_event():
    generate_table()


@app.post("/process_event")
async def process_event(event: EventRequest) -> Dict[str, Any]:
    """Insert a new event record into the database."""
    event_timestamp = datetime.utcnow().isoformat()

    query = """
    INSERT INTO events (eventtimestamputc, userid, eventname)
    VALUES (?, ?, ?);
    """

    conn = initialize_db()
    cursor = conn.cursor()
    cursor.execute(query, (event_timestamp, event.userid, event.eventname))
    conn.commit()
    conn.close()

    return {"message": "Event processed successfully"}

@app.post("/get_reports")
async def get_reports(request: ReportRequest) -> Dict[str, Any]:
    """
    Return all events for a given userid in the last X seconds
    (where X = request.lastseconds).
    """
    now = datetime.utcnow()
    time_threshold = now - timedelta(seconds=request.lastseconds)
    time_threshold_str = time_threshold.isoformat()

    query = """
    SELECT eventtimestamputc, userid, eventname 
    FROM events
    WHERE userid = ? AND eventtimestamputc >= ?;
    """

    conn = initialize_db()
    cursor = conn.cursor()
    cursor.execute(query, (request.userid, time_threshold_str))
    rows = cursor.fetchall()
    conn.close()

    events = [
        {
            "eventtimestamputc": row["eventtimestamputc"],
            "userid": row["userid"],
            "eventname": row["eventname"]
        }
        for row in rows
    ]

    return {"events": events}
