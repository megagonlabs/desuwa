#!/usr/bin/env python3

import unittest
from pathlib import Path
from typing import List

from pyknp import MList, Morpheme

import tests.util
from desuwa.rule.constraint import FeatureConstraint
from desuwa.rule.rule_mrph import RuleLevelMrph, RulerMrph, RulesLevelMrph


class TestRuler(unittest.TestCase):
    def setUp(self):
        path_parsed = Path(__file__).parent.joinpath("..", "data", "parsed.jumanpp")
        self.jumanpp = tests.util.DummyJumanpp(path_parsed)

    def test_rule(self):
        myrule = """( ( ?* ) ( [接頭辞 * * * (非 不 無 未)] ) ( ?* ) 否定 )"""
        r = RuleLevelMrph(myrule)
        self.assertEqual([d for d in r.operations], [(False, "否定")])
        self.assertEqual(None, r.prev_constraints)
        self.assertEqual(None, r.next_constraints)
        self.assertEqual(True, len(str(r)) > 0)

        mytest = "無停止だ"
        mlist: MList = self.jumanpp.get(mytest)
        RulesLevelMrph.initialize(mlist)
        assert r.constraints is not None
        self.assertEqual(True, r.constraints.match(mlist, 0, 0, 0))
        self.assertEqual(False, r.constraints.match(mlist, 1, 1, 1))
        self.assertEqual(False, r.constraints.match(mlist, 2, 2, 2))

        for idx, gold in enumerate([True, False, False]):
            self.assertEqual(gold, r.match(mlist, idx))
            r.apply(mlist, idx)
        self.assertEqual(True, "否定" in mlist[0].fs)
        self.assertEqual(False, "否定" in mlist[1].fs)
        self.assertEqual(False, "否定" in mlist[2].fs)

        myrule2 = """( ( ?* ) ( [^判定詞] ) ( ?* ) テスト ^否定 ^ダミー)"""
        r2 = RuleLevelMrph(myrule2)
        assert r2.constraints is not None
        self.assertEqual(True, r2.constraints.match(mlist, 0, 0, 0))
        self.assertEqual(True, r2.constraints.match(mlist, 1, 1, 1))
        self.assertEqual(False, r2.constraints.match(mlist, 2, 2, 2))
        for idx, gold in enumerate([True, True, False]):
            self.assertEqual(gold, r2.match(mlist, idx))
            r2.apply(mlist, idx)
        self.assertEqual(True, "テスト" in mlist[0].fs)
        self.assertEqual(True, "テスト" in mlist[1].fs)
        self.assertEqual(False, "テスト" in mlist[2].fs)

        myrule3 = """( ( ?* ) ( [^(接頭辞 判定詞)] ) ( ?* ) テスト )"""
        r3 = RuleLevelMrph(myrule3)
        assert r3.constraints is not None
        self.assertEqual(False, r3.constraints.match(mlist, 0, 0, 0))
        self.assertEqual(True, r3.constraints.match(mlist, 1, 1, 1))
        self.assertEqual(False, r3.constraints.match(mlist, 2, 2, 2))
        for idx, gold in enumerate([False, True, False]):
            self.assertEqual(gold, r3.match(mlist, idx))

    def test_complex_rule(self):
        mytest = "無停止だ"
        mlist: MList = self.jumanpp.get(mytest)
        RulesLevelMrph.initialize(mlist)
        myrules1: List[str] = [
            """( ( ?* ) ( [* サ変名詞] ) ( ?* ) ダミー )""",
            """( ( [ダミー]* [接頭辞] ) ( [* サ変名詞] ) ( ?* ) ダミー )""",
            """( ( [接頭辞] ) ( [* サ変名詞] ) ( ?* ) ダミー )""",
            """( ( [接頭辞]* ) ( [* サ変名詞] ) ( ?* ) ダミー )""",
            """( ( [接頭辞]? ) ( [* サ変名詞] ) ( ?* ) ダミー )""",
            """( ( ^[名詞]* ) ( [* サ変名詞] ) ( ?* ) ダミー )""",
            """( ( ^[名詞]? ) ( [* サ変名詞] ) ( ?* ) ダミー )""",
            """( ( ?* ) ( [* サ変名詞] ) ( [判定詞] ) ダミー )""",
            """( ( ?* ) ( [* サ変名詞] ) ( [判定詞]* ) ダミー )""",
            """( ( ?* ) ( [* サ変名詞] ) ( [判定詞]? ) ダミー )""",
        ]
        for myrule1 in myrules1:
            r1 = RuleLevelMrph(myrule1)
            for idx, gold in enumerate([False, True, False]):
                self.assertEqual(gold, r1.match(mlist, idx))

        r2 = RuleLevelMrph("""( ( ^[助詞 格助詞] ) ( [* サ変名詞] ) ( [名詞]* ) ダミー )""")
        for idx, gold in enumerate([False, True, False]):
            self.assertEqual(gold, r2.match(mlist, idx))

        r3 = RuleLevelMrph("""( ( [名詞]* ) ( [判定詞] ) ( ?* ) ダミー )""")
        for idx, gold in enumerate([False, False, True]):
            self.assertEqual(gold, r3.match(mlist, idx))

    def test_feature(self):
        fc1 = FeatureConstraint({"f1", "^f2"})
        self.assertEqual(True, fc1.match({"f1"}))
        self.assertEqual(True, fc1.match({"f1", "f3"}))
        self.assertEqual(False, fc1.match({"f2"}))
        self.assertEqual(False, fc1.match({"f1", "f2"}))

    def test_tag(self):
        myrules = [
            """( ( ?* ) ( [* * * * * ((文頭))] ) ( ?* ) タグ単位始 )""",
            """ ( ( ?* [* * * * * ((^非独立接頭辞))] )
( [* * * * * ((非独立接頭辞)(内容語))] )
( ?* ) タグ単位始 )""",
        ]
        rules = RulesLevelMrph()
        for mr in myrules:
            rules.append(RuleLevelMrph(mr))
        mlist: MList = self.jumanpp.get("お調べ")
        RulesLevelMrph.initialize(mlist)
        mlist[0].fs.add("非独立接頭辞")
        mlist[1].fs.add("内容語")
        rules.apply(mlist)
        for idx, gold in enumerate([True, False]):
            self.assertEqual(gold, "タグ単位始" in mlist[idx].fs)

    def test_tag2(self):
        myrules = [
            """( ( ?* [(動詞 接尾辞 助動詞 形容詞 判定詞) * *
(タ系連用テ形 ダ列タ系連用テ形 デアル列タ系連用テ形)] )
( [形容詞 * * ^(タ形 基本連用形) (良い よい いい 宜しい よろしい)] ) ( ?* ) 付属 )"""
        ]
        rules = RulesLevelMrph()
        for mr in myrules:
            rules.append(RuleLevelMrph(mr))
        mlist: MList = self.jumanpp.get("広くなくていいです")
        RulesLevelMrph.initialize(mlist)
        rules.apply(mlist)
        #         print(rules[0])
        #         print([m.fs for m in mlist])
        self.assertEqual(True, "付属" in mlist[2].fs)

    def test_feature1(self):
        myrules = [
            """ ( ( ?* ) ( [動詞 * * * (いただく)] ) ( ?* ) 付属 )""",
            """ ( ( ?* [* * * * * ((サ変))] ) ( [動詞 * * * (いただく)] ) ( ?* ) 付属 )""",
            """ ( ( ?* [* * * * * ((サ変))] [特殊 括弧終]* ) ( [動詞 * * * (頂ける いただく)] ) ( ?* ) 付属 )""",
        ]
        for rule in myrules:
            mlist: MList = self.jumanpp.get("利用いただく")
            RulesLevelMrph.initialize(mlist)
            rs = RulesLevelMrph()
            r = RuleLevelMrph(rule)
            rs.append(r)
            mlist[0].fs.add("サ変")
            rs.apply(mlist)
            self.assertEqual(True, "付属" in mlist[1].fs)

    def test_feature2(self):
        myrule = """( ( ?* [接頭辞 名詞接頭辞 * * (御 お)] [動詞 * * 基本連用形] )
( [動詞 * * * (する 出来る できる 致す いたす 為さる なさる
下さる くださる 頂く いただく 頂ける いただける
願う ねがう 願える ねがえる 申し上げる 申しあげる)] ) ( ?* ) 付属 )"""
        mlist: MList = self.jumanpp.get("お楽しみいただけます。")
        RulesLevelMrph.initialize(mlist)
        r = RuleLevelMrph(myrule)
        self.assertEqual(True, r.match(mlist, 2))

        rs = RulesLevelMrph()
        rs.append(r)
        ruler = RulerMrph([rs])
        ruler.apply(mlist)
        self.assertEqual({"付属", "付属動詞候補（タ系）", "可能動詞:頂く/いただく"}, mlist[2].fs.values)
        self.assertEqual(True, "可能動詞" in mlist[2].fs)
        self.assertEqual(False, "可能動詞:頂く" in mlist[2].fs)
        self.assertEqual(True, "可能動詞:頂く/いただく" in mlist[2].fs)
        self.assertEqual(False, "" in mlist[2].fs)
        tags = ruler.get_tags(mlist)
        self.assertEqual(1, len(tags))
        self.assertEqual(5, len(tags[0]))
        self.assertEqual(True, isinstance(tags[0][0], Morpheme))


if __name__ == "__main__":
    unittest.main()
