import enum

from sqlalchemy import TypeDecorator, String


# Custom SQLAlchemy type to handle enum conversion
class EnumAsString(TypeDecorator):
    """Represents an enum value as a string in the database."""
    impl = String
    cache_ok = True

    def __init__(self, enum_type, **kw):
        self.enum_type = enum_type
        super(EnumAsString, self).__init__(**kw)

    def process_bind_param(self, value, dialect):
        """Process enum value and convert it to string when saving to database."""
        if value is None:
            return None
        return value.value if isinstance(value, self.enum_type) else value

    def process_result_value(self, value, dialect):
        """Convert the string value back to an enum value when loading from database."""
        if value is None:
            return None
        for item in self.enum_type:
            if item.value == value:
                return item
        return value


# Helper function to make the EnumAsString class importable in migration script without
# requiring the app module
def get_enum_as_string():
    return EnumAsString

class UserType(str, enum.Enum):
    MANAGER = 'manager'
    USER = 'user'
    ADMIN = 'admin'
