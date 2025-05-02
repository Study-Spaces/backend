import requests
import datetime

ROOMS = {
    5647: ("Uris Library", "4B02"),
    5648: ("Uris Library", "4B03"),
    5649: ("Uris Library", "4B04"),
    174127: ("Uris Library", "Uris Privacy Pod"),
    30587: ("Uris Library", "108"),
    183113: ("Olin Library", "120A"),
    183114: ("Olin Library", "120B"),
    3845: ("Olin Library", "302"),
    105731: ("Olin Library", "303"),
    3846: ("Olin Library", "402"),
    105733: ("Olin Library", "403"),
    3847: ("Olin Library", "404"),
    105730: ("Olin Library", "602"),
    105734: ("Olin Library", "603"),
    36201: ("Olin Library", "B30"),
    36202: ("Olin Library", "B30"),
    110724: ("Catherwood Library", "136A"),
    110725: ("Catherwood Library", "136B"),
    110726: ("Catherwood Library", "136C"),
    19594: ("Catherwood Library", "230A"),
    3837: ("Catherwood Library", "231A"),
    3838: ("Catherwood Library", "231B"),
    18604: ("Mann Library", "100"),
    18605: ("Mann Library", "102"),
    18628: ("Mann Library", "Stone Classroom"),
    18606: ("Mann Library", "Lobby Tabling Space 1"),
    18607: ("Mann Library", "Lobby Tabling Space 2"),
    18630: ("Mann Library", "Bissett Collaborative Workstation 1"),
    18631: ("Mann Library", "Bissett Collaborative Workstation 2"),
    52496: ("Mann Library", "260"),
    18632: ("Mann Library", "261"),
    20087: ("Mann Library", "270"),
    52497: ("Mann Library", "360"),
    52498: ("Mann Library", "361"),
    52495: ("Mann Library", "370"),
    18635: ("Mann Library", "Interview Room"),
    172082: ("Mann Library", "Mann Privacy Pod"),
    176569: ("Mann Library", "Sensory Study Room"),
    20088: ("Mann Library", "271"),
    20089: ("Mann Library", "272"),
    52485: ("Mann Library", "273"),
    52486: ("Mann Library", "274"),
    52487: ("Mann Library", "276"),
    52500: ("Mann Library", "277"),
    52488: ("Mann Library", "278"),
    52489: ("Mann Library", "280"),
    52490: ("Mann Library", "371"),
    52491: ("Mann Library", "377"),
    52492: ("Mann Library", "378"),
    52493: ("Mann Library", "381"),
    105863: ("Mann Library", "372"),
    105862: ("Mann Library", "373"),
    105861: ("Mann Library", "374"),
    105860: ("Mann Library", "376"),
    105600: ("Mann Library", "380"),
    107079: ("Mann Library", "Grad Group Study Desk"),
    21969: ("Carpenter Library", "103C"),
    21970: ("Carpenter Library", "103D")
}

LIBRARY_IDS = {
    "Uris Library": "94",
    "Olin Library": "94",
    "Mann Library": "96",
    "Catherwood Library": "527",
    "Carpenter Library": "3403"
}



BASE_URL = "http://localhost:8000"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://spaces.library.cornell.edu/",
    "Origin": "https://spaces.library.cornell.edu"
}

HOURS = {
    "Uris Library": [{"monday":"8am - 11pm", "tuesday":"8am - 11pm",
                      "wednesday":"8am - 11pm", "thursday":"8am - 11pm",
                      "friday":"8am - 5pm", "saturday":"12pm - 5pm",
                      "sunday": "12pm - 11pm"}],
    "Olin Library": [{"monday":"8am – 12am", "tuesday":"8am – 12am",
                      "wednesday":"8am – 12am", "thursday":"8am – 12am",
                      "friday":"8am – 6pm", "saturday":"10am – 6pm",
                      "sunday": "10am – 12am"}],
    "Mann Library": [{"monday":"8am – 8pm", "tuesday":"8am – 8pm",
                      "wednesday":"8am – 10pm", "thursday":"8am – 10pm",
                      "friday":"8am – 6pm", "saturday":"12pm – 6pm",}],
    "Catherwood Library": [{"monday":"8am – 8pm", "tuesday":"8am – 8pm",
                            "wednesday":"8am – 8pm","thursday":"8am – 8pm",
                            "friday":"8am – 5pm"}],
    "Carpenter Library": [{"monday":"24 Hours", "tuesday":"24 Hours",
                           "wednesday":"24 Hours", "thursday":"24 Hours",
                           "friday":"24 Hours", "saturday":"24 Hours",
                           "sunday":"24 Hours"}]
}


def fetch_slots(library_id):
    """
    Fetches available slots for bookable rooms across Cornell libraries using the Cornell LibCal API.
    :param library_id: An Integer representing the libraries ID.
    :return: A list of available slot dictionaries from the response JSON. If no slots are found or the response is malformed, returns an empty list.
    """

    now = datetime.datetime.now()
    later = now + datetime.timedelta(hours=3)

    payload = {
        "lid": library_id,
        "start": now.isoformat(),
        "end": later.isoformat(),
        "pageIndex": "0",
        "pageSize": "5000"
    }

    response = requests.post(
        "https://spaces.library.cornell.edu/spaces/availability/grid",
        data=payload,
        headers=HEADERS
    )
    return response.json().get("slots", [])


def determine_availability(slots):
    """
    Checks which bookable rooms in a libray are currently checked out based on active time slots.
    :param slots: List of slot dicts, each with 'itemId', 'start', 'end', and 'className'.
    :return: Dict mapping item IDs to True (if checked out) or False (if not in use right now).
    """
    availability = {}
    now = datetime.datetime.now()

    for slot in slots:
        item_id = slot.get("itemId")
        start = datetime.datetime.fromisoformat(slot.get("start"))
        end = datetime.datetime.fromisoformat(slot.get("end"))
        class_name = slot.get("className")

        if start <= now <= end:
            availability[item_id] = (class_name == "s-lc-eq-checkout")

    return availability


def update_room(room_id, availability):
    """
    Updates the availability status of a room via an external API.
    :param room_id: An int representing the room ID.
    :param availability: Boolean indicating if the room is bookable, or None to reset status.
    """
    url = BASE_URL + "/api/rooms/external/" + str(room_id) + "/"
    if availability is None:
        payload = {
            "is_bookable": None,
            "availability": -1
        }
    else:
        payload = {
            "is_bookable": availability,
            "availability": -1
        }
    requests.put(url, json=payload, headers={"Content-Type": "application/json"})


def main():
    """
    Syncs room availability data with an external system by:

    1. Grouping rooms by their library.
    2. Fetching current slot data for each library.
    3. Determining which rooms are currently checked out.
    4. Updating each room's availability via an external API.
    """
    rooms_by_library = {}
    for room_id in ROOMS:
        room_info = ROOMS[room_id]
        library = room_info[0]
        if library not in rooms_by_library:
            rooms_by_library[library] = []
        rooms_by_library[library].append(room_id)

    for library_name in rooms_by_library:
        room_ids = rooms_by_library[library_name]
        library_id = LIBRARY_IDS.get(library_name)
        slots = fetch_slots(library_id)
        availability = determine_availability(slots)

        for room_id in room_ids:
            current_status = availability.get(room_id, None)
            update_room(room_id, current_status)


def calculate_general_room_availability():
    """
    Calculates and updates the average fullness of general (non-external) rooms based on recent usage reports.

    Process:
    1. Fetches all rooms from the API.
    2. Skips rooms that have an 'external_id' (they're managed externally).
    3. For each remaining room:
       - Fetches usage reports.
       - Filters reports to only those from the last 2 hours.
       - Averages the 'fullness' values from these recent reports.
    4. If there are recent reports:
       - Sends a PUT request to update the room's 'availability' field with the average fullness.
    """
    url = BASE_URL + "/api/rooms/"
    rooms_res = requests.get(url)
    rooms = rooms_res.json().get("Rooms", [])

    now = datetime.datetime.now()
    two_hours_ago = now - datetime.timedelta(hours=2)

    for room in rooms:
        if room["external_id"] is not None:
            continue

        room_id = room["id"]
        reports_res = requests.get(BASE_URL + "/api/rooms/" + str(room_id) + "/reports/")
        reports = reports_res.json().get("reports", [])

        recent_reports = []
        for report in reports:
            ts_str = report.get("time_stamp")

            if ts_str:
                ts = datetime.datetime.fromisoformat(ts_str)
                if ts >= two_hours_ago:
                    recent_reports.append(report)


        if recent_reports:
            total_fullness = 0
            for report in recent_reports:
                total_fullness += report["fullness"]

            avg = total_fullness / len(recent_reports)
        else:
            avg = None

        if avg is not None:
            requests.put(
                BASE_URL + "/api/rooms/" + str(room_id) + "/",
                json={"availability": avg},
                headers={"Content-Type": "application/json"}
            )
        else:
            requests.put(
                BASE_URL + "/api/rooms/" + str(room_id) + "/",
                json={"availability": None},
                headers={"Content-Type": "application/json"}
            )

def calculate_library_general_availability(k_general=10, k_library=10):
    """
    Calculates and updates the overall fullness (availability) of each library using a weighted average
    of recent general room reports, bookable room availability, and library-level reports.

    :param k_general: An integer that is a smoothing factor for weighting general room data vs. bookable room data.
    :param k_library: An integer that is a smoothing factor for weighting library-level reports vs. combined room data.
    """
    libraries_url = BASE_URL + "/api/libraries/"
    libraries_res = requests.get(libraries_url)
    libraries = libraries_res.json().get("libraries", [])

    now = datetime.datetime.now()
    two_hours_ago = now - datetime.timedelta(hours=2)

    for lib in libraries:
        general_rooms = lib.get("general_rooms", [])
        bookable_rooms = lib.get("bookable_rooms", [])

        library_id = LIBRARY_IDS.get(lib["name"])
        if library_id is not None:
            slots = fetch_slots(library_id)
        else:
            slots = []
        bookable_room_ids = []
        for room in bookable_rooms:
            external_id = room.get("external_id")
            if external_id is not None:
                bookable_room_ids.append(external_id)
        if len(slots) > 0 and len(bookable_room_ids) > 0:
            bookable_avg = calculate_bookable_room_window_availability(slots, bookable_room_ids)
        else:
            bookable_avg = None

        library_reports = lib.get("library_reports", [])


        general_availabilities = []
        for room in general_rooms:
            availability = room.get("availability")

            if isinstance(availability, (int,float)) and availability >= 0:
                general_availabilities.append(availability)

        n_general = len(general_availabilities)

        if n_general > 0:
            total = 0
            for value in general_availabilities:
                total += value
            general_reports_avg = total / n_general
        else:
            general_reports_avg = None

        lib_fullness_values = []
        for r in library_reports:
            fullness = r.get("fullness")
            ts_str = r.get("time_stamp")
            if ts_str and isinstance(fullness, (int, float)) and fullness >= 0:
                ts = datetime.datetime.fromisoformat(ts_str)
                if ts >= two_hours_ago:
                    lib_fullness_values.append(fullness)

        n_library = len(lib_fullness_values)

        if n_library > 0:
            total = 0
            for value in lib_fullness_values:
                total += value
            library_reports_avg = total / n_library
        else:
            library_reports_avg = None

        if general_reports_avg is not None and bookable_avg is not None:
            weight_general = n_general / (n_general + k_general)
            combined_report_avg = weight_general * general_reports_avg + (1 - weight_general) * bookable_avg
        elif general_reports_avg is not None:
            combined_report_avg = general_reports_avg
        elif bookable_avg is not None:
            combined_report_avg = bookable_avg
        else:
            combined_report_avg = None

        if library_reports_avg is not None and combined_report_avg is not None:
            weight_library = n_library / (n_library + k_library)
            final_avg = weight_library * library_reports_avg + (1 - weight_library) * combined_report_avg
        elif library_reports_avg is not None:
            final_avg = library_reports_avg
        elif combined_report_avg is not None:
            final_avg = combined_report_avg
        else:
            final_avg = None


        update_url = BASE_URL + "/api/libraries/" + str(lib["id"]) + "/"
        if final_avg is not None:
            print(f"{lib['name']}: {round(final_avg, 2)}")
        else:
            print(f"{lib['name']}: No data")

        requests.put(update_url, json={"fullness": final_avg}, headers={"Content-Type": "application/json"})

def calculate_bookable_room_window_availability(slots, room_ids):
    """
    Calculates a scaled average availability score (0–5) for a set of bookable rooms, based on the five hour slot data.
    :param slots: List of slot dictionaries, each with 'itemId' and 'className' fields.
    :param room_ids: List of bookable room external IDs to include in the calculation.
    :return: Average availability score (0–5), or None if no relevant data is found.
    """
    availability_per_room = {}
    for room_id in room_ids:
        availability_per_room[room_id] = []

    for slot in slots:
        room_id = slot.get("itemId")
        class_name = slot.get("className")

        if room_id in availability_per_room:
            if class_name == "s-lc-eq-checkout":
                availability_per_room[room_id].append(True)
            else:
                availability_per_room[room_id].append(False)

    room_avgs = []
    for room_id in availability_per_room:
        availabilities = availability_per_room[room_id]
        if len(availabilities) > 0:
            available_count = 0
            for is_available in availabilities:
                if is_available:
                    available_count += 1
            available_fraction = available_count / len(availabilities)
            room_avgs.append(available_fraction)

    if len(room_avgs) > 0:
        total = 0
        for value in room_avgs:
            total += value
        avg_availability = total / len(room_avgs)
        return avg_availability * 5
    else:
        return None

def determine_hours():
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    today = days[datetime.datetime.now().weekday()]

    for lib_name in LIBRARY_IDS:
        for hours_lib in HOURS:
            if hours_lib == lib_name:
                if today in HOURS[hours_lib][0]:
                    h = HOURS[hours_lib][0][today]
                    ext_id = LIBRARY_IDS[lib_name]
                    url = BASE_URL + "/api/libraries/external/" + ext_id + "/"
                    requests.put(url, json={"hours": h})
                break

if __name__ == "__main__":
    main()
    calculate_general_room_availability()
    calculate_library_general_availability(7,10)
    determine_hours()