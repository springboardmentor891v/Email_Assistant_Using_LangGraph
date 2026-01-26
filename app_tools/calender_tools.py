# tools/calendar_tools.py


def create_event(calendar_service, title, description, start_dt, end_dt):
    event = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start_dt, "timeZone": "UTC"},
        "end": {"dateTime": end_dt, "timeZone": "UTC"}
    }

    created = calendar_service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    print("✅ Calendar event created")
    print("🔗", created.get("htmlLink"))


def has_conflict(calendar_service, start_dt, end_dt):
    events_result = calendar_service.events().list(
        calendarId="primary",
        timeMin=start_dt,
        timeMax=end_dt,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])
    return len(events) > 0
