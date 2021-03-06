import json
import time
import uuid

import sqlalchemy
from sqlalchemy.dialects import postgresql


_engine = None
_conn = None
_metadata = sqlalchemy.MetaData()


def initdb(uri):
    global _engine, _conn
    _engine = sqlalchemy.create_engine(uri)
    _conn = _engine.connect()


def createdb():
    _metadata.create_all(_engine)


def dropdb():
    _metedata.drop_all(_engine)


class Model:
    def save(self, statement):
        _conn.execute(statement)


class Event(Model):
    _table = sqlalchemy.Table(
        'events',
        _metadata,
        sqlalchemy.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sqlalchemy.Column('location_name', sqlalchemy.String),
        sqlalchemy.Column('image_url', sqlalchemy.String),
        sqlalchemy.Column('lattitude', sqlalchemy.Float),
        sqlalchemy.Column('longitude', sqlalchemy.Float),
        sqlalchemy.Column('comments', sqlalchemy.String),
        sqlalchemy.Column('created', sqlalchemy.Integer),
    )

    def __init__(self, location_name, image_url, lattitude=None, longitude=None,
                 comments=None, id=None, created=None):
        self.id = id
        self.image_url = image_url
        self.location_name = location_name
        self.lattitude = lattitude
        self.longitude = longitude
        self.comments = comments
        self.created = created or time.time()

    def save(self):
        id = uuid.uuid4()
        ev = Event._table.insert().values(
            location_name=self.location_name,
            id=id,
            image_url=self.image_url,
            lattitude=self.lattitude,
            longitude=self.longitude,
            comments=self.comments,
            created=self.created
        )
        self.id = id
        super().save(ev)

    @staticmethod
    def all(offset=None, limit=None, area=None):
        query = Event._table.select().order_by(
            Event._table.c.created.desc()
        )

        if area is not None:
            min_lon, max_lon, min_lat, max_lat = (
                float(v) for v in area.split(',')
            )
            query = query.where(
                Event._table.c.longitude > min_lon
            ).where(
                Event._table.c.longitude < max_lon
            ).where(
                Event._table.c.lattitude > min_lat
            ).where(
                Event._table.c.lattitude < max_lat
            )
        
        query = query.offset(offset).limit(limit)

        cur = _conn.execute(query)
        events = [ev for ev in cur]
        cols = cur.keys()
        return [
            Event(**{cols[idx]: val for idx, val in enumerate(ev)})
            for ev in events
        ]
