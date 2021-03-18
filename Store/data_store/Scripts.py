from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Scripts(Base):
    __tablename__ = 'scripts'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)
    content = Column(String)
    triggers = Column(String)

    def __repr__(self):
        return "<Script(id='%s', name='%s', triggers='%s', content='%s')>" % (
                             self.id, self.name, self.triggers, self.content)


class ScriptsStore:

    def __init__(self, sesssion):
        self.Session = sesssion

    def script_from_row(self, row):
        return {'id': row.id, 'name': row.name, 'path': row.path, 'script_content': row.content,
                'triggers': row.triggers}

    def get_script(self, id):
        try:
            with self.Session() as session:
                result = session.query(Scripts).filter_by(id=id).first()
            return self.script_from_row(result)
        except AttributeError:
            raise KeyError('Script Not Found')

    def get_scripts_dict(self):
        with self.Session() as session:
            with session.begin():
                result = session.query(Scripts).all()
                scripts = {}
                for row in result:
                    scripts[row.id] = self.script_from_row(row)
        return scripts

    def add_scripts(self, script):
        item = Scripts(id=script["id"], name=script['name'],
                       content=script['script_content'], triggers=script['triggers'])
        with self.Session() as session:
            with session.begin():
                session.add(item)
        pass

    def remove_scripts(self, script):
        try:
            with self.Session() as session:
                result = session.query(Scripts).filter_by(id=script).first()
        except AttributeError:
            raise KeyError('Script Not Found')

        with self.Session() as session:
            with session.begin():
                session.delete(result)
