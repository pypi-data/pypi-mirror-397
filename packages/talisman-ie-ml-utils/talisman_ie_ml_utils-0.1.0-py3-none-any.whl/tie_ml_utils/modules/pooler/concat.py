from typing import Optional

import torch
from torch import Tensor

from tp_interfaces.serializable import DirectorySerializableMixin
from .abstract import AbstractPooler, choose


class ConcatPooler(AbstractPooler, DirectorySerializableMixin):

    def __init__(self, from_index: Optional[int] = None, to_index: Optional[int] = None, concat_along_index: int = -1):
        DirectorySerializableMixin.__init__(self)
        self._from_index = from_index
        self._to_index = to_index
        self._concat_along_dim = concat_along_index

    def pool(self, tensor: Tensor, *, dim: int) -> Tensor:
        selected_elements = choose(tensor, self._from_index, self._to_index, dim=dim)
        tensor_list = torch.unbind(selected_elements, dim)
        return torch.concat(tensor_list, dim=self._concat_along_dim)
