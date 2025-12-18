from dataclasses import dataclass
from pathlib import Path
from typing import Literal

__all__ = [
    "Column",
    "QueryInformation",
    "QueryAlias",
    "QueryLoadProcedures",
    "Dimension",
    "DimensionJoin",
    "TableDefinitionColumn",
    "TableDefinition",
]


@dataclass
class QueryLoadProcedures:
    sequence: int
    identifier: str


@dataclass
class QueryAlias:
    name: str
    type: Literal["primary", "non_primary"]


@dataclass
class QueryInformation:
    name: str
    select_file_path: Path
    sequence: int
    aliases: list[QueryAlias]
    query: str


@dataclass
class Column:
    column_name: str
    data_type_full: str
    type: str
    nullable: bool


@dataclass
class DimensionJoin:
    delta_column: str
    dimension_column = str


@dataclass
class Dimension:
    dimension: str
    role_playing: str
    dimension_joins = list[DimensionJoin]


@dataclass
class TableDefinitionColumn:
    column_name: str
    data_type: str
    character_maximum_length: int
    numeric_precision: int
    numeric_scale: int
    nullable: bool
    business_key: bool


@dataclass
class TableDefinition:
    schema: str
    table_identifier: str
    columns: list[TableDefinitionColumn]
