from torch import Tensor

from tp_interfaces.serializable import DirectorySerializableMixin
from .abstract import AbstractPooler


class SelectPooler(AbstractPooler, DirectorySerializableMixin):

    def __init__(self, index: int):
        DirectorySerializableMixin.__init__(self)
        self._index = index

    def pool(self, tensor: Tensor, *, dim: int) -> Tensor:
        if dim == 0 or dim == -len(tensor.shape):
            return tensor[self._index]
        return tensor.swapdims(0, dim)[[self._index]].swapdims(0, dim).squeeze(dim)
