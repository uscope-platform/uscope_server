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


class Bitstreams(Base):
    __tablename__ = 'bitstreams'

    VersionTableName = 'bitstreams'

    id = Column(Integer, primary_key=True)
    path = Column(String)


    def __repr__(self):
        return "<Script(id='%s', path='%s')>" % (
                             self.id, self.path)

def bitstream_from_row(row):
    return {'id': row.id, 'path': row.path}