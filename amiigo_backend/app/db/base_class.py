from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import inspect

@as_declarative()
class Base:
    """
    Base class for all SQLAlchemy models.

    It provides a default __tablename__ generation and an id primary key column.
    It also includes a __repr__ method for easier debugging.
    """
    id: any # Primary key column, actual type defined in subclasses
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Generates the table name automatically from the class name.
        Converts CamelCase class names to snake_case table names.
        Example: UserProfile -> user_profile
        """
        import re
        # First, convert CamelCase to snake_case with underscores
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        # Then, ensure it ends with 's' if it's a common noun,
        # or handle specific pluralization rules if necessary.
        # For simplicity, many prefer to just use the snake_case name
        # or explicitly define __tablename__ in the model if auto-pluralization is complex.
        # Here, we'll just use the snake_case name.
        # If you want pluralized names, you might add an 's' or use a library like 'inflect'.
        # For example, to add 's':
        # if not name.endswith('s'):
        #     name += 's'
        return name

    def _asdict(self) -> dict:
        """
        Return a dictionary representation of the model.
        This is useful for converting model instances to dictionaries,
        for example, when preparing data for Pydantic schemas or API responses.
        """
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}

    def __repr__(self) -> str:
        """
        Provides a developer-friendly string representation of the model instance.
        Shows the class name and primary key, which is useful for debugging.
        """
        pk_columns = [pk.name for pk in inspect(self.__class__).primary_key]
        pk_values = {col: getattr(self, col) for col in pk_columns}
        pk_str = ", ".join(f"{k}={v!r}" for k, v in pk_values.items())
        return f"<{self.__class__.__name__}({pk_str})>"

# This Base class can now be imported by your models:
# from app.db.base_class import Base
#
# class User(Base):
#     id = Column(Integer, primary_key=True, index=True)
#     # ... other columns
# ``` # Removed offending backticks
