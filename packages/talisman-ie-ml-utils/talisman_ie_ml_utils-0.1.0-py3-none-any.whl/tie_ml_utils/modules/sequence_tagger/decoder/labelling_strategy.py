# moved from tie_ml.modules.sequence_tagger.decoder.labelling_strategy

import logging
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from copy import copy
from enum import Enum
from itertools import chain, starmap
from typing import Iterable, Iterator, NamedTuple, Sequence

import torch
from tdm.abstract.datamodel import AbstractFact, FactStatus
from tdm.datamodel.facts import MentionFact
from tdm.datamodel.mentions import TextNodeMention
from tdm.utils import MentionedFactsFactory
from torch import LongTensor

from tie_datamodel.datamodel.node.text import TIETextNode
from tie_datamodel.datamodel.span import Span

logger = logging.getLogger(__name__)


class LabellingStrategyType(str, Enum):
    BIO = 'BIO'
    IOB = 'IOB'


class MentionSignature(NamedTuple):
    start: int
    end: int


class AbstractLabellingStrategy(metaclass=ABCMeta):
    """
    An abstract utility class that defines an interface of functions that:
    1) encode text into a plain sequence of labels (basically for training/evaluation purposes, not inference)
    2) decode label_ids according to the selected labelling strategy

    Note that labels are a combination of entity type and label prefix except non-entity label.
    Also keep in mind that entity type is not the same as the fact type.
    """

    def __init__(self, ent_labels: set[str], outside_ent_label: str = 'O'):
        """
        :param ent_labels: label prefixes denoting entities
        :param outside_ent_label: non-entity label
        """
        self._ent_labels = copy(ent_labels)
        self._outside_ent_label = outside_ent_label

    def get_possible_categories(self, ent_types: set[str]) -> set[str]:
        """
        Returns possible labels based on label prefixes and entity types.
        """
        return {
            f'{label}-{e_type}'
            for label in self._ent_labels for e_type in ent_types
        }.union((self._outside_ent_label,))

    @property
    @abstractmethod
    def type(self) -> LabellingStrategyType:
        """
        Type of used labelling strategy.
        """
        pass

    @property
    def outside_ent_label(self) -> str:
        """
        Non-entity label.
        """
        return self._outside_ent_label

    @abstractmethod
    def encode_labels(self, node: TIETextNode, mentions: Iterable[MentionFact]) -> list[str]:
        """
        Encodes node text into a list of labels (one label per span).
        Note that during encoding, the entity type and the fact type are the same
        and only labels based on the AtomValueFact type IDs are used.

        :param node: given document node with text
        :param mentions: sequence of mention facts
        """
        pass

    @abstractmethod
    def decode_signatures(
            self,
            label_ids: LongTensor,
            label_ids_mapping: Sequence[str],
            *,
            ignore_label_id: int = -100
    ) -> dict[str, list[MentionSignature]]:
        """
        Decodes label_ids into labels and returns a dict of extracted model entity types with the corresponding mentions.

        :param label_ids: given sequence of labels ids to decode
        :param label_ids_mapping: sequence of used labels
        :param ignore_label_id: ID of ignored label
        """
        pass

    @abstractmethod
    def decode_label_ids(
            self,
            node: TIETextNode,
            label_ids: LongTensor,
            *,
            type_mapping: dict[str, set[MentionedFactsFactory]],
            label_ids_mapping: Sequence[str],
            precomputed_tokens: Sequence[Span] | None = None
    ) -> Iterator[AbstractFact]:
        """
        Decodes label_ids into labels and returns a set of extracted facts.

        :param node: original document node with text
        :param label_ids: given sequence of labels ids to decode
        :param domain: used domain
        :param type_mapping: mapping from entity types to the corresponding facts factory
        :param label_ids_mapping: sequence of used labels
        :param precomputed_tokens: precomputed tokens from the given node
        """
        pass


def _greedy_resolve_intersections(entities: Iterator[MentionFact]) -> Iterator[MentionFact]:
    try:
        prev = next(entities)
    except StopIteration:
        return
    yield prev
    for current in entities:
        prev_span = Span(prev.mention.start, prev.mention.end)
        current_span = Span(current.mention.start, current.mention.end)
        if current_span.intersects(prev_span):
            def format_mention(fact: MentionFact) -> str:
                mention = fact.mention
                mention_text = mention.node.content[mention.start:mention.end]
                return f'<{fact.value.str_type_id} at [{mention.start}, {mention.end}] in {mention.node_id}: "{mention_text}">'

            logger.warning(f"Intersecting entities mentions:\n"
                           f"\t{format_mention(prev)};\n"
                           f"\t{format_mention(current)}.\n"
                           f"Only first one will be used")
            continue
        yield current
        prev = current


def _match_to_tokens(tokens: Iterator[Span], entities: Iterator[MentionFact]) -> Iterator[tuple[int, int, str]]:
    try:
        current_entity = next(entities)
    except StopIteration:
        return  # no entities

    current_start: int | None = None
    token_idx = 0
    for token_idx, token in enumerate(tokens):
        while current_entity.mention.end <= token.start:
            if current_start is not None:
                yield current_start, token_idx, current_entity.value.str_type_id
                current_start = None
            try:
                current_entity = next(entities)
            except StopIteration:
                return
        if current_start is None and token.start >= current_entity.mention.start and token.end <= current_entity.mention.end:
            current_start = token_idx
        # TODO: check token boundary intersection
    if current_start is not None:
        yield current_start, token_idx + 1, current_entity.value.str_type_id


class _BIOFactoryLabellingStrategy(AbstractLabellingStrategy, metaclass=ABCMeta):
    def __init__(self, start_symbol: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._start_symbol = start_symbol if start_symbol is not None else None

    def encode_labels(self, node: TIETextNode, mentions: Iterable[MentionFact]) -> list[str]:
        text_mentions = filter(lambda m: isinstance(m.mention, TextNodeMention), mentions)
        # sort for greedy intersection resolution
        sorted_text_mentions = sorted(text_mentions, key=lambda m: (m.mention.start, -m.mention.end))
        labels = [self._outside_ent_label] * sum(map(len, node.sentences))

        if not len(sorted_text_mentions):
            return labels

        for ent_start, ent_end, ent_label in _match_to_tokens(node.tokens, _greedy_resolve_intersections(iter(sorted_text_mentions))):
            last_label = labels[ent_start - 1]  # it may get the label on position -1 on first iteration (it will be `O`)
            entity_labels = self._encode_entity(ent_end - ent_start, ent_label, last_label)
            labels[ent_start:ent_end] = (f'{label}-{ent_label}' for label in entity_labels)

        return labels

    def _is_object(self, label: str) -> bool:
        return label != self._outside_ent_label

    @staticmethod
    def _get_object_type(label: str) -> str:
        return '-'.join(label.split('-')[1:])

    @staticmethod
    def _get_object_encoding(label: str) -> str:
        return label.split('-')[0]

    def decode_signatures(
            self,
            label_ids: LongTensor,
            label_ids_mapping: Sequence[str],
            *,
            ignore_label_id: int = -100
    ) -> dict[str, list[MentionSignature]]:

        mentions: list[int] = []
        fact_type = None
        compressed_ids, counts = torch.unique_consecutive(label_ids, return_counts=True)

        label_position = 0
        fact_signatures: dict[str, list[MentionSignature]] = defaultdict(list)
        for label_id, count in zip(compressed_ids, counts):
            next_label_position = label_position + count
            positions = tuple(range(label_position, next_label_position))
            label_position = next_label_position

            if label_id == ignore_label_id:
                continue

            label = label_ids_mapping[label_id.item()]

            encode = self._get_object_encoding(label)
            current_type = self._get_object_type(label)

            if encode == self._start_symbol:  # beginning of a new entity
                if fact_type is not None:
                    # finish current entity
                    fact_signatures[fact_type].append(MentionSignature(mentions[0], mentions[-1]))

                # several start labels in a row == series of one-span entities
                fact_signatures[current_type].extend(MentionSignature(position, position) for position in positions[:-1])

                # start new entity for last span
                mentions = [positions[-1]]
                fact_type = current_type
                continue

            if encode != self._outside_ent_label and encode != self._start_symbol:  # inside an entity
                if fact_type is not None and fact_type != current_type:
                    # finish current entity
                    fact_signatures[fact_type].append(MentionSignature(mentions[0], mentions[-1]))
                    mentions = []

                mentions.extend(positions)
                fact_type = current_type
                continue

            # outside an entity

            if fact_type is not None:
                # finish current entity
                fact_signatures[fact_type].append(MentionSignature(mentions[0], mentions[-1]))

                fact_type = None
                mentions = []

        if fact_type is not None:
            # finish current entity
            fact_signatures[fact_type].append(MentionSignature(mentions[0], mentions[-1]))

        return fact_signatures

    def decode_label_ids(
            self,
            node: TIETextNode,
            label_ids: LongTensor,
            *,
            type_mapping: dict[str, set[MentionedFactsFactory]],
            label_ids_mapping: Sequence[str],
            precomputed_tokens: Sequence[Span] | None = None
    ) -> Iterator[AbstractFact]:

        fact_signatures = self.decode_signatures(label_ids, label_ids_mapping)
        tokens = precomputed_tokens if precomputed_tokens is not None else tuple(node.tokens)

        def build_facts_for_signatures(label: str, signatures: list[tuple[int, int]]) -> Iterator[AbstractFact]:
            for factory in type_mapping[label]:
                for start, end in signatures:  # convert signatures to mentions
                    mention = TextNodeMention(node, tokens[start].start, tokens[end].end)
                    yield from factory(mention, FactStatus.NEW)

        yield from chain.from_iterable(starmap(build_facts_for_signatures, fact_signatures.items()))

    @abstractmethod
    def _encode_entity(self, span_count: int, current_type: str, prev_label: str) -> list[str]:
        pass


class BIOLabellingStrategy(_BIOFactoryLabellingStrategy):
    def __init__(self):
        super().__init__('B', {'B', 'I'})

    def _encode_entity(self, span_count: int, current_type: str, prev_label: str) -> list[str]:
        return ['B'] + ['I'] * (span_count - 1)

    @property
    def type(self) -> LabellingStrategyType:
        return LabellingStrategyType.BIO


class IOBLabellingStrategy(_BIOFactoryLabellingStrategy):
    def __init__(self):
        super().__init__('B', {'B', 'I'})

    def _encode_entity(self, span_count: int, current_type: str, prev_label: str) -> list[str]:
        first = ['B'] if self._is_object(prev_label) and current_type == self._get_object_type(prev_label) else ['I']
        return first + ['I'] * (span_count - 1)

    @property
    def type(self) -> LabellingStrategyType:
        return LabellingStrategyType.IOB


_LABELLING_STRATEGIES = {
    LabellingStrategyType.BIO: BIOLabellingStrategy,
    LabellingStrategyType.IOB: IOBLabellingStrategy
}


def get_labelling_strategy(name: str | LabellingStrategyType) -> AbstractLabellingStrategy:
    strategy_type = LabellingStrategyType(name)
    return _LABELLING_STRATEGIES[strategy_type]()
