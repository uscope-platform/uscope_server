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

from sqlalchemy import Column, String, ARRAY, Integer
from .OrmBase import Base
from sqlalchemy.dialects import postgresql


class Applications(Base):
    __tablename__ = 'applications'

    VersionTableName = 'Applications'

    id = Column(Integer, primary_key=True)
    application_name = Column(String)
    bitstream = Column(String)
    clock_frequency = Column(String)
    channels = Column(postgresql.JSONB)
    channel_groups = Column(postgresql.JSONB)
    initial_registers_values = Column(postgresql.JSONB)
    macro = Column(postgresql.JSONB)
    parameters = Column(postgresql.JSONB)
    peripherals = Column(postgresql.JSONB)
    miscellaneous = Column(postgresql.JSONB)
    soft_cores = Column(postgresql.JSONB)
    filters = Column(postgresql.JSONB)
    programs = Column(ARRAY(String))
    scripts = Column(ARRAY(String))
    pl_clocks = Column(postgresql.JSONB)

    def __repr__(self):
        return "<Application(id='%s' application_name='%s', bitstream='%s')>" % ( self.id, self.application_name, self.bitstream)


def application_from_row(row: Applications):
    app = {
        'id': row.id,
        'application_name': row.application_name,
        'bitstream': row.bitstream,
        'clock_frequency': row.clock_frequency,
        'channels': row.channels,
        'channel_groups': row.channel_groups,
        'initial_registers_values': row.initial_registers_values,
        'macro': row.macro,
        'parameters': row.parameters,
        'peripherals': row.peripherals,
        'soft_cores': row.soft_cores,
        'filters': row.filters,
        'scripts': row.scripts,
        'programs': row.programs,
        'miscellaneous': row.miscellaneous,
        'pl_clocks': row.pl_clocks
    }

    return app

