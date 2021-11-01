#!/usr/bin/env python3

from typing import Any, ClassVar, List, Optional, Set, Tuple, Union

import sexpdata
from sexpdata import Symbol

from desuwa.util import clean_sexp, tab_indent


class RuleSequenceTemplate(list):
    RuleClass: ClassVar

    def __init__(self, constraints: List[List[Union[Symbol, List[Symbol]]]], forward: bool):
        self.forward = forward
        self.denies: Set[int] = set()
        self.minimum: List[Optional[int]] = []
        for constraint in constraints:
            if isinstance(constraint, sexpdata.Symbol):
                _d = sexpdata.dumps(constraint)
                if _d == r"\?*":
                    self.append(None)
                    self.minimum.append(0)
                    continue
                elif _d == r"*":
                    self.minimum[-1] = 0
                    continue
                elif _d == r"\?":
                    if len(self.minimum) == 0:
                        # such as ( ?* ? [* * * * * ((住所末尾))] ?* )
                        self.append(None)
                        self.minimum.append(1)
                    else:
                        self.minimum[-1] = 1
                    continue
                elif _d == r"^":
                    self.denies.add(len(self))
                    continue
                else:
                    raise NotImplementedError
            self.append(self.RuleClass(constraint))
            self.minimum.append(None)

    def match(self, mylist: List, position: int, span_start: int, span_end: int) -> bool:
        assert 0 <= span_start <= span_end < len(mylist)
        rule_num = len(self)

        if self.forward:
            rule_idx = 0
            delta_step = 1
            position_final = span_end + 1
            rule_final = rule_num
        else:
            rule_idx = rule_num - 1
            delta_step = -1
            position_final = span_start - 1
            rule_final = -1
        _counts = self.minimum[:]
        wait_for_match = False

        while 0 <= rule_idx < rule_num:
            #             print('@@', rule_idx, position, span_start, span_end, position_final, rule_final, mylist)
            if position < span_start or position > span_end:
                # last is ANY and the size of ANY is 0 or *
                if rule_idx + delta_step == rule_final and (self[rule_idx] is None or self.minimum[rule_idx] == 0):
                    return True
                #                 print('yy', self.minimum[rule_idx])
                return False

            if self[rule_idx] is None:
                rule_idx += delta_step
                wait_for_match = True
                continue

            hit: bool = True
            if self[rule_idx].match(mylist, position):
                if rule_idx in self.denies:
                    hit = False
            else:
                if rule_idx not in self.denies:
                    hit = False

            #             print(f'hit= {hit}')
            if hit:
                position += delta_step
                if _counts[rule_idx] is None:
                    rule_idx += delta_step
                    wait_for_match = False
                else:
                    _new_cnt = _counts[rule_idx] - 1  # type: ignore
                    _counts[rule_idx] = _new_cnt  # type: ignore
                    #                     print('zz', _new_cnt, position, rule_idx)
                    # checked all rules
                    if (
                        _new_cnt <= 0
                        and (position < span_start or position > span_end)
                        and (rule_idx + delta_step == rule_final)
                    ):
                        return True
                continue
            else:
                if wait_for_match:
                    position += delta_step
                    continue
                elif _counts[rule_idx] is None:
                    return False
                elif _counts[rule_idx] > 0:  # type: ignore
                    return False
            rule_idx += delta_step
            wait_for_match = False

        # ここに到達した場合は，ルールは全て見ている
        # 原則終端まで達しているべき
        if position != position_final:
            # ただし最後のルールがany or *ならOK
            if self[rule_final - delta_step] is None or self.minimum[rule_final - delta_step] == 0:
                return True
            return False

        return True

    def __str__(self) -> str:
        out = f"{self.RuleClass.__name__} / Forward={self.forward}, Denies={self.denies}, Minimum={self.minimum}" ""
        if len(self) > 0:
            for i, v in enumerate(self):
                _v_str = tab_indent(str(v), 1)
                out += f"\n#{i}:\n{_v_str}"
        return out


class RuleTemplate(object):
    RuleClass: ClassVar
    SeqRuleClass: ClassVar

    def __init__(self, text: str):
        self.text = text
        _s = sexpdata.loads(clean_sexp(text))
        assert len(_s) >= 4
        self._center_len = 1
        self.prev_constraints: Optional[Any] = None
        if not self.RuleClass.is_any(_s[0]):
            self.prev_constraints = self.SeqRuleClass(_s[0], False)

        self.next_constraints: Optional[Any] = None
        if not self.RuleClass.is_any(_s[2]):
            self.next_constraints = self.SeqRuleClass(_s[2], True)

        self.constraints: Optional[Any] = None
        if not self.RuleClass.is_any(_s[1]):
            self.constraints = self.SeqRuleClass(_s[1], True)
            self._center_len = len(self.constraints)

        self.operations: List[Tuple[bool, str]] = []
        for v in _s[3:]:
            feature = sexpdata.dumps(v)
            remove = False
            if feature.startswith("^"):
                remove = True
                feature = feature[1:]
            self.operations.append((remove, feature))

    def match(self, mylist: List, target: int) -> bool:
        if self.prev_constraints:
            if target - 1 < 0:
                return False
            _matched = self.prev_constraints.match(mylist, target - 1, 0, target - 1)
            if not _matched:
                return False
        if self.constraints:
            _span_end = target + self._center_len - 1
            if _span_end >= len(mylist):
                return False
            _matched = self.constraints.match(mylist, target, target, _span_end)
            if not _matched:
                return False

        target += self._center_len

        if self.next_constraints:
            if target >= len(mylist):
                return False
            _matched = self.next_constraints.match(mylist, target, target, len(mylist) - 1)
            if not _matched:
                return False
        return True

    def apply(self, mylist: List, index: int):
        _matched = self.match(mylist, index)
        if not _matched:
            return
        for j in range(index, index + self._center_len):
            for (remove, myfeature) in self.operations:
                if remove:
                    mylist[j].fs.discard(myfeature)
                elif myfeature not in mylist[j].fs:
                    mylist[j].fs.add(myfeature)

    def __str__(self) -> str:
        _prev_str = tab_indent(str(self.prev_constraints), 1)
        _self_str = tab_indent(str(self.constraints), 1)
        _next_str = tab_indent(str(self.next_constraints), 1)
        out = f"""{self.RuleClass.__name__}: {self.text}
\tOperations: {self.operations}
\tPrev: {_prev_str}
\tSelf: {_self_str}
\tNext: {_next_str}"""

        return out
