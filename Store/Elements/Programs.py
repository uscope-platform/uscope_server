# Copyright 2021 University of Nottingham Ningbo China
# Author: Filippo Savi <filssavi@gmail.com>
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

from sqlalchemy import Column, String, Integer, BigInteger
from .OrmBase import Base
from sqlalchemy.dialects import postgresql


class Programs(Base):
    __tablename__ = 'programs'

    VersionTableName = 'programs'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    content = Column(String)
    type = Column(String)
    hex = Column(postgresql.ARRAY(BigInteger))
    build_settings = Column(postgresql.JSONB)
    def __repr__(self):
        return "<Program(id='%s', name='%s', content='%s')>" % (
                             self.id, self.name, self.content)


def program_from_row(row):
    return {'id': row.id, 'name': row.name, 'program_content': row.content,
            'program_type': row.type, 'hex': row.hex, 'build_settings': row.build_settings}
