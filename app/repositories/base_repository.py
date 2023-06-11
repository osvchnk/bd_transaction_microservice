import abc
from typing import TypeVar, Generic, Type

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import async_session

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseTransactionRepository(Generic[ModelType], metaclass=abc.ABCMeta):

    def __init__(self):
        self.session: AsyncSession = async_session()

    @property
    @abc.abstractmethod
    def _model(self) -> Type[ModelType]:
        ...

    async def close(self):
        if self.session is not None:
            try:
                await self.session.close()
            except Exception as ex:
                raise ex

    async def get(self, id: int) -> ModelType | None:
        return await self.session.get(self._model, id)

    async def update(self, id: int, update_data: dict) -> ModelType | None:
        obj = await self.get(id)
        if obj is None:
            return None
        for key, value in update_data.items():
            setattr(obj, key, value)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get_by(self, **kwargs):
        query = (
            select(self._model).
            options(selectinload(self._model.transaction)).
            filter(*[getattr(self._model, key) == value for key, value in kwargs.items()])
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_list_by(self, **kwargs):
        query = (
            select(self._model).
            options(selectinload(self._model.transaction)).
            filter(*[getattr(self._model, key) == value for key, value in kwargs.items()])
        )
        result = await self.session.execute(query)
        return result.scalars().all()
