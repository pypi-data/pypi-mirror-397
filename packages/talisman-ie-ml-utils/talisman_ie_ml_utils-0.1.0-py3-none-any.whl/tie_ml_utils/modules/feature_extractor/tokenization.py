# moved from tie_ml.modules.feature_extractor.tokenization

from dataclasses import dataclass

from tie_ml_utils.helper import TupleLike


@dataclass(slots=True)
class SentenceTokenization(TupleLike):
    """
    Sentence tokenized into sub tokens. Cannot be empty.
    """

    sub_token_ids: tuple[int, ...]
    tokens_start_mask: tuple[bool, ...]

    def __len__(self):
        return len(self.sub_token_ids)

    def __post_init__(self):
        if not len(self):
            raise ValueError('Empty tokenization is not allowed!')


@dataclass(slots=True)
class ContextualizedSentenceTokenization(SentenceTokenization):
    """
    Tokenization with added surrounding context.
    """

    main_sub_tokens_mask: tuple[bool, ...]


@dataclass(slots=True)
class TokenizedNodeChunk(ContextualizedSentenceTokenization):
    """
    Chunk of a document text. Can include text from multiple nodes, node_ids specify node id for each sentence.
    """

    node_ids: tuple[int, ...]
    sentence_ids: tuple[int, ...]
    shift: int

    def __post_init__(self):
        super(TokenizedNodeChunk, self).__post_init__()
        if not len(self.sentence_ids):
            raise ValueError('There should be at least one sentence in tokenized node!')
        if len(self.node_ids) != len(self.sentence_ids):
            raise ValueError('Length mismatch for node_ids and sentences!')


@dataclass(slots=True)
class TokenizedNodeChunkWithSentenceInfo(TokenizedNodeChunk):
    sentence_lengths: list[int]

    def __post_init__(self):
        super(TokenizedNodeChunk, self).__post_init__()
        if len(self.sentence_lengths) != len(self.sentence_ids):
            raise ValueError('Length mismatch for sentence_lengths and sentences!')
