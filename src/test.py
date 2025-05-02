import requests

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

LIBRARY_DETAILS = {
    "Mann Library": {
        "hours": "8am – 10pm",
        "location": "Ag Quad"
    },
    "Uris Library": {
        "hours": "8am – 11pm, (24/7)",
        "location": "Arts Quad"
    },
    "Olin Library": {
        "hours": "8am – 12am",
        "location": "Arts Quad"
    },
    "Catherwood Library": {
        "hours": "8am – 8pm",
        "location": "ILR School Campus"
    },
    "Carpenter Library": {
        "hours": "24 Hours",
        "location": "Carpenter Hall"
    }
}

BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}


def get_or_create_library(name):
    r = requests.get(f"{BASE_URL}/api/libraries/")
    if r.status_code != 200:
        raise Exception("Failed to fetch libraries")

    existing = r.json()
    for lib in existing["libraries"]:
        if lib["name"] == name:
            return lib["id"]

    print(f"Creating library: {name}")
    details = LIBRARY_DETAILS.get(name, {})
    payload = {
        "name": name,
        "hours": details.get("hours", "9am–9pm"),
        "location": details.get("location", "unknown")
    }
    r = requests.post(f"{BASE_URL}/api/libraries/", json=payload, headers=HEADERS)
    if r.status_code not in [200, 201]:
        raise Exception(f"Failed to create library {name}: {r.status_code} {r.text}")
    return r.json()["id"]


def create_room(library_id, external_id, name):
    payload = {
        "name": name,
        "external_id": external_id,
        "floor": -1,
        "is_bookable": True,
        "availability": -1
    }
    r = requests.post(f"{BASE_URL}/api/libraries/{library_id}/rooms/", json=payload, headers=HEADERS)
    if r.status_code in [200, 201]:
        print(f"✅ Created room {name} ({external_id})")
    elif r.status_code == 409:
        print(f"ℹ️ Room {external_id} already exists")
    else:
        print(f"❌ Failed to create room {name} ({external_id}): {r.status_code} {r.text}")


def main():
    libraries = {}
    for room_id, (library_name, room_name) in ROOMS.items():
        libraries.setdefault(library_name, []).append((room_id, room_name))

    for library_name, room_list in libraries.items():
        library_id = get_or_create_library(library_name)
        for room_id, room_name in room_list:
            create_room(library_id, room_id, room_name)


if __name__ == "__main__":
    main()
