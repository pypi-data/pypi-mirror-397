import math
from typing import Tuple

import torch
from torch import Tensor

from tie_ml_utils.torch_wrapper import DirectorySerializableTorchModule
from .abstract import AbstractPooler


class AttentionPooler(AbstractPooler, DirectorySerializableTorchModule):
    def __init__(self, features: int, dropout_rate: float):
        DirectorySerializableTorchModule.__init__(self)
        self._attention = torch.nn.Linear(in_features=features, out_features=1)
        self._dropout = torch.nn.Dropout(dropout_rate)
        self._scaling_factor = math.sqrt(features)

    def _validate_dim(self, shape: Tuple[int, ...], dim: int):
        if dim == -1 or dim == len(shape) - 1:
            raise ValueError(f'{self.__class__.__name__} cannot pool feature dimension!')
        if len(shape) < 3:
            raise ValueError(f'{self.__class__.__name__} requires at least 3 dimensions but {len(shape)} were given!')
        if shape[-1] != self._attention.in_features:
            raise ValueError(f'Expected feature dimension to be {self._attention.in_features} but got {shape[-1]}!')

    def pool(self, tensor: Tensor, *, dim: int) -> Tensor:
        # wrapper around call that the parent class needs to have
        return self.__call__(tensor, dim=dim)

    def forward(self, tensor: Tensor, *, dim: int) -> Tensor:
        """
        Pools `tensor` by applying scaled dot-product attention and dropout.
        Args:
            tensor: a (3+)-dimensional tensor of shape N1, ..., Nm, F where F is an embedding dimension
            dim: pooled dimension, last dimension cannot be pooled

        Returns:
            tokens: tensor of the same shape as input tensor but with pooling dimension missing
        """
        orig_dims = tensor.shape  # shape N1, ..., Nm, F
        self._validate_dim(orig_dims, dim)

        # move pooled dimension at -2
        tensor = torch.swapdims(tensor, dim, -2)  # shape N_1, ..., N_dim-1, N_m, N_dim+1, ..., N_m-1, N_dim, F

        attn_scores = self._attn_scores(tensor)  # shape N_1, ..., N_dim-1, N_m, N_dim+1, ..., N_m-1, N_dim
        attn_scores = attn_scores.unsqueeze(-2)  # shape N_1, ..., N_dim-1, N_m, N_dim+1, ..., N_m-1, 1, N_dim

        # N = N_1 * ... * N_dim-1 * N_m * N_dim+1 * ... * N_m-1
        # BMM operation on (N, 1, N_dim) x (N, N_dim, F) -> (N, 1, F)
        unravelled_dims = attn_scores.shape[:-2]
        pooled_dim = attn_scores.shape[-1]
        result = torch.bmm(attn_scores.reshape(-1, 1, pooled_dim), tensor.reshape(-1, pooled_dim, self._attention.in_features))

        # restore original dims
        result = result.reshape(*unravelled_dims, 1, self._attention.in_features)  # shape N1, ..., N_dim-1, N_m, N_dim+1, ..., N_m-1, 1, F
        result = torch.swapdims(result, -2, dim)  # shape N1, ..., N_dim-1, 1, N_dim+1, ..., N_m, F
        return result.squeeze(dim)  # remove pooled dim, shape N1, ..., N_dim-1, N_dim+1, ..., N_m, F

    def _attn_scores(self, example_representations: Tensor):
        # mask with 0 at positions belonging to the words and -inf elsewhere to mask out padding
        attn_mask = example_representations.sum(dim=-1) != 0
        not_empty_examples_mask = attn_mask.sum(dim=-1) != 0

        attn_mask = torch.log(attn_mask.to(torch.float))
        attn_mask[~not_empty_examples_mask] = 0  # for empty examples we will get constant scores that will not affect gradients

        attn_scores = self._attention(self._dropout(example_representations))  # [..., 1], removed transposition
        attn_scores = attn_mask + attn_scores.squeeze(dim=-1)  # ONLY squeeze last dim - otherwise error with len 1 dims

        # apply scaling factor as in https://arxiv.org/pdf/1706.03762v5.pdf to preserve variance 1
        return torch.softmax(attn_scores / self._scaling_factor, dim=-1)
