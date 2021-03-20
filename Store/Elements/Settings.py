from sqlalchemy import Column, String, ForeignKey
from .OrmBase import Base
from sqlalchemy.dialects import postgresql


class Settings(Base):
    __tablename__ = 'app_settings'

    name = Column(String, primary_key=True)
    user = Column(String, ForeignKey('users.username'))
    value = Column(postgresql.JSONB)

    def __repr__(self):
        return "<Setting(name='%s', value='%s, instance='%s')>" % (self.name, self.value, self.instance_id)


class SettingsDatabase:

    def __init__(self, session):
        self.Session = session

    def get_value(self, name, user):
        with self.Session() as session:
            with session.begin():
                res = session.query(Settings).filter_by(name=name, user=user).first()
                return res.value

    def set_value(self, name, value, user):

        item = Settings(name=name, value=value, user=user)
        with self.Session() as session:
            with session.begin():
                setting = session.query(Settings).filter_by(name=name, user=user).first()
                if setting:
                    setting.value = value
                else:
                    session.add(item)

    def clear_settings(self):
        with self.Session() as session:
            with session.begin():
                session.query(Settings).delete()

    def dump(self):
        return []


    def restore(self,data):
        pass