#!/usr/bin/env python3


import argparse
from pathlib import Path

import desuwa.predicate
from desuwa.rule import loads_tags
from desuwa.rule.rule_mrph import RulerMrph, RulesLevelMrph
from desuwa.rule.rule_tag import RulerTag, RulesLevelTag
from desuwa.util import get_mlist

DEFAULT_RULE_BASE = Path(__file__).parent.joinpath("knp_rules")
DEFAULT_MRPH_RULES = [
    DEFAULT_RULE_BASE.joinpath("mrph_filter.rule"),
    DEFAULT_RULE_BASE.joinpath("mrph_basic.rule"),
]

DEFAULT_TAG_RULES = [
    DEFAULT_RULE_BASE.joinpath("bnst_basic.rule"),
]


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--mrphrule", "-m", type=Path, action="append", default=DEFAULT_MRPH_RULES)
    oparser.add_argument("--tagrule", "-t", type=Path, action="append", default=DEFAULT_TAG_RULES)
    oparser.add_argument("--input", "-i", type=argparse.FileType("r"), default="-")
    oparser.add_argument("--output", "-o", type=argparse.FileType("w"), default="-")
    oparser.add_argument("--dump", action="store_true")
    oparser.add_argument("--segment", action="store_true")
    oparser.add_argument("--predicate", action="store_true")
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    ruler = RulerMrph([RulesLevelMrph(r_path) for r_path in opts.mrphrule])
    tag_ruler = None
    if opts.tagrule:
        tag_ruler = RulerTag([RulesLevelTag(r_path) for r_path in opts.tagrule])

    if opts.dump:
        for rules in ruler.rules_list:
            for rule in rules:
                print(rule)
                print()
        return

    if opts.predicate:
        with opts.input as inf, opts.output as outf:
            buf: str = ""
            for line in inf:
                buf += line
                if line != "EOS\n":
                    continue
                tags = loads_tags(buf)
                buf = ""
                for r in desuwa.predicate.parse(tags):
                    outf.write(f"{r}\n")
        return

    with opts.input as inf, opts.output as outf:
        for mlist in get_mlist(inf):
            tags = ruler.get_tags(mlist)
            if tag_ruler:
                tag_ruler.apply(tags)

            if opts.segment:
                outf.write(f"{tags}\n")
            else:
                outf.write(tags.dumps())


if __name__ == "__main__":
    main()
