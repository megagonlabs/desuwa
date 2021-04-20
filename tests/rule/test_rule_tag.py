#!/usr/bin/env python3

import unittest
from pathlib import Path

from pyknp import MList

import tests.util
from desuwa.rule import Tags
from desuwa.rule.rule_tag import RuleLevelTag


class TestRuler(unittest.TestCase):

    def setUp(self):
        path_parsed = Path(__file__).parent.joinpath('..', 'data', 'parsed.jumanpp')
        self.jumanpp = tests.util.DummyJumanpp(path_parsed)

    def test_rule(self):
        dummyf = 'DUMMY'
        myrule = f'''( ( ?* ) ( < (?* [名詞] ?*) > ) ( <( ?* [助詞] )> ?* ) {dummyf} )'''
        r = RuleLevelTag(myrule)
        self.assertEqual(True, len(str(r)) > 0)

        mytest = '私は│パンを│食べて│友人は│ご飯を│食べていました。'
        indices = [0, 2, 4, 5, 7, 9]
        mlist: MList = self.jumanpp.get(mytest.replace('│', ''))
        tags = Tags(mlist, indices)
        self.assertEqual(mytest, str(tags))

        golds = [True, False, False, True, False, False]
        center_golds = [True, True, False, True, True, False]
        next_golds = [True, False, True, True, False, None]
        assert r.constraints is not None
        assert r.next_constraints is not None

        for idx, (gold, center_gold, next_gold) \
                in enumerate(zip(golds, center_golds, next_golds)):
            self.assertEqual(None, r.prev_constraints)

            self.assertEqual(center_gold,
                             r.constraints.match(tags, idx,
                                                 idx, idx))
            if idx != len(tags) - 1:
                _m = r.next_constraints.match(tags, idx + 1,
                                              idx + 1,
                                              len(tags) - 1)
                self.assertEqual(next_gold, _m)

            self.assertEqual(gold, r.match(tags, idx))


if __name__ == '__main__':
    unittest.main()
