#!/usr/bin/env python3


import unittest
from pathlib import Path

import sexpdata
from pyknp import MList

import tests.util
from desuwa.rule import Tags
from desuwa.rule.tag import TagRule, TagsRule
from desuwa.util import clean_sexp


class TestTagRule(unittest.TestCase):
    def setUp(self):
        path_parsed = Path(__file__).parent.joinpath('..', 'data', 'parsed.jumanpp')
        self.jumanpp = tests.util.DummyJumanpp(path_parsed)

    def test_any(self):
        sample = clean_sexp(''' < (?* [副詞 * * * * ((数量相対名詞修飾))] ) > ''')
        in_parts = [''' ( ?* ) ''', sample]
        golds = [True, False]
        for intext, gold in zip(in_parts, golds):
            p = sexpdata.loads(intext)
            self.assertEqual(gold, TagRule.is_any(p))

    def test_rule(self):
        in_samples = [
            clean_sexp('''< (?* [副詞 * * * * ((数量相対名詞修飾))] ) >'''),
            clean_sexp('''< (?*) ((ダミー1 ^ダミー2)) >'''),
            clean_sexp('''< (?* [* * * * * ((付属))]) >'''),
            clean_sexp('''< (?* [* * * * * ((付属))]*) >'''),
        ]
        gold_fc_strs = [
            'None',
            '''FC<SI=['ダミー1'], SNI=['ダミー2']>''',
            'None',
            'None',
        ]
        gold_nums = [
            2, 1, 2, 2,
        ]
        for intext, gold_fc_str, gold_num in zip(in_samples, gold_fc_strs, gold_nums):
            p = sexpdata.loads(intext)
            tr = TagRule(p)
            self.assertEqual(gold_fc_str, str(tr.feature_constraints))
            self.assertEqual(gold_num, len(tr.rules))

    def test_match(self):
        rule_text = clean_sexp('''< (?* [判定詞] ) ((ダミー1 ^ダミー2)) >''')
        tr = TagRule(sexpdata.loads(rule_text))

        mytest = '無停止だ'
        mlist: MList = self.jumanpp.get(mytest)
        tags = Tags(mlist, [0])
        tags[0].fs.add('ダミー0')
        self.assertEqual(False, tr.match(tags, 0))
        tags[0].fs.add('ダミー1')
        self.assertEqual(True, tr.match(tags, 0))

        rule_text2 = clean_sexp('''< (?* [接頭辞] ?*) >''')
        tr2 = TagRule(sexpdata.loads(rule_text2))
        self.assertEqual(True, tr2.match(tags, 0))

        rule_text4 = clean_sexp('''< (?* [接頭辞] ) ((ダミー9)) >''')
        tr4 = TagRule(sexpdata.loads(rule_text4))
        self.assertEqual(False, tr4.match(tags, 0))

        rule_text3 = clean_sexp('''< (?* [非マッチ] ) >''')
        tr3 = TagRule(sexpdata.loads(rule_text3))
        self.assertEqual(False, tr3.match(tags, 0))

    def test_rules(self):
        tags_rule_text = clean_sexp('''( ?* ^< (?*) ((ダミーA)) > * < (?*) ((^ダミーB)) >? ?* )''')
        p = sexpdata.loads(tags_rule_text)
        for order in [True, False]:
            tagr = TagsRule(p, order)
            self.assertEqual(True, len(str(tagr)) > 0)


if __name__ == '__main__':
    unittest.main()
