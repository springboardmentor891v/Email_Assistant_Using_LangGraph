from googleapiclient.errors import HttpError
def create_event(calendar_service, summary, start_dt, end_dt, attendees=None):
    if not summary or not start_dt or not end_dt:
        print("Skipping event creation: missing required info")
        return None

    event = {
        "summary": summary,
        "start": {"dateTime": start_dt, "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": end_dt, "timeZone": "Asia/Kolkata"},
    }

    if attendees:
        event["attendees"] = [{"email": email} for email in attendees]

    try:
        created_event = calendar_service.events().insert(
            calendarId='primary', body=event).execute()
        print("Event created:", created_event.get('htmlLink'))
        return created_event
    except HttpError as error:
        print("Calendar API error:", error)
        return None
