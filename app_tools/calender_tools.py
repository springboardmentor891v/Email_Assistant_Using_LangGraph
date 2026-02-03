# tools/calendar_tools.py


def create_event(calendar_service, title, description, start_dt, end_dt):
    event = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start_dt, "timeZone": "UTC"},
        "end": {"dateTime": end_dt, "timeZone": "UTC"}
    }

    if has_conflict(calendar_service, start_dt, end_dt):
        print("🚫 Conflict detected! Event cannot be created.")
        return None

    created = calendar_service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    print("✅ Calendar event created")
    print("🔗", created.get("htmlLink"))
    return created



from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")
UTC = pytz.utc


def to_utc(dt_str: str) -> str:
    # Handle Z suffix (UTC indicator) properly
    if dt_str.endswith("Z"):
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    else:
        dt = datetime.fromisoformat(dt_str)
        # If naive → assume IST
        if dt.tzinfo is None:
            dt = IST.localize(dt)

    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def has_conflict(calendar_service, start_dt: str, end_dt: str) -> bool:
    """
    Returns True if ANY existing calendar event overlaps
    the given start/end window.
    """

    time_min = to_utc(start_dt)
    time_max = to_utc(end_dt)

    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "items": [{"id": "primary"}]
    }

    response = calendar_service.freebusy().query(body=body).execute()

    busy_slots = response["calendars"]["primary"]["busy"]

    # 🔥 THIS is the actual conflict check
    return len(busy_slots) > 0



from datetime import timedelta

def suggest_free_slots(calendar_service, date_str):
    start_of_day = f"{date_str}T09:00:00"
    end_of_day = f"{date_str}T18:00:00"

    body = {
        "timeMin": to_utc(start_of_day),
        "timeMax": to_utc(end_of_day),
        "items": [{"id": "primary"}]
    }

    response = calendar_service.freebusy().query(body=body).execute()
    busy = response["calendars"]["primary"]["busy"]

    slots = []
    # Create timezone-aware cursor in IST for display
    cursor = datetime.fromisoformat(start_of_day)
    if cursor.tzinfo is None:
        cursor = IST.localize(cursor)
    
    end_cursor = datetime.fromisoformat(end_of_day)
    if end_cursor.tzinfo is None:
        end_cursor = IST.localize(end_cursor)

    for b in busy:
        # Parse UTC timestamps with proper timezone handling
        busy_start = datetime.fromisoformat(b["start"].replace("Z", "+00:00")).astimezone(IST)
        busy_end = datetime.fromisoformat(b["end"].replace("Z", "+00:00")).astimezone(IST)
        
        # Find all 1-hour free slots before this busy period
        while cursor + timedelta(hours=1) <= busy_start and len(slots) < 3:
            slots.append(cursor.strftime("%H:%M"))
            cursor += timedelta(hours=1)
        
        # Move cursor to end of busy period
        cursor = max(cursor, busy_end)

    # Add remaining free slots after last busy period
    while cursor + timedelta(hours=1) <= end_cursor and len(slots) < 3:
        slots.append(cursor.strftime("%H:%M"))
        cursor += timedelta(hours=1)

    return slots[:3]
