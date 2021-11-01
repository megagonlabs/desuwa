#!/usr/bin/env python3

import unittest
from pathlib import Path

import tests.util
from desuwa.rule.rule_mrph import RulerMrph, RulesLevelMrph


class TestRuler(unittest.TestCase):
    def setUp(self):
        path_parsed = Path(__file__).parent.joinpath("data", "parsed.jumanpp")
        self.jumanpp = tests.util.DummyJumanpp(path_parsed)

    def test_segment(self):
        path_test = Path(__file__).parent.joinpath("data", "segment.tsv")
        rules_list = []
        for name in ["mrph_filter.rule", "mrph_auto_dic.rule", "mrph_basic.rule"]:
            rules_list.append(RulesLevelMrph(Path(__file__).parent.joinpath("..", "desuwa", "knp_rules", name)))
        ruler = RulerMrph(rules_list)

        with path_test.open() as inf:
            for line in inf:
                line = line.strip()
                if len(line) == 0 or line[0].startswith(";"):
                    continue

                mlist = self.jumanpp.get(line.replace("│", ""))
                tags = ruler.get_tags(mlist)
                self.assertEqual(line, str(tags))


if __name__ == "__main__":
    unittest.main()
