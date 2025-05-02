from db import db, Library, Room, LibraryReport, RoomReport
from flask import Flask, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)
db_filename = "libraries.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

def success_response(data, code=200):
    """
    Helper function for returning success response
    :param data: a json object
    :param code: a code representing the result of an action
    :return: JSON object from the DB with a specific code
    """
    return json.dumps(data), code

def error_response(error, code=404):
    """
    Helper function for returning success response
    :param error: a json object
    :param code: a code representing the result of an action
    :return: JSON object from the DB with a specific code
    """
    return json.dumps({"error": error}), code

@app.route("/api/libraries/", methods=["GET"])
def get_libraries():
    """
    Retrieves all the libraries from the db using SqlAlchemy.
    :return: A JSON object from the DB representing all libraries
    """

    libraries = Library.query.all()
    return success_response({"libraries": [l.serialize() for l in libraries]})

@app.route("/api/libraries/<int:library_id>/", methods=["GET"])
def get_library(library_id):
    """
    Retrieves a specific library from the db using SqlAlchemy.
    :param library_id: An integer representing the library id
    :return: A JSON object from the DB representing a specific library
    """
    library = Library.query.filter_by(id=library_id).first()

    if library is None:
        return error_response("Library not found", 404)

    return success_response(library.serialize())

@app.route("/api/libraries/", methods=["POST"])
def create_library():
    body = json.loads(request.data)
    name = body.get("name")
    hours = body.get("hours")
    location = body.get("location")

    if name is None:
        return error_response("Name is required", 400)
    if hours is None:
        return error_response("Hours is required", 400)
    if location is None:
        return error_response("Location is required", 400)

    new_library = Library(name=name, hours=hours, location=location)
    db.session.add(new_library)
    db.session.commit()
    return success_response(new_library.serialize(), 201)

@app.route("/api/libraries/<int:library_id>/rooms/", methods=["POST"])
def add_room(library_id):
    """
    Adds a new room to a specific library in the db using SqlAlchemy.
    :param library_id: An integer representing the library id
    :return: A JSON object from the DB representing a new room
    """
    body = json.loads(request.data)
    name = body.get("name")
    floor = body.get("floor")
    external_id = body.get("external_id")
    is_bookable = body.get("is_bookable")

    if name is None:
        return error_response("Name is required", 400)
    if floor is None:
        floor = -1

    library = Library.query.filter_by(id=library_id).first()
    if library is None:
        return error_response("Library not found", 404)

    room = Room(name=name, floor=floor, library=library, external_id=external_id, is_bookable=is_bookable)
    db.session.add(room)
    db.session.commit()
    return success_response(room.serialize(), 201)

@app.route("/api/rooms/", methods=["GET"])
def get_rooms():
    """
    Retrieves all the rooms from the db using SqlAlchemy.
    :return: A JSON object from the DB representing all rooms
    """
    rooms = Room.query.all()
    return success_response({"Rooms": [r.serialize() for r in rooms]})

@app.route("/api/rooms/<int:room_id>/", methods=["GET"])
def get_room(room_id):
    """
    Retrieves a specific room from the db using SqlAlchemy.
    :param room_id: A integer representing the room id
    :return: A JSON object from the DB representing a specific room
    """
    room = Room.query.filter_by(id=room_id).first()

    if room is None:
        return error_response("Room not found", 404)

    return success_response(room.serialize())

@app.route("/api/libraries/<int:library_id>/reports/", methods=["POST"])
def create_library_report(library_id):
    """
    Creates a new library report from the db using SqlAlchemy.
    :param library_id: A integer representing the library id
    :return: A JSON object from the DB representing a new library
    """
    body = json.loads(request.data)
    fullness = body.get("fullness")

    if fullness is None:
        return error_response("Fullness is required", 400)

    library = Library.query.filter_by(id=library_id).first()

    if library is None:
        return error_response("Library not found", 404)

    library_report = LibraryReport(fullness=fullness, library=library)
    db.session.add(library_report)
    db.session.commit()
    return success_response(library_report.serialize(), 201)

@app.route("/api/libraries/<int:library_id>/reports/", methods=["GET"])
def get_library_reports(library_id):
    """
    Retrieves all the library reports from a specific library using the db using SqlAlchemy.
    :param library_id: an integer representing the library id
    :return: A JSON object from the DB representing all library reports
    """
    library = Library.query.filter_by(id=library_id).first()

    if library is None:
        return error_response("Library not found", 404)

    reports = LibraryReport.query.filter_by(libraries_id=library_id).all()

    return success_response({"reports": [r.serialize() for r in reports]})

@app.route("/api/libraries/<int:library_id>/reports/<int:report_id>/", methods=["DELETE"])
def delete_library_report(library_id, report_id):
    """
    Deletes a specific library report from the db using SqlAlchemy.
    :param library_id: A integer representing the library id
    :param report_id: A integer representing the report id
    :return: A JSON object from the DB representing a specific library report
    """
    library = Library.query.filter_by(id=library_id).first()
    if library is None:
        return error_response("Library not found", 404)
    report = LibraryReport.query.filter_by(id=report_id).first()
    if report is None:
        return error_response("Report not found", 404)
    db.session.delete(report)
    db.session.commit()
    return success_response(report.serialize())

@app.route("/api/rooms/<int:room_id>/reports/", methods=["POST"])
def create_room_report(room_id):
    """
    Creates a new room report from the db using SqlAlchemy.
    :param room_id: A integer representing the library id
    :return: A JSON object from the DB representing a new room report
    """
    body = json.loads(request.data)
    fullness = body.get("fullness")

    if fullness is None:
        return error_response("Fullness is required", 400)

    room = Room.query.filter_by(id=room_id).first()

    if room is None:
        return error_response("Room not found", 404)

    room_report = RoomReport(fullness=fullness, room=room)
    db.session.add(room_report)
    db.session.commit()
    return success_response(room_report.serialize(), 201)

@app.route("/api/rooms/<int:room_id>/reports/", methods=["GET"])
def get_room_reports(room_id):
    """
    Retrieves all the room reports from a specific library using the db using SqlAlchemy.
    :param room_id: an integer representing the library id
    :return: A JSON object from the DB representing all library reports
    """
    room = Room.query.filter_by(id=room_id).first()

    if room is None:
        return error_response("Room not found", 404)

    reports = RoomReport.query.filter_by(room_id=room_id).all()

    return success_response({"reports": [r.serialize() for r in reports]})

@app.route("/api/rooms/<int:room_id>/reports/<int:report_id>/", methods=["DELETE"])
def delete_room_report(room_id, report_id):
    """
    Deletes a specific room report from the db using SqlAlchemy.
    :param room_id: A integer representing the library id
    :param report_id: A integer representing the report id
    :return: A JSON object from the DB representing a specific room report
    """
    room = Room.query.filter_by(id=room_id).first()
    if room is None:
        return error_response("Room not found", 404)
    report = RoomReport.query.filter_by(id=report_id).first()
    if report is None:
        return error_response("Report not found", 404)
    db.session.delete(report)
    db.session.commit()
    return success_response(report.serialize())

@app.route("/api/libraries/<int:library_id>/", methods=["DELETE"])
def delete_library(library_id):
    """
    Deletes a specific library report from the db using SqlAlchemy.
    :param library_id: A integer representing the library id
    :return: A JSON object from the DB representing a specific library report
    """
    library = Library.query.filter_by(id=library_id).first()
    if library is None:
        return error_response("Library not found", 404)

    db.session.delete(library)
    db.session.commit()
    return success_response(library.serialize())


@app.route("/api/rooms/<int:room_id>/", methods=["DELETE"])
def delete_room(room_id):
    """
    Deletes a specific room report from the db using SqlAlchemy.
    :param room_id: A integer representing the library id
    :return: A JSON object from the DB representing a specific room report
    """
    room = Room.query.filter_by(id=room_id).first()
    if room is None:
        return error_response("Room not found", 404)

    db.session.delete(room)
    db.session.commit()
    return success_response(room.serialize())

@app.route("/api/libraries/<int:library_id>/", methods=["PUT"])
def update_library(library_id):
    """
    Updates a specific library report from the db using SqlAlchemy.
    :param library_id: A integer representing the library id
    :return: A JSON object from the DB representing a specific library report
    """
    library = Library.query.filter_by(id=library_id).first()
    if library is None:
        return error_response("Library not found", 404)

    body = json.loads(request.data)

    name = body.get("name")
    hours = body.get("hours")
    location = body.get("location")
    fullness = body.get("fullness")
    external_id = body.get("external_id")

    if name is not None:
        library.name = name
    if hours is not None:
        library.hours = hours
    if location is not None:
        library.location = location
    if fullness is not None:
        library.general_availability = fullness
    if external_id is not None:
        library.external_id = external_id

    db.session.commit()
    return success_response(library.serialize())

@app.route("/api/rooms/<int:room_id>/", methods=["PUT"])
def update_room(room_id):
    """
    Updates a specific room report from the db using SqlAlchemy.
    :param room_id: An integer representing the library id
    :return: A JSON object from the DB representing a specific room report
    """
    room = Room.query.filter_by(id=room_id).first()
    if room is None:
        return error_response("Room not found", 404)

    body = json.loads(request.data)

    name = body.get("name")
    floor = body.get("floor")
    availability = body.get("availability")
    is_bookable = body.get("is_bookable")

    if name is not None:
        room.name = name
    if floor is not None:
        room.floor = floor
    if availability is not None:
        room.availability = availability
    if is_bookable is not None:
        room.is_bookable = is_bookable


    db.session.commit()
    return success_response(room.serialize())

@app.route("/api/rooms/external/<int:external_id>/", methods=["PUT"])
def update_room_by_external_id(external_id):
    """
    Updates a specific room report from the db using SqlAlchemy.
    :param external_id: An integer representing the external id
    :return: A JSON object from the DB representing a specific room
    """

    room = Room.query.filter_by(external_id=external_id).first()
    if room is None:
        return error_response("Room not found", 404)

    data = json.loads(request.data)
    is_bookable = data.get("is_bookable")

    room.is_bookable = is_bookable
    db.session.commit()
    return success_response(room.serialize())

@app.route("/api/libraries/external/<int:external_id>/", methods=["PUT"])
def update_library_by_external_id(external_id):
    library = Library.query.filter_by(external_id=external_id).first()
    if library is None:
        return error_response("Library not found", 404)

    data = json.loads(request.data)

    hours = data.get("hours")

    library.hours = hours
    db.session.commit()
    return success_response(library.serialize())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)