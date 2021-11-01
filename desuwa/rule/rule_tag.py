#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import List, Optional

from desuwa.rule import Tags
from desuwa.rule.tag import TagRule, TagsRule
from desuwa.rule.template import RuleTemplate
from desuwa.rule.util import parse_rule_text


class RuleLevelTag(RuleTemplate):
    RuleClass = TagRule
    SeqRuleClass = TagsRule


class RulesLevelTag(list):
    def __init__(self, fpath: Optional[Path] = None):
        if fpath:
            self.open(fpath)

    def apply(self, tags: Tags):
        # tag-> Reversed
        for index in reversed(range(len(tags))):
            for rule in self:
                rule.apply(tags, index)

    def open(self, path_in: Path):
        with path_in.open() as inf:
            for i, r in enumerate(parse_rule_text(inf)):
                self.append(RuleLevelTag(r))


class RulerTag(object):
    def __init__(self, rules_list: List[RulesLevelTag]):
        self.rules_list = rules_list

    def apply(self, tags: Tags):
        for rules in self.rules_list:
            rules.apply(tags)


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--rule", "-r", type=Path, action="append", required=True)
    oparser.add_argument("--input", "-i", type=argparse.FileType("r"), default="-")
    oparser.add_argument("--output", "-o", type=argparse.FileType("w"), default="-")
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    ruler = RulerTag([RulesLevelTag(r_path) for r_path in opts.rule])

    for rules in ruler.rules_list:
        for rule in rules:
            print(rule)
            print()


if __name__ == "__main__":
    main()
