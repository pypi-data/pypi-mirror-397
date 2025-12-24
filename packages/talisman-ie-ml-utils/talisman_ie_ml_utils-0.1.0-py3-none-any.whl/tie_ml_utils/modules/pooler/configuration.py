from enum import Enum
from functools import partial
from typing import Any, Callable, Type, Union

import torch
from torch import Tensor

from tie_ml_utils.torch_wrapper import DirectorySerializableTorchModule
from tp_interfaces.abstract import ModelTypeFactory
from .abstract import AbstractPooler


def _get_select_pooler() -> Type[AbstractPooler]:
    from .select import SelectPooler
    return SelectPooler


def _get_concat_pooler() -> Type[AbstractPooler]:
    from .concat import ConcatPooler
    return ConcatPooler


def _get_aggregate_pooler() -> Type[AbstractPooler]:
    from .aggregate import AggregatePooler
    return AggregatePooler


def _get_attn_pooler() -> Type[AbstractPooler]:
    from .attention import AttentionPooler
    return AttentionPooler


def _add_args(factory: Callable[[], Type[AbstractPooler]], **args) -> Callable[[], Callable[[], AbstractPooler]]:
    def factory_wrapper() -> Callable[[], AbstractPooler]:
        return partial(factory(), **args)

    return factory_wrapper


def _max_wrapper(tensor: Tensor, dim: int) -> Tensor:
    return torch.max(tensor, dim).values


class PoolerType(Enum):
    AGGREGATE = 'aggregate'
    CONCAT = 'concat'
    MAX = 'max'
    MEAN = 'mean'
    LAST = 'last'
    SELECT = 'select'
    SUM = 'sum'
    FIRST = 'first'
    ATTN = 'attention'


POOLERS = ModelTypeFactory({
    PoolerType.AGGREGATE.value: _get_aggregate_pooler,
    PoolerType.CONCAT.value: _get_concat_pooler,
    PoolerType.MAX.value: _add_args(_get_aggregate_pooler, aggregate_function=_max_wrapper),
    PoolerType.MEAN.value: _add_args(_get_aggregate_pooler, aggregate_function=torch.mean),
    PoolerType.LAST.value: _add_args(_get_select_pooler, index=-1),
    PoolerType.SELECT.value: _get_select_pooler,
    PoolerType.SUM.value: _add_args(_get_aggregate_pooler, aggregate_function=torch.sum),
    PoolerType.FIRST.value: _add_args(_get_select_pooler, index=0),
    PoolerType.ATTN.value: _get_attn_pooler
})


class NamedPooler(AbstractPooler, DirectorySerializableTorchModule):

    def __init__(self, name: str, pooler: AbstractPooler):
        DirectorySerializableTorchModule.__init__(self)
        self._pooler = pooler
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def forward(self, *args, **kwargs) -> Any:
        self.pool(*args, **kwargs)

    def pool(self, tensor: Tensor, *, dim: int) -> Tensor:
        return self._pooler.pool(tensor, dim=dim)


def configure_pooler(config_or_pooler_type: Union[str, PoolerType, dict]) -> NamedPooler:
    if isinstance(config_or_pooler_type, str):
        config_or_pooler_type = PoolerType(config_or_pooler_type)
    if isinstance(config_or_pooler_type, PoolerType):
        model_name = config_or_pooler_type.value
        model_args = {}
    else:
        model_name = config_or_pooler_type['model']
        model_args = config_or_pooler_type['config']
    return NamedPooler(model_name, POOLERS[model_name](**model_args))
