import pytest
from sqlpgq import (
    Column,
    VertexTable,
    EdgeTable,
    PropertyGraph,
    Node,
    Edge,
    Integer,
    String,
    Date,
)


class User(VertexTable):
    __tablename__ = "users"
    __label__ = "Person"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)


class Friendship(EdgeTable):
    __tablename__ = "friendships"
    __label__ = "knows"

    __source__ = (Column("user_id"), User)
    __destination__ = (Column("friend_id"), User)

    since = Column(Date)


@pytest.fixture
def social_graph() -> PropertyGraph:
    return PropertyGraph(
        name="social_network",
        vertices=[User],
        edges=[Friendship],
    )


class TestPropertyGraph:
    def test_create_statement_duckdb(self, social_graph: PropertyGraph) -> None:
        sql = social_graph.create_statement(dialect="duckdb")

        assert "CREATE PROPERTY GRAPH social_network" in sql
        assert "VERTEX TABLES" in sql
        assert "users LABEL Person" in sql
        assert "PROPERTIES" not in sql
        assert "EDGE TABLES" in sql
        assert "friendships" in sql
        assert "SOURCE KEY (user_id) REFERENCES users (id)" in sql
        assert "DESTINATION KEY (friend_id) REFERENCES users (id)" in sql
        assert "LABEL knows" in sql

    def test_create_statement_oracle(self, social_graph: PropertyGraph) -> None:
        sql = social_graph.create_statement(dialect="oracle")

        assert "CREATE PROPERTY GRAPH social_network" in sql
        assert "users LABEL Person PROPERTIES" in sql
        assert "LABEL knows" in sql


class TestPatternMatching:
    def test_simple_pattern(self, social_graph: PropertyGraph) -> None:
        a = Node("a", "Person")
        b = Node("b", "Person")

        query = (
            social_graph.query()
            .match(a >> Edge(label="knows") >> b)
            .where(a.name == "Alice")
            .columns(friend_name=b.name)
        )

        sql = query.to_sql()

        assert "GRAPH_TABLE (social_network" in sql
        assert "(a IS Person)" in sql
        assert "IS knows]->" in sql
        assert "(b IS Person)" in sql
        assert "a.name = 'Alice'" in sql
        assert "b.name AS friend_name" in sql

    def test_multi_hop_pattern(self, social_graph: PropertyGraph) -> None:
        a = Node("a", "Person")
        b = Node("b", "Person")
        c = Node("c", "Person")

        query = (
            social_graph.query()
            .match(
                a >> Edge(label="knows") >> b,
                b >> Edge(label="knows") >> c,
            )
            .where(a.name == "Alice")
            .columns(friend_of_friend=c.name)
        )

        sql = query.to_sql()

        assert "(a IS Person) -[" in sql and "IS knows]-> (b IS Person)" in sql
        assert "(b IS Person) -[" in sql and "IS knows]-> (c IS Person)" in sql

    def test_edge_with_properties(self, social_graph: PropertyGraph) -> None:
        a = Node("a", "Person")
        b = Node("b", "Person")
        e = Edge(alias="e", label="knows")

        query = (
            social_graph.query()
            .match(a >> e >> b)
            .columns(friend=b.name, friends_since=e.since)
        )

        sql = query.to_sql()

        assert "-[e IS knows]->" in sql
        assert "e.since AS friends_since" in sql

    def test_variable_length_path(self, social_graph: PropertyGraph) -> None:
        a = Node("a", "Person")
        b = Node("b", "Person")

        query = (
            social_graph.query()
            .match(a >> Edge(label="knows").repeat(1, 3) >> b)
            .columns(reachable=b.name)
        )

        sql = query.to_sql()

        assert "IS knows]->{1,3}" in sql

    def test_undirected_edge(self, social_graph: PropertyGraph) -> None:
        a = Node("a", "Person")
        b = Node("b", "Person")

        query = (
            social_graph.query()
            .match(a - Edge(label="knows") - b)
            .columns(connected=b.name)
        )

        sql = query.to_sql()

        assert "IS knows]-" in sql
        assert "]->" not in sql.split("MATCH")[1]

    def test_multiple_labels(self, social_graph: PropertyGraph) -> None:
        a = Node("a", ["Person", "Company"])

        sql = a.to_sql()

        assert "(a IS Person|Company)" in sql


class TestConditions:
    def test_equality(self, social_graph: PropertyGraph) -> None:
        a = Node("a", "Person")
        b = Node("b", "Person")

        query = (
            social_graph.query()
            .match(a >> Edge(label="knows") >> b)
            .where(a.name == "Alice")
            .where(a.age > 25)
            .columns(friend=b.name)
        )

        sql = query.to_sql()

        assert "a.name = 'Alice'" in sql
        assert "a.age > 25" in sql

    def test_inequality(self, social_graph: PropertyGraph) -> None:
        a = Node("a", "Person")
        b = Node("b", "Person")

        query = (
            social_graph.query()
            .match(a >> Edge(label="knows") >> b)
            .where(a.id != b.id)
            .columns(friend=b.name)
        )

        sql = query.to_sql()

        assert "a.id <> b.id" in sql
