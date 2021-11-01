#!/usr/bin/env python3


from typing import List, Set

import sexpdata
from sexpdata import Symbol


class FeatureConstraint(object):
    def __init__(self, fs: Set[str]):
        self.should_include: List[str] = []
        self.should_not_include: List[str] = []
        for t in fs:
            if t.startswith("^"):
                self.should_not_include.append(t[1:])
            else:
                self.should_include.append(t)

    def match(self, fs: Set[str]) -> bool:
        for t in self.should_include:
            if t not in fs:
                return False
        for t in self.should_not_include:
            if t in fs:
                return False
        return True

    def __str__(self) -> str:
        return f"FC<SI={self.should_include}, SNI={self.should_not_include}>"


class FeatureConstraints(list):
    def __init__(self, constraint: List[List[Symbol]], deny=False):
        self.deny = deny
        if deny:
            raise NotImplementedError
        for _cs in constraint:
            _constraint: Set[str] = set()
            for _c in _cs:
                assert isinstance(_c, sexpdata.Symbol)
                f = sexpdata.dumps(_c)
                _constraint.add(f)
            self.append(FeatureConstraint(_constraint))

    def match(self, fs: Set[str]) -> bool:
        for fc in self:
            if fc.match(fs):
                return True
        return False

    def __str__(self) -> str:
        return f'{",".join([str(s) for s in self])}'
