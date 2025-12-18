from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from sqlpgq.query import Query


@dataclass
class Column:
    name_or_type: str | Type[Any] | None = None
    type_: Type[Any] | None = None
    primary_key: bool = False
    _name: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.name_or_type, str):
            self._name = self.name_or_type
        elif isinstance(self.name_or_type, type):
            self.type_ = self.name_or_type

    def __set_name__(self, owner: type, name: str) -> None:
        if self._name is None:
            self._name = name

    @property
    def name(self) -> str | None:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value


class TableMeta(type):
    def __new__(
        mcs, name: str, bases: tuple[type, ...], namespace: dict[str, Any]
    ) -> TableMeta:
        cls = super().__new__(mcs, name, bases, namespace)

        columns: dict[str, Column] = {}
        for attr_name, attr_value in namespace.items():
            if isinstance(attr_value, Column):
                if attr_value.name is None:
                    attr_value.name = attr_name
                columns[attr_name] = attr_value

        cls._columns = columns  # type: ignore[attr-defined]
        return cls


class VertexTable(metaclass=TableMeta):
    __tablename__: str
    __label__: str | None = None
    _columns: dict[str, Column]

    @classmethod
    def get_label(cls) -> str:
        return cls.__label__ or cls.__name__

    @classmethod
    def get_tablename(cls) -> str:
        return cls.__tablename__

    @classmethod
    def get_columns(cls) -> dict[str, Column]:
        return cls._columns

    @classmethod
    def get_primary_key(cls) -> str | None:
        for name, col in cls._columns.items():
            if col.primary_key:
                return col.name
        return None

    @classmethod
    def get_property_names(cls) -> list[str]:
        return [col.name for col in cls._columns.values() if col.name]


class EdgeTable(metaclass=TableMeta):
    __tablename__: str
    __label__: str | None = None
    __source__: tuple[Column, Type[VertexTable]]
    __destination__: tuple[Column, Type[VertexTable]]
    _columns: dict[str, Column]

    @classmethod
    def get_label(cls) -> str:
        return cls.__label__ or cls.__name__

    @classmethod
    def get_tablename(cls) -> str:
        return cls.__tablename__

    @classmethod
    def get_source(cls) -> tuple[str, Type[VertexTable]]:
        col, vertex = cls.__source__
        return (col.name or "", vertex)

    @classmethod
    def get_destination(cls) -> tuple[str, Type[VertexTable]]:
        col, vertex = cls.__destination__
        return (col.name or "", vertex)

    @classmethod
    def get_property_names(cls) -> list[str]:
        source_col = cls.__source__[0].name
        dest_col = cls.__destination__[0].name
        return [
            col.name
            for col in cls._columns.values()
            if col.name and col.name not in (source_col, dest_col)
        ]


@dataclass
class PropertyGraph:
    name: str
    vertices: list[Type[VertexTable]] = field(default_factory=list)
    edges: list[Type[EdgeTable]] = field(default_factory=list)

    def create_statement(self, dialect: str = "duckdb") -> str:
        lines = [f"CREATE PROPERTY GRAPH {self.name}"]

        if self.vertices:
            lines.append("VERTEX TABLES (")
            vertex_parts = []
            for v in self.vertices:
                if dialect == "duckdb":
                    vertex_parts.append(f"  {v.get_tablename()} LABEL {v.get_label()}")
                else:
                    props = ", ".join(v.get_property_names())
                    vertex_parts.append(
                        f"  {v.get_tablename()} LABEL {v.get_label()} PROPERTIES ({props})"
                    )
            lines.append(",\n".join(vertex_parts))
            lines.append(")")

        if self.edges:
            lines.append("EDGE TABLES (")
            edge_parts = []
            for e in self.edges:
                source_col, source_vertex = e.get_source()
                dest_col, dest_vertex = e.get_destination()
                source_pk = source_vertex.get_primary_key() or "id"
                dest_pk = dest_vertex.get_primary_key() or "id"

                if dialect == "duckdb":
                    edge_parts.append(
                        f"  {e.get_tablename()}\n"
                        f"    SOURCE KEY ({source_col}) REFERENCES {source_vertex.get_tablename()} ({source_pk})\n"
                        f"    DESTINATION KEY ({dest_col}) REFERENCES {dest_vertex.get_tablename()} ({dest_pk})\n"
                        f"    LABEL {e.get_label()}"
                    )
                else:
                    prop_names = e.get_property_names()
                    props_clause = (
                        f"PROPERTIES ({', '.join(prop_names)})"
                        if prop_names
                        else "NO PROPERTIES"
                    )
                    edge_parts.append(
                        f"  {e.get_tablename()}\n"
                        f"    SOURCE KEY ({source_col}) REFERENCES {source_vertex.get_tablename()} ({source_pk})\n"
                        f"    DESTINATION KEY ({dest_col}) REFERENCES {dest_vertex.get_tablename()} ({dest_pk})\n"
                        f"    LABEL {e.get_label()}\n"
                        f"    {props_clause}"
                    )
            lines.append(",\n".join(edge_parts))
            lines.append(")")

        return "\n".join(lines) + ";"

    def query(self) -> Query:
        from sqlpgq.query import Query

        return Query(self)
