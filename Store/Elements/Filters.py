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

from sqlalchemy import Column, String, Integer, ARRAY, Float
from .OrmBase import Base
from sqlalchemy.dialects import postgresql


class Filters(Base):
    __tablename__ = 'filters'

    VersionTableName = 'filters'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    parameters = Column(postgresql.JSONB)
    ideal_taps = Column(ARRAY(Float))
    quantized_taps = Column(ARRAY(Integer))

    def __repr__(self):
        return "<Filter(id='%s', name='%s')>" % (
                             self.id, self.path)


def filter_from_row(row):
    return {'id': row.id,
            'name': row.name,
            'parameters': row.parameters,
            'ideal_taps': row.ideal_taps,
            'quantized_taps': row.quantized_taps
            }
