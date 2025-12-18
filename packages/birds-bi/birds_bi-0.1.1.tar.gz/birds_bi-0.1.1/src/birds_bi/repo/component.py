from __future__ import annotations
from functools import cached_property

from pathlib import Path
from typing import TYPE_CHECKING, Literal
import json
from .models import *

if TYPE_CHECKING:
    from .repository import Repository

Category = Literal["help", "dim", "fact"]


class Component:
    def __init__(
        self, *, repo: "Repository", category: Category, component: str
    ) -> None:
        self._repo: Repository = repo
        self.category: Category = category
        self.component: str = component

    def __str__(self) -> str:
        return f"{self.category}.{self.component}"

    def __repr__(self) -> str:
        return f"{self.category}.{self.component}"

    @property
    def path(self) -> Path:
        # content/<category>/<component_component>
        return self._repo.content_path / self.category / self.component

    @cached_property
    def component_definition(self) -> dict[str, object]:
        path: Path = (
            self._repo.content_path
            / self.category
            / self.component
            / "deployment"
            / "component_definition.json"
        )

        if not path.is_file():
            raise FileNotFoundError(f"Component definition not found: {path}")

        with path.open(encoding="utf-8") as f:
            return json.load(f)

    @property
    def manual_mode(self) -> bool:
        return self.component_definition.get("manual_mode")

    @property
    def load_type(self) -> int:
        return self.component_definition.get("load_type")

    @property
    def process_type(self) -> int:
        return self.component_definition.get("process_type")

    @property
    def is_customized(self) -> int:
        return self.component_definition.get("is_customized")

    @property
    def columns(self) -> list[Column]:

        database_object_columns = self.component_definition.get("database_object").get(
            "columns"
        )
        query_columns = self.component_definition.get("query_columns")

        nullable_by_name = {
            column.get("column_name"): column.get("nullable")
            for column in database_object_columns
            if column.get("column_name") is not None
        }

        return [
            Column(
                column_name=column.get("column_name"),
                data_type_full=column.get("data_type_full"),
                type=column.get("type"),
                nullable=(
                    None
                    if self.manual_mode
                    else nullable_by_name.get(column.get("column_name"))
                ),
            )
            for column in query_columns
        ]

    @property
    def load_procedures(self) -> list[QueryLoadProcedures]:

        load_procedures = self.component_definition.get("load_procedures")

        return [
            QueryLoadProcedures(
                sequence=load_procedure.get("sequence"),
                identifier=load_procedure.get("identifier"),
            )
            for load_procedure in load_procedures
        ]

    @property
    def dimensions(self) -> list[Dimension]:

        dimensions = self.component_definition.get("dimensions", [])

        if self.manual_mode or self.category == "dim":
            return []

        return [
            Dimension(
                dimension=dimension.get("dimension"),
                role_playing=dimension.get("role_playing"),
                dimension_joins=[
                    DimensionJoin(
                        delta_column=dimension_join.get("delta_column"),
                        dimension_column=dimension_join.get("dimension_column"),
                    )
                    for dimension_join in dimension.get("dimension_joins", [])
                ],
            )
            for dimension in dimensions
        ]

    @property
    def queries(self) -> list[str]:

        folder = (
            self.path if self.manual_mode else self.path / "deployment" / "generated"
        )

        query_files = sorted(
            p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in {".sql"}
        )

        return [p.read_text(encoding="utf-8") for p in query_files]

    @property
    def query_information(self) -> list[QueryInformation]:

        folder = (
            self.path if self.manual_mode else self.path / "deployment" / "generated"
        )

        query_files = sorted(
            p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".sql"
        )

        if self.manual_mode:
            return [
                QueryInformation(
                    name=p.name.removesuffix(".sql"),
                    select_file_path=p.name,
                    sequence=-1,
                    aliases=[],
                    query=p.read_text(encoding="utf-8"),
                )
                for p in query_files
            ]

        queries = {p.name: p.read_text(encoding="utf-8") for p in query_files}

        query_information = self.component_definition.get("queries")

        return [
            QueryInformation(
                name=query.get("name"),
                select_file_path=query.get("select_file_path"),
                sequence=query.get("sequence"),
                aliases=[
                    QueryAlias(
                        name=alias.get("name"),
                        type=alias.get("type"),
                    )
                    for alias in query.get("aliases")
                ],
                query=queries.get(query.get("select_file_path")),
            )
            for query in query_information
        ]

    @property
    def table_definitions(self) -> list[TableDefinition]:
        table_definition_path = Path(self.path / "deployment")
        table_definitions = []

        for table_definition_file in table_definition_path.iterdir():
            if (
                table_definition_file.is_file()
                and table_definition_file.stem.lower().startswith("table_definition")
            ):
                payload = json.loads(table_definition_file.read_text(encoding="utf-8"))

                table_definitions.append({
                    "schema": table_definition_file.stem.split(".")[-1],
                    "tables": payload.get("tables", []),
                })

        return [
            TableDefinition(
                schema=table_definition.get("schema"),
                table_identifier=table.get("table_identifier"),
                columns=[
                    TableDefinitionColumn(
                        column_name=column.get("column_name"),
                        data_type=column.get("data_type"),
                        character_maximum_length=column.get("character_maximum_length"),
                        numeric_precision=column.get("numeric_precision"),
                        numeric_scale=column.get("numeric_scale"),
                        nullable=column.get("nullable"),
                        business_key=column.get("business_key"),
                    )
                    for column in (table.get("columns") or [])
                ],
            )
            for table_definition in table_definitions
            for table in (table_definition.get("tables") or [])
        ]
