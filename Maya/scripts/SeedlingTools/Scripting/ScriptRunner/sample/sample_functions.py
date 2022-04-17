# -*- coding: utf_8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function

import os
import maya.cmds as cmds

"""
このスクリプトはScriptRunnerの実行可能/不可能な関数のサンプルを記載しています。
特に重要なのは関数の定義部分の書き方です。

このツールは関数外のスクリプトの部分実行には対応していません。
必ず実行したい処理は関数にまとめてください。

クラスの書き方は「sample_classes.py」をご確認ください。
"""


# ===============================================
# Sample 1  |  例１
# ===============================================

# It can work  |  動作するスクリプト

# 関数の定義は可能な限り例に従ってください。
def print_can_work_1(text):
    """
    引数がstringかチェックしてprint & returnする関数
    """

    # 関数の中には実行したい処理を記述します。
    # 基本的にどんな処理でも動作する想定ですが、
    # 一部の例外はこの後の動作しない方のスクリプトで紹介します。

    if not isinstance(text, unicode) and not isinstance(text, str):
        cmds.error("Argument 'text' is not the type of string or unicode!!")

    print(text)

    # returnした値はScriptRunnerで実行後に「result : ""」の形で返されます
    return text

# Python3から可能な引数のタイプ指定・返り値のタイプ指定の表記があっても動作するようになっています。
# 補足：Python2で実行するとインポート時に必ずエラーになるためコメントアウトしています。
'''
def print_can_work_2(text: str) -> str:
    # 処理は割愛します
    return text
'''


# It cannot work  |  動作しないスクリプト

# 関数の定義内にTabが含まれていると認識されません。
#  ↓ ここがTabになっている
def	print_cannot_work_1(text):
    # 処理は割愛します
    return text


# ローカル関数もツールで読み込むことができます。
# ※クラス内のローカル関数は実行できないので注意してください。
def __print_cannot_work_2(text):
    """
    引数がstringかチェックしてprint & returnする関数
    """

    # Python2ではエラー文に日本語を含むマルチバイト文字を含むとScriptRunner本体でエラーになるおそれがあります。
    # 可能な限りエラー文にはマルチバイト文字を含めないでください。
    if not isinstance(text, unicode) and not isinstance(text, str):
        cmds.error("入力された引数はunicode型とstring型どちらでもありません！！")

	# 関数内であればTabを含んでいても動作はしますが、スクリプトプレビュー(リストのダブルクリック)で表示されないおそれがあります。
	print(text)
	return text


# ===============================================
# Sample 2  |  例２
# ===============================================

# It can work  |  動作するスクリプト

# 引数に初期値や可変長引数を与えても問題ありません。
def path_checker_can_work(path='C:\\Users', *args, **kwargs ):
    """
    入力されたパスのチェックをする関数
    """

    check_result = {
        "is_dir": None,
        "is_exist": None,
        "file_type": '',
    }

    if os.path.isfile(path):
        print(path + "はファイルのパスです")
        check_result["is_dir"] = False

        check_result["file_type"] = os.path.splitext(path)[1]
        print(path + "のファイルタイプは" + check_result["file_type"] + "です")
    else:
        print(path + "はディレクトリのパスです")
        check_result["is_dir"] = True

    if os.path.exists(path):
        print(path + "はPC上に存在しています")
        check_result["is_exist"] = True
    else:
        print(path + "はPC上に存在していません")
        check_result["is_exist"] = False

    return check_result


# ===============================================
# Sample 3  |  例３
# ===============================================

# It can work  |  動作するスクリプト

# もちろん引数や返り値がない関数でも動作します。
# 返り値の入力がないとき "result : None" になります。
def get_python_version_can_work():
    """
    pythonのバージョンを表示する関数
    """
    import sys
    print(sys.version)
