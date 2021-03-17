from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects import postgresql

from sqlalchemy import create_engine

import Applications

# declarative base class
Base = declarative_base()


engine = create_engine("postgresql+psycopg2://uscope:test@172.23.0.4/uscope")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

a = 0

for instance in session.query(Applications.Applications):
    print(instance)
