class SQLType:
    sql_type: str = "TEXT"


class Integer(SQLType):
    sql_type = "INTEGER"


class String(SQLType):
    sql_type = "TEXT"


class Float(SQLType):
    sql_type = "REAL"


class Boolean(SQLType):
    sql_type = "BOOLEAN"


class Date(SQLType):
    sql_type = "DATE"


class DateTime(SQLType):
    sql_type = "TIMESTAMP"
