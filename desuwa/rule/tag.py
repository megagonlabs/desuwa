#!/usr/bin/env python3

from typing import Any, List, Optional, Union

from sexpdata import Symbol, dumps

from desuwa.rule import Tags
from desuwa.rule.constraint import FeatureConstraints
from desuwa.rule.mrph import MrphsRule
from desuwa.rule.template import RuleSequenceTemplate

TYPE_TAG_CONSTRAINT = List[List[Union[Symbol, List[Symbol]]]]


class TagRule(object):
    @staticmethod
    def is_any(constraint: List[Any]) -> bool:
        return len(constraint) == 1 and isinstance(constraint[0], Symbol) and dumps(constraint[0]) == r"\?*"

    def __init__(self, tag_constraint: TYPE_TAG_CONSTRAINT):
        direction_forward = True
        self.feature_constraints: Optional[FeatureConstraints] = None

        self.rules = MrphsRule(tag_constraint[0], direction_forward)
        if len(tag_constraint) == 2:
            self.feature_constraints = FeatureConstraints(tag_constraint[1], False)

    def __str__(self) -> str:
        return f"""TagRule: {self.rules}
FC: {self.feature_constraints}"""

    def match(self, tags: Tags, tag_index: int) -> bool:
        _start = tags.get_first_m_index(tag_index)
        _last = tags.get_last_m_index(tag_index)
        ok = self.rules.match(tags.mlist, _start, _start, _last)
        if ok and self.feature_constraints:
            return self.feature_constraints.match(tags[tag_index].fs)
        return ok


class TagsRule(RuleSequenceTemplate):
    RuleClass = TagRule
