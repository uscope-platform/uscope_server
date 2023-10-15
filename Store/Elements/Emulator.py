## Copyright 2023 Filippo Savi
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

from sqlalchemy import Column, String, Integer
from .OrmBase import Base
from sqlalchemy.dialects import postgresql


class Emulator(Base):
    __tablename__ = 'emulators'

    VersionTableName = 'Emulators'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    cores = Column(postgresql.JSONB)
    connections = Column(postgresql.JSONB)
    inputs = Column(postgresql.JSONB)
    outputs = Column(postgresql.JSONB)

    def __repr__(self):
        return "<Peripheral(name='%s')>" % self.name


def emulator_from_row(row):
    return {
        'id': row.id, 'name': row.name, 'cores': row.registers, 'connections': row.connections,
        'inputs': row.inputs, 'outputs': row.outputs
    }
