# -*- coding: utf_8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function

import os


"""
このスクリプトはScriptRunnerの実行可能/不可能なクラス内の関数サンプルのみを記載しています。
細かい記載ルールは「sample_functions.py」もご確認ください。
実行可能なのは以下のサンプルのようなスクリプトです。

このツールは関数外のスクリプトの部分実行には対応していません。
必ず実行したい処理は関数にまとめてください。

関数と、基礎的な書き方は「sample_functions.py」をご確認ください。
"""


# ===============================================
# Sample 1  |  例１
# ===============================================

# It can work  |  動作するスクリプト


# クラス定義の「()」の有無はどちらでも問題ありません。
# クラスの構造について、可能な限り例に従ってください。
class PrinterCanWork:
    '''
    stringを保持して出力するクラス
    このクラスは動作します！
    '''

    # 初期化の関数の書き方は自由ですが、シングルトンのような書き方をする場合はエラーになるおそれがあります。
    def __init__(self, text):
        self.text = ''

        if self.__is_unicode(text):
            self.text = text

        else:
            print('"text"には文字列を使用してください')

    # 通常の関数の書き方と同様に記載できます。
    def print_text(self):
        print(self.text)
        return self.text

    # クラスメソッドも読み込みできますが、
    # 処理前にクラスの初期化はされないため注意してください。
    # (設定は初期化なしで固定されています。要望があれば切り替えを実装します)
    @classmethod
    def check_and_print(cls, text):
        if isinstance(text, unicode):
            print(text)
            return text
        else:
            return None

    # ローカル関数もツールで読み込むことができますが、直接実行はできないため注意してください。
    def __is_unicode(self, text=''):
        if not text:
            return True if isinstance(self.text, unicode) else False
        else:
            return True if isinstance(text, unicode) else False


# ===============================================
# Sample 2  |  例２
# ===============================================

# It can work  |  動作するスクリプト

# 継承したクラスも動作可能です。
class PathCheckerCanWork(dict):
    def __init__(self, path=''):
        try:
            super(PathCheckerCanWork, self).__init__()
        except:
            super().__init__()

        self["is_dir"]      = None
        self["is_exist"]    = None
        self["file_type"]   = ''

        self.set_path(path)

    def set_path(self, path):
        if not path or not isinstance(path, unicode):
            return
        self.path = path


    # 引数に初期値や可変長引数を与えても問題ありません。
    def run_check(self):
        if os.path.isfile(self.path):
            print(self.path + "はファイルのパスです")
            self["is_dir"] = False

            self["file_type"] = os.path.splitext(self.path)[1]
            print(self.path + "のファイルタイプは" + self["file_type"] + "です")
        else:
            print(self.path + "はディレクトリのパスです")
            self["is_dir"] = True

        if os.path.exists(self.path):
            print(self.path + "はPC上に存在しています")
            self["is_exist"] = True
        else:
            print(self.path + "はPC上に存在していません")
            self["is_exist"] = False

        print(self)
        return self
