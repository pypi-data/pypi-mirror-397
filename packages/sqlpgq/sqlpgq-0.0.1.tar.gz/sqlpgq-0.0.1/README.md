`sqlpgq` is a Python library for working with SQL/PGQ graph queries.

# Example
With the DuckPGQ extension installed, create the following social network tables.
```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER
);

-- Friendships table  
CREATE TABLE friendships (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    friend_id INTEGER REFERENCES users(id),
    since DATE
);

INSERT INTO users VALUES (1, 'Alice', 30), (2, 'Bob', 25), (3, 'Carol', 35);
INSERT INTO friendships VALUES (1, 1, 2, '2020-01-01'), (2, 2, 3, '2021-06-15');
```

Then run `examples/social_network.py` to see the generated SQL/PGQ graph queries.
