from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select, delete, update

from app.db.base_class import Base # Your SQLAlchemy base model

# Define TypeVariables for generic CRUD operations
ModelType = TypeVar("ModelType", bound=Base) # SQLAlchemy model type
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel) # Pydantic schema for creation
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel) # Pydantic schema for update

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic base class for CRUD (Create, Read, Update, Delete) operations.

    This class provides basic CRUD functionalities that can be inherited by
    specific CRUD classes for each SQLAlchemy model.

    Parameters:
    - `model`: The SQLAlchemy model class.
    """
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Retrieve a single record by its ID.

        :param db: SQLAlchemy database session.
        :param id: The ID of the record to retrieve.
        :return: The SQLAlchemy model instance if found, else None.
        """
        return db.get(self.model, id) # db.get is new in SQLAlchemy 1.4+
        # For older SQLAlchemy:
        # return db.query(self.model).filter(self.model.id == id).first()


    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Retrieve multiple records with pagination.

        :param db: SQLAlchemy database session.
        :param skip: Number of records to skip (for pagination).
        :param limit: Maximum number of records to return (for pagination).
        :return: A list of SQLAlchemy model instances.
        """
        statement = select(self.model).offset(skip).limit(limit)
        return db.execute(statement).scalars().all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record in the database.

        :param db: SQLAlchemy database session.
        :param obj_in: Pydantic schema containing the data for the new record.
        :return: The newly created SQLAlchemy model instance.
        """
        # Convert Pydantic schema to a dictionary suitable for SQLAlchemy model
        obj_in_data = jsonable_encoder(obj_in, exclude_unset=True)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update an existing record in the database.

        :param db: SQLAlchemy database session.
        :param db_obj: The existing SQLAlchemy model instance to update.
        :param obj_in: Pydantic schema or dictionary containing the data to update.
        :return: The updated SQLAlchemy model instance.
        """
        obj_data = jsonable_encoder(db_obj) # Get current data of db_obj as dict

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # Convert Pydantic schema to dict, excluding unset values to only update provided fields
            update_data = obj_in.model_dump(exclude_unset=True)
            # Pydantic V1: update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: Any) -> Optional[ModelType]:
        """
        Remove a record from the database by its ID.

        :param db: SQLAlchemy database session.
        :param id: The ID of the record to remove.
        :return: The removed SQLAlchemy model instance if found and deleted, else None.
        """
        obj = db.get(self.model, id) # db.get for SQLAlchemy 1.4+
        # For older SQLAlchemy:
        # obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    # Alternative remove without fetching first (more efficient for just deletion)
    def remove_by_id(self, db: Session, *, id: Any) -> bool:
        """
        Remove a record directly by ID without fetching it first.

        :param db: SQLAlchemy database session.
        :param id: The ID of the record to remove.
        :return: True if a record was deleted, False otherwise.
        """
        # Assuming 'id' is the primary key name. Adjust if your PK has a different name.
        # This requires the model to have an 'id' attribute that corresponds to the PK column.
        # If your PK is named differently, e.g., 'user_id', you'd need to adapt this or
        # pass the PK column object.
        # For a generic base, we assume 'id' or handle it in the specific CRUD class.
        # If self.model.id is not guaranteed, this method might need adjustment or removal from base.
        try:
            pk_name = self.model.__mapper__.primary_key[0].name
            statement = delete(self.model).where(getattr(self.model, pk_name) == id)
            result = db.execute(statement)
            db.commit()
            return result.rowcount > 0 # rowcount indicates how many rows were deleted
        except Exception:
            # Fallback or specific error handling if needed
            db.rollback()
            return False


# Example of how to use CRUDBase for a specific model:
#
# from .base import CRUDBase
# from app.models.item import Item # Assuming Item is an SQLAlchemy model
# from app.schemas.item import ItemCreate, ItemUpdate # Assuming Pydantic schemas
#
# class CRUDItem(CRUDBase[Item, ItemCreate, ItemUpdate]):
#     # You can add item-specific CRUD methods here if needed
#     # For example:
#     # def get_by_name(self, db: Session, *, name: str) -> Optional[Item]:
#     #     return db.query(Item).filter(Item.name == name).first()
#     pass
#
# item = CRUDItem(Item) # Instantiate the CRUD class for Item model
# ``` # Removed offending backticks
