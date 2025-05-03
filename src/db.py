from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Library(db.Model):
    """
    A class representing a table of libraries in SQLAlchemy.
    :param db: Instance of a SQLAlchemy database model.
    """

    __tablename__ = 'libraries'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    hours = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    general_availability = db.Column(db.Float, nullable=True)
    external_id = db.Column(db.Integer, nullable=True)

    rooms = db.relationship('Room', backref='library', cascade="all, delete")
    library_reports = db.relationship('LibraryReport', backref='library', cascade="all, delete")

    def serialize(self):
        """
        Serializes this instance to a JSON.
        :return: A JSON-serializable object.
        """
        return {
            'id': self.id,
            'name': self.name,
            'hours': self.hours,
            'location': self.location,
            'general_availability': self.general_availability,
            'bookable_rooms': [r.serialize() for r in self.rooms if r.external_id is not None],
            'general_rooms': [r.serialize() for r in self.rooms if r.external_id is None],
            'library_reports': [ls.serialize() for ls in self.library_reports]
        }


class Room(db.Model):
    """
    A class representing a table of rooms in SQLAlchemy.
    :param db: Instance of a SQLAlchemy database model.
    """
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.Integer, nullable=True)
    library_id = db.Column(db.Integer, db.ForeignKey('libraries.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    is_bookable = db.Column(db.Boolean, nullable=True)
    availability = db.Column(db.Float, nullable=True)

    reports = db.relationship('RoomReport', backref='room', cascade="all, delete")

    def serialize(self):
        """
        Serializes this instance to a JSON.
        :return: A JSON-serializable object.
        """
        return {
            'id': self.id,
            "external_id": self.external_id,
            'library_id': self.library_id,
            'name': self.name,
            'floor': self.floor,
            "is_bookable": self.is_bookable,
            "availability": self.availability,
            "reports": [r.serialize() for r in self.reports]
        }

class LibraryReport(db.Model):
    """
    A class representing a table of reports in SQLAlchemy.
    :param db: Instance of a SQLAlchemy database model.
    """
    __tablename__ = 'lib_reports'

    id = db.Column(db.Integer, primary_key=True)
    libraries_id = db.Column(db.Integer, db.ForeignKey('libraries.id'), nullable=False)
    fullness = db.Column(db.Float, nullable=False)
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def serialize(self):
        """
        Serializes this instance to a JSON.
        :return: A JSON-serializable object.
        """
        return {
            'id': self.id,
            'libraries_id': self.libraries_id,
            'fullness': self.fullness,
            'time_stamp': self.time_stamp.isoformat()
        }

class RoomReport(db.Model):
    """
    A class representing a table of reports in SQLAlchemy.
    :param db: Instance of a SQLAlchemy database model.
    """
    __tablename__ = 'room_reports'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    fullness = db.Column(db.Float, nullable=False)
    time_stamp = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def serialize(self):
        """
        Serializes this instance to a JSON.
        :return: A JSON-serializable object.
        """
        return {
            'id': self.id,
            'room_id': self.room_id,
            'fullness': self.fullness,
            'time_stamp': self.time_stamp.isoformat()
        }