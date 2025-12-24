import json
from pathlib import Path
from typing import Any, Callable, Optional

from torch import Tensor

from tp_interfaces.serializable import DirectorySerializableMixin
from .abstract import AbstractPooler, choose


class AggregatePooler(AbstractPooler, DirectorySerializableMixin):

    def __init__(
            self,
            from_index: Optional[int] = None,
            to_index: Optional[int] = None,
            aggregate_function: Callable[[Tensor, int], Tensor] = None
    ):
        DirectorySerializableMixin.__init__(self)

        if aggregate_function is None:
            raise ValueError('No aggregate function specified!')

        self._from_index = from_index
        self._to_index = to_index
        self._aggregate_function = aggregate_function

    def pool(self, tensor: Tensor, *, dim: int) -> Tensor:
        selected_elements = choose(tensor, self._from_index, self._to_index, dim=dim)
        return self._aggregate_function(selected_elements, dim)

    @classmethod
    def _serializer(cls, obj) -> tuple[Callable[[Any, Path], None], Callable[[Path], Any] | dict]:
        if isinstance(obj, Callable):
            return _save_callable, _load_callable
        return super()._serializer(obj)


def _save_callable(obj: Callable, path: Path):
    import inspect
    with path.open('w', encoding='utf-8') as f:
        json.dump({
            'module': inspect.getmodule(obj).__name__,
            'qualname': obj.__qualname__
        }, f, ensure_ascii=False, indent=2)


def _load_callable(path: Path) -> Callable:
    import importlib
    with path.open('r', encoding='utf-8') as f:
        config = json.load(f)
    module = importlib.import_module(config['module'])
    if '.' in config['qualname']:
        class_name, name = config['qualname'].rsplit('.', 1)
        module = getattr(module, class_name)
        config['qualname'] = name
    return getattr(module, config['qualname'])
