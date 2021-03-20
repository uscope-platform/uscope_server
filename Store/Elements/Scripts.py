from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Scripts(Base):
    __tablename__ = 'scripts'

    VersionTableName = 'scripts'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)
    content = Column(String)
    triggers = Column(String)

    def __repr__(self):
        return "<Script(id='%s', name='%s', triggers='%s', content='%s')>" % (
                             self.id, self.name, self.triggers, self.content)

def script_from_row(row):
    return {'id': row.id, 'name': row.name, 'path': row.path, 'script_content': row.content,
            'triggers': row.triggers}