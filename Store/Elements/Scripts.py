# Copyright 2021 University of Nottingham Ningbo China
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from sqlalchemy import Column, String, Integer
from .OrmBase import Base


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