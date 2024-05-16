from sqlalchemy import TypeDecorator, String


class StringEnum(TypeDecorator):
    """
    A custom type for SQLAlchemy to store enums as strings in the database,
    while representing them as enum objects in Python.
    """
    impl = String
    cache_ok = False

    def __init__(self, enum_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_type = enum_type

    def process_bind_param(self, value, dialect):
        """Convert enum object to string before storing in the database."""
        return value.value if value is not None else None

    def process_result_value(self, value, dialect):
        """Convert string back to enum object when loading from the database."""
        return self.enum_type(value) if value is not None else None
