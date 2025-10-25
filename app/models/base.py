from sqlalchemy.orm import declarative_base, DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def to_dict(self):
        obj_dict = {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
        return obj_dict

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
