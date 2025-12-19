from typing import Any, Optional, List

from attrs import define, field

from .field import Field


@define
class RelationshipField(Field):
    related_model: Any = field()

    def __init__(self, related_model: Any, *args: Any, **kwargs: Any) -> None:
        self.related_model = related_model
        super().__init__(*args, **kwargs)

    def validate(self, value: Any) -> None:
        if not isinstance(value, self.related_model):
            raise ValueError(f"Value must be an instance of {self.related_model.__name__}")

    def to_python(self, value: Any) -> Any:
        if isinstance(value, self.related_model):
            return value
        elif isinstance(value, dict):
            return self.related_model(**value)
        else:
            raise ValueError(f"Cannot convert {value} to {self.related_model.__name__}")


@define
class ForeignKeyField(RelationshipField):
    on_delete: str = field(default="CASCADE")

    def __init__(self, related_model: Any, on_delete: str = "CASCADE", *args: Any, **kwargs: Any) -> None:
        super().__init__(related_model, *args, **kwargs)
        self.on_delete = on_delete

    def validate(self, value: Any) -> None:
        super().validate(value)
        # Additional validation specific to ForeignKey could be added here

    def to_python(self, value: Any) -> Any:
        if isinstance(value, (int, str)):  # Assuming the foreign key could be an ID or a string identifier
            # Here you might want to fetch the actual object from the database
            # For now, we'll just return the value as is
            return value
        return super().to_python(value)


@define
class ManyToManyField(RelationshipField):
    through: Optional[str] = field(default=None)

    def __init__(self, related_model: Any, through: Optional[str] = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(related_model, *args, **kwargs)
        self.through = through

    def validate(self, value: Any) -> None:
        if not isinstance(value, (list, tuple)):
            raise ValueError("Value must be a list or tuple of related objects")
        for item in value:
            super().validate(item)

    def to_python(self, value: Any) -> List[Any]:
        if isinstance(value, (list, tuple)):
            return [super().to_python(item) for item in value]
        else:
            raise ValueError(f"Cannot convert {value} to a list of {self.related_model.__name__}")
