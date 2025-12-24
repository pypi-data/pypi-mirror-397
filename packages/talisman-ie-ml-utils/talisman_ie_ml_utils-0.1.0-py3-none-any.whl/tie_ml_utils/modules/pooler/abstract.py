from abc import ABCMeta, abstractmethod

from torch import Tensor

from tp_interfaces.serializable import Serializable


class AbstractPooler(Serializable, metaclass=ABCMeta):

    @abstractmethod
    def pool(self, tensor: Tensor, *, dim: int) -> Tensor:
        pass


def choose(tensor: Tensor, from_idx: int, to_idx: int, *, dim: int) -> Tensor:
    return tensor.swapdims(0, dim)[from_idx:to_idx].swapdims(0, dim)
