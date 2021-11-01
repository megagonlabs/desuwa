#!/usr/bin/env python3

from pathlib import Path
from typing import List, Optional

from pyknp import MList

from desuwa.rule import Features, Tags
from desuwa.rule.mrph import MrphRule, MrphsRule
from desuwa.rule.template import RuleTemplate
from desuwa.rule.util import parse_rule_text


class RuleLevelMrph(RuleTemplate):
    RuleClass = MrphRule
    SeqRuleClass = MrphsRule


class RulesLevelMrph(list):
    def __init__(self, fpath: Optional[Path] = None):
        if fpath:
            self.open(fpath)

    def apply(self, mlist: MList):
        self.initialize(mlist)
        for index in range(len(mlist)):
            for rule in self:
                rule.apply(mlist, index)

    def open(self, path_in: Path):
        with path_in.open() as inf:
            for i, r in enumerate(parse_rule_text(inf)):
                self.append(RuleLevelMrph(r))

    #         self[-1].operations.append((False, f'SRC={path_in.name}/{i}'))
    #         print(self[-1])

    @staticmethod
    def initialize(mlist: MList):
        if hasattr(mlist, "fs_inited"):
            return
        mlist.fs_inited = True

        for m in mlist:
            m.fs = Features()
            if m.imis == "NIL" or len(m.imis) == 0:
                continue
            for f in m.imis.split(" "):
                if f.startswith("代表表記"):
                    continue
                m.fs.add(f)
        mlist[0].fs.add("文頭")
        mlist[-1].fs.add("文末")


class RulerMrph(object):
    def __init__(self, rules_list: List[RulesLevelMrph]):
        self.rules_list = rules_list

    def apply(self, mlist: MList):
        for rules in self.rules_list:
            rules.apply(mlist)

    def get_tags(self, mlist: MList) -> Tags:
        self.apply(mlist)

        indices: List[int] = []
        for i, m in enumerate(mlist):
            if "タグ単位始" in m.fs or i == 0:
                indices.append(i)

        tags = Tags(mlist, indices)
        return tags
