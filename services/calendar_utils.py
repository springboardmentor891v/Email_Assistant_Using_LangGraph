from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")


#CHECK AVAILABILITY
def check_availability(calendar_service, start_dt, duration_minutes=60):
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=IST)

    end_dt = start_dt + timedelta(minutes=duration_minutes)

    # Convert to UTC for Google Calendar API
    utc_start = start_dt.astimezone(UTC)
    utc_end = end_dt.astimezone(UTC)

    events = calendar_service.events().list(
        calendarId='primary',
        timeMin=utc_start.isoformat(),
        timeMax=utc_end.isoformat(),
        singleEvents=True
    ).execute().get('items', [])

    return "busy" if events else "free"


#CREATE EVENT
def create_event(calendar_service, summary, start_dt, duration_minutes=60):
    # Ensure start_dt is IST aware
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=IST)

    end_dt = start_dt + timedelta(minutes=duration_minutes)

    event = {
        'summary': summary,
        'start': {
            'dateTime': start_dt.isoformat(),   # IST time preserved
            'timeZone': 'Asia/Kolkata'          # 🔥 CRITICAL FIX
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': 'Asia/Kolkata'
        }
    }

    created = calendar_service.events().insert(
        calendarId='primary',
        body=event
    ).execute()

    return created.get('htmlLink')


# FREE SLOT FINDER
def get_free_slots_for_day(calendar_service, date_obj, duration_minutes=60):
    start_of_day = datetime.combine(date_obj, datetime.min.time()).replace(hour=9, tzinfo=IST)
    end_of_day = start_of_day.replace(hour=18)

    utc_start = start_of_day.astimezone(UTC)
    utc_end = end_of_day.astimezone(UTC)

    events = calendar_service.events().list(
        calendarId='primary',
        timeMin=utc_start.isoformat(),
        timeMax=utc_end.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute().get('items', [])

    busy_ranges = []
    for event in events:
        start = datetime.fromisoformat(event['start']['dateTime'].replace("Z", "+00:00"))
        end = datetime.fromisoformat(event['end']['dateTime'].replace("Z", "+00:00"))
        busy_ranges.append((start, end))

    free_slots = []
    current = start_of_day

    while current + timedelta(minutes=duration_minutes) <= end_of_day:
        slot_end = current + timedelta(minutes=duration_minutes)

        current_utc = current.astimezone(UTC)
        slot_end_utc = slot_end.astimezone(UTC)

        clash = any(start < slot_end_utc and end > current_utc for start, end in busy_ranges)

        if not clash:
            free_slots.append(current)

        current += timedelta(minutes=30)

    return free_slots[:2]
