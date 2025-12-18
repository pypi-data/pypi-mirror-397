from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlpgq.schema import PropertyGraph


@dataclass
class PropertyRef:
    element_name: str
    property_name: str

    def __eq__(self, other: Any) -> Condition:  # type: ignore[override]
        return Condition(self, "=", other)

    def __ne__(self, other: Any) -> "Condition":  # type: ignore[override]
        return Condition(self, "<>", other)

    def __lt__(self, other: Any) -> "Condition":
        return Condition(self, "<", other)

    def __le__(self, other: Any) -> "Condition":
        return Condition(self, "<=", other)

    def __gt__(self, other: Any) -> "Condition":
        return Condition(self, ">", other)

    def __ge__(self, other: Any) -> "Condition":
        return Condition(self, ">=", other)

    def to_sql(self) -> str:
        return f"{self.element_name}.{self.property_name}"


@dataclass
class Condition:
    left: PropertyRef | Any
    operator: str
    right: Any

    def to_sql(self) -> str:
        left_sql = (
            self.left.to_sql() if hasattr(self.left, "to_sql") else str(self.left)
        )
        if isinstance(self.right, str):
            right_sql = f"'{self.right}'"
        elif hasattr(self.right, "to_sql"):
            right_sql = self.right.to_sql()
        else:
            right_sql = str(self.right)
        return f"{left_sql} {self.operator} {right_sql}"


@dataclass
class Node:
    alias: str
    label: str | list[str] | None = None

    def __getattr__(self, attr: str) -> PropertyRef:
        if attr.startswith("_") or attr in ("alias", "label"):
            raise AttributeError(attr)
        return PropertyRef(self.alias, attr)

    def __rshift__(self, edge: Edge) -> PartialPath:
        return PartialPath(self, edge, directed=True, forward=True)

    def __rrshift__(self, other: PartialPath) -> PathPattern:
        return PathPattern(
            other.source, other.edge, self, other.directed, other.forward
        )

    def __sub__(self, edge: Edge) -> PartialPath:
        return PartialPath(self, edge, directed=False, forward=True)

    def to_sql(self) -> str:
        if self.label is None:
            return f"({self.alias})"
        elif isinstance(self.label, list):
            labels = "|".join(self.label)
            return f"({self.alias} IS {labels})"
        else:
            return f"({self.alias} IS {self.label})"


@dataclass
class Edge:
    alias: str | None = None
    label: str | None = None
    min_hops: int | None = None
    max_hops: int | None = None

    def __getattr__(self, attr: str) -> PropertyRef:
        if attr.startswith("_") or attr in ("alias", "label", "min_hops", "max_hops"):
            raise AttributeError(attr)
        if self.alias is None:
            raise ValueError("Edge must have an alias to access properties")
        return PropertyRef(self.alias, attr)

    def __rsub__(self, other: PartialPath) -> PathPattern:
        return PathPattern(other.source, other.edge, self, directed=False, forward=True)  # type: ignore

    def repeat(self, min_hops: int, max_hops: int) -> Edge:
        return Edge(
            alias=self.alias,
            label=self.label,
            min_hops=min_hops,
            max_hops=max_hops,
        )

    def to_sql(self, directed: bool = True, forward: bool = True) -> str:
        alias_part = self.alias if self.alias else ""
        label_part = f"IS {self.label}" if self.label else ""
        inner = f"{alias_part} {label_part}".strip()

        quantifier = ""
        if self.min_hops is not None and self.max_hops is not None:
            quantifier = f"{{{self.min_hops},{self.max_hops}}}"

        if directed:
            if forward:
                return f"-[{inner}]->{quantifier}"
            else:
                return f"<-[{inner}]-{quantifier}"
        else:
            return f"-[{inner}]-{quantifier}"


_edge_counter = 0


def _next_edge_alias() -> str:
    global _edge_counter
    _edge_counter += 1
    return f"_e{_edge_counter}"


@dataclass
class PartialPath:
    source: Node
    edge: Edge
    directed: bool
    forward: bool

    def __rshift__(self, target: Node) -> PathPattern:
        edge = self.edge
        if edge.alias is None:
            edge = Edge(
                alias=_next_edge_alias(),
                label=edge.label,
                min_hops=edge.min_hops,
                max_hops=edge.max_hops,
            )
        return PathPattern(self.source, edge, target, self.directed, self.forward)

    def __sub__(self, target: Node) -> PathPattern:
        edge = self.edge
        if edge.alias is None:
            edge = Edge(
                alias=_next_edge_alias(),
                label=edge.label,
                min_hops=edge.min_hops,
                max_hops=edge.max_hops,
            )
        return PathPattern(self.source, edge, target, directed=False, forward=True)


@dataclass
class PathPattern:
    source: Node
    edge: Edge
    target: Node
    directed: bool = True
    forward: bool = True

    def to_sql(self) -> str:
        return f"{self.source.to_sql()} {self.edge.to_sql(self.directed, self.forward)} {self.target.to_sql()}"


@dataclass
class ColumnDef:
    expression: PropertyRef | str
    alias: str

    def to_sql(self) -> str:
        if isinstance(self.expression, PropertyRef):
            return f"{self.expression.to_sql()} AS {self.alias}"
        return f"{self.expression} AS {self.alias}"


@dataclass
class Query:
    graph: PropertyGraph
    patterns: list[PathPattern] = field(default_factory=list)
    conditions: list[Condition] = field(default_factory=list)
    column_defs: list[ColumnDef] = field(default_factory=list)
    group_by_columns: list[str] = field(default_factory=list)

    def match(self, *patterns: PathPattern) -> Query:
        return Query(
            graph=self.graph,
            patterns=self.patterns + list(patterns),
            conditions=self.conditions,
            column_defs=self.column_defs,
            group_by_columns=self.group_by_columns,
        )

    def where(self, condition: Condition) -> Query:
        return Query(
            graph=self.graph,
            patterns=self.patterns,
            conditions=self.conditions + [condition],
            column_defs=self.column_defs,
            group_by_columns=self.group_by_columns,
        )

    def columns(self, **kwargs: PropertyRef) -> Query:
        new_cols = [ColumnDef(expr, alias) for alias, expr in kwargs.items()]
        return Query(
            graph=self.graph,
            patterns=self.patterns,
            conditions=self.conditions,
            column_defs=self.column_defs + new_cols,
            group_by_columns=self.group_by_columns,
        )

    def group_by(self, *columns: str) -> Query:
        return Query(
            graph=self.graph,
            patterns=self.patterns,
            conditions=self.conditions,
            column_defs=self.column_defs,
            group_by_columns=self.group_by_columns + list(columns),
        )

    def to_sql(self) -> str:
        select_columns = (
            ", ".join(c.alias for c in self.column_defs) if self.column_defs else "*"
        )

        match_patterns = ",\n        ".join(p.to_sql() for p in self.patterns)

        where_clause = ""
        if self.conditions:
            where_strs = [c.to_sql() for c in self.conditions]
            where_clause = f"\n  WHERE {' AND '.join(where_strs)}"

        columns_inner = ", ".join(c.to_sql() for c in self.column_defs)

        sql = f"""SELECT {select_columns} FROM GRAPH_TABLE ({self.graph.name}
  MATCH {match_patterns}{where_clause}
  COLUMNS ({columns_inner})
)"""

        if self.group_by_columns:
            sql += f"\nGROUP BY {', '.join(self.group_by_columns)}"

        return sql + ";"
