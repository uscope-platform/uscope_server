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

from sqlalchemy import Column, String
from .OrmBase import Base
from sqlalchemy.dialects import postgresql


class Peripherals(Base):
    __tablename__ = 'peripherals'

    VersionTableName = 'Peripherals'

    name = Column(String, primary_key=True)
    image = Column(String)
    version = Column(String)
    registers = Column(postgresql.JSONB)

    def __repr__(self):
        return "<Peripheral(name='%s', image='%s', version='%s')>" % (
                             self.name, self.image, self.version)


def peripheral_from_row(row):
    return {'peripheral_name': row.name, 'image': row.image, 'version': row.version, 'registers': row.registers}
