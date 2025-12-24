# moved from tie_ml.modules.feature_extractor.helper

import io
import pickle
from hashlib import md5
from typing import Any

import torch
from torch import BoolTensor, Tensor
from torch.nn import Parameter

from tie_ml_utils.helper import fill_roll


def parameter_hash(param: Parameter) -> str:
    buffer = io.BytesIO()
    pickle.dump(param.data.tolist(), buffer)
    buffer.seek(0)
    return md5(buffer.read()).hexdigest()


def extract_padded_token_images(
        sub_token_representations: Tensor,
        token_masks: BoolTensor,
        padding_masks: BoolTensor,
        *,
        pad_value: Any = 0.0
) -> Tensor:
    """Converts sub token representation into token images.
    Token image - token's sub token representations, concatenated into 'image'.

    For example, token with the following sub token representations: [1, 2], [3, 4], [5, 6]
    forms a token image:
    [
        [1, 2],
        [3, 4],
        [5, 6]
    ]

    :param: sub_token_representations - tensor of shape (B, ST, F)
    :param: token_masks - tensor of shape (B, ST) that indicates starts of tokens
    :param: padding_masks - tensor of shape (B, ST) that indicates non-pad sub tokens
    :param: pad_value - padding value for resulting images
    :return: tensor of shape (B, T, I, F)

    B - batch size
    ST - maximum length of sequences in sub tokens
    F - number of features
    T - maximum length of sequences in tokens
    I - maximum number of sub tokens in tokens
    """

    device = sub_token_representations.device
    batch_size, _, n_features = sub_token_representations.shape

    # calculate number of tokens in each batch sequence

    n_tokens = token_masks.sum(dim=-1)
    pad_sequences_to_size = n_tokens.max()

    # calculate how much padding tokens should be skipped for each batch sequence

    padding_tokens = torch.cumsum(pad_sequences_to_size - n_tokens, dim=-1)
    padding_tokens_skip = fill_roll(padding_tokens, shift=1, fill=0)

    # calculate image sizes (number of sub tokens in each token)

    cumulative_tokens_count = torch.cumsum(token_masks.view(-1), dim=-1)
    _, image_sizes = torch.unique_consecutive(cumulative_tokens_count[padding_masks.view(-1)], return_counts=True)

    # reserve space for padded images

    pad_images_to_size = image_sizes.max()
    padded_shape = (batch_size, pad_sequences_to_size, pad_images_to_size, n_features)
    padded_token_images = torch.full(padded_shape, fill_value=pad_value, dtype=sub_token_representations.dtype, device=device)

    # calculate shifts in dimensions for each sub token

    # FIXME: suboptimal
    image_dim_shift = torch.cat(list(map(torch.arange, image_sizes)))

    sequence_dim_shift = (cumulative_tokens_count - 1).view(batch_size, -1) + padding_tokens_skip.view(batch_size, 1)
    total_shift = sequence_dim_shift[padding_masks] * pad_images_to_size.to(device) + image_dim_shift.to(device)

    # fill feature representations into images

    raveled_padded_token_images = padded_token_images.view(-1, n_features)
    raveled_sub_token_representations = sub_token_representations[padding_masks]
    raveled_padded_token_images[total_shift] = raveled_sub_token_representations

    return padded_token_images
