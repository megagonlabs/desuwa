#!/usr/bin/env python3


import re
from typing import List, Optional, Union

import sexpdata
from pyknp import MList
from sexpdata import Symbol

from desuwa.rule import Features
from desuwa.rule.constraint import FeatureConstraints
from desuwa.rule.template import RuleSequenceTemplate


class MrphRule(object):
    @staticmethod
    def is_any(constraint: List[Union[Symbol, List[Symbol]]]) -> bool:
        if (
            len(constraint) == 1
            and isinstance(constraint[0], sexpdata.Symbol)
            and sexpdata.dumps(constraint[0]) == r"\?*"
        ):
            return True
        return False

    def __init__(self, constraint: List[Union[Symbol, List[Symbol]]]):
        rexp_str_list: List[str] = []
        self._feature_constraints: Optional[FeatureConstraints] = None

        def _deny(e: str) -> str:
            if e.startswith("^"):
                return f"(?!{e[1:]})"
            return e

        _deny_flg = False
        _any_str = "_ANY_"
        for c in constraint:
            if len(rexp_str_list) == 5:
                self._feature_constraints = FeatureConstraints(c, _deny_flg)
                _deny_flg = False
                break
            if isinstance(c, list):
                e = [_deny(sexpdata.dumps(_e)) for _e in c]
                q = "(" + "|".join(e) + ")"
                if _deny_flg:
                    q = f"(?!{q})"
                    _deny_flg = False
                rexp_str_list.append(q)
                continue
            assert isinstance(c, sexpdata.Symbol)
            _c_str = sexpdata.dumps(c)
            if _c_str == "*":
                rexp_str_list.append(_any_str)
            elif _c_str == "^":
                _deny_flg = True
            else:
                rexp_str_list.append(_deny(_c_str))

        for item in reversed(rexp_str_list):
            if item == _any_str:
                rexp_str_list.pop()
            else:
                break
        self._regexps = [None if v == _any_str else re.compile(v) for v in rexp_str_list]

    def match(self, mlist: MList, idx: int) -> bool:
        mrph = mlist[idx]
        if not hasattr(mrph, "fs"):
            mrph.fs = Features()

        if len(self._regexps) == 0:
            matched = True
        else:
            matched = True
            for idx, exp in enumerate(self._regexps):
                if exp is None:
                    continue
                val: str = [mrph.hinsi, mrph.bunrui, mrph.katuyou1, mrph.katuyou2, mrph.genkei][idx]
                if not exp.match(val):  # check from start
                    matched = False
                    break

        if matched and self._feature_constraints is not None:
            matched = self._feature_constraints.match(mrph.fs.get_keys())
        return matched

    def __str__(self) -> str:
        return f"[{self._regexps}, {self._feature_constraints}]"


class MrphsRule(RuleSequenceTemplate):
    RuleClass = MrphRule
