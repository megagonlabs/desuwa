#!/usr/bin/env python3

import io
import unittest

import desuwa.util


class TestUtil(unittest.TestCase):
    def test_mlist(self):
        txt = """星 ほし 星 名詞 6 普通名詞 1 * 0 * 0 "代表表記:星/ほし カテゴリ:自然物 漢字読み:訓"
を を を 助詞 9 格助詞 1 * 0 * 0 NIL
みる みる みる 動詞 2 * 0 母音動詞 1 基本形 2 "代表表記:見る/みる 自他動詞:自:見える/みえる 補文ト"
@ みる みる みる 動詞 2 * 0 母音動詞 1 基本形 2 "代表表記:診る/みる ドメイン:健康・医学 補文ト"
EOS
"""
        f = io.StringIO(txt)

        mlists = [ml for ml in desuwa.util.get_mlist(f)]
        self.assertEqual(1, len(mlists))

    def test_tab_indent(self):
        intext = """123
456
789"""
        gold = """\t\t123
\t\t456
\t\t789"""
        self.assertEqual(gold, desuwa.util.tab_indent(intext, 2))

    def test_clean_sexp(self):
        intext = """< (?* [判定詞] ) ((ダミー1 ^ダミー2)) >"""
        gold = """( (?* (判定詞) ) ((ダミー1 ^ダミー2)) )"""
        self.assertEqual(gold, desuwa.util.clean_sexp(intext))


if __name__ == "__main__":
    unittest.main()
