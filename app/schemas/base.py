from typing import TypeVar, Generic, List

from pydantic import BaseModel as PydanticBaseModel, model_validator


class BaseModel(PydanticBaseModel):
    class Config:
        from_attributes = True

    def model_dump_without_empty(self):
        return self.model_dump(
            exclude_none=True,
            exclude={key for key, value in self.model_dump().items() if not value}
        )


T = TypeVar("T", bound=BaseModel)


class DefaultPageParams(BaseModel):
    page_number: int = 1
    page_size: int = 20
    sort_by: str = "create_date"
    sort_order: str = "desc"

    @property
    def limit(self):
        return self.page_size

    @property
    def offset(self):
        return (self.page_number - 1) * self.page_size

    @model_validator(mode='before')
    def parse_empty_value(cls, data):
        for key, value in data.items():
            if not value:
                data[key] = None
        return data


class DefaultPageResponse(BaseModel, Generic[T]):
    total: int
    data: List[T]

