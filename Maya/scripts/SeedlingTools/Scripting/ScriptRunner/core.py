# -*- coding: utf_8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function

import os
import sys
import re
from collections import OrderedDict
from functools import partial
import traceback

import xml.etree.ElementTree as et

import maya.cmds as cmds
import pymel.core as pm
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as omanim2


# ++++++++++++++++++++++++++++++++++++++++++++++++++
class ScriptRunner():

    # ========================================
    def __init__(self):

        self.script_runner_path = \
            os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')

        self.setting_file_path = \
            '{0}/.settings/script_runner_setting.xml'.format(self.script_runner_path)

        self.module_path = None

        self.script_path = None
        self.script_name = None

        self.module_name = None
        self.imported_module_name = None

        self.func_class_dict = OrderedDict()

        self.iterate_var_name = None
        self.iterate_var = None

        self.pre_command_var = None

        self.class_name = None
        self.function_name = None

        self.class_arg = None
        self.function_arg = None

        self.exec_cmd = None

        self.history_button_list = []

    # ========================================
    def create_ui(self):

        # ------------------------------
        # ウィンドウ作成、再作成
        window_name = u'ScriptRunner'

        self.__remove_same_window(window_name)

        window = cmds.window(
            window_name,
            title=window_name,
            w=450,
            s=True,
            mnb=False,
            mxb=False,
            rtf=True,
            cc=partial(self.__save_options, self.setting_file_path))

        # ------------------------------
        wrap_column = cmds.columnLayout(adj=True, rs=5)

        # ------------------------------
        cmds.columnLayout(adj=True, rs=5)
        cmds.text(
            l=u'-- スクリプト設定 --',
            h=16,
            bgc=[0.2, 0.2, 0.2],
            align='center'
        )

        # ------------------------------
        cmds.rowColumnLayout(nc=5, adj=1)
        cmds.textField('script_path', cc=self.__refresh_function_info)
        # cmds.textField('script_path', e=True, tx=self.__debug_path)
        cmds.text(l='', w=3)
        cmds.button(l=u'参照', c=self.__set_script_path)
        cmds.text(l='', w=3)
        cmds.button(l=u'更新', c=self.__refresh_function_info)

        cmds.setParent('..')
        cmds.setParent('..')

        # ------------------------------
        function_column = cmds.columnLayout(adj=True, rs=5)
        cmds.text(
            l=u'-- 実行設定 --',
            h=16,
            bgc=[0.2, 0.2, 0.2],
            align='center'
        )

        cmds.textScrollList(
            'function_list',
            ams=False,
            sc=self.__refresh_cls_func_field,
            dcc=self.__view_code)

        # ------------------------------
        # 設定
        cmds.columnLayout(adj=True, rs=5)

        # ------------------------------
        cmds.rowColumnLayout(nc=2, adj=2)
        cmds.checkBox("for", w=60)
        cmds.rowColumnLayout(nc=5, adj=4)
        cmds.text(l="(", align='right')
        cmds.textField('iterate_var_name', w=100, tx='iterate_var', en=False)
        cmds.text(l="in", align='center')
        cmds.textField('iterate_var')
        cmds.text(l=")", align='left')

        cmds.setParent('..')
        cmds.setParent('..')

        # ------------------------------
        cmds.rowColumnLayout(nc=2, adj=2)
        cmds.checkBox("pre cmd", w=70)
        cmds.textField('pre_command_text')

        cmds.setParent('..')

        cmds.text(l='', h=2, bgc=[0.2, 0.2, 0.2])

        # ------------------------------
        cmds.rowColumnLayout(nc=2, adj=2)
        cmds.text(l="class", w=60, align='left')
        cmds.textField('class_name')

        cmds.setParent('..')

        # ------------------------------
        cmds.rowColumnLayout(nc=3, adj=3)
        cmds.text(l='', w=10)
        cmds.text(l="init arg", w=60, align='left')
        cmds.textField('class_arg')

        cmds.setParent('..')

        # ------------------------------
        cmds.rowColumnLayout(nc=2, adj=2)
        cmds.text(l="function", w=60, align='left')
        cmds.textField('function_name')

        cmds.setParent('..')

        # ------------------------------
        cmds.rowColumnLayout(nc=3, adj=3)
        cmds.text(l='', w=10)
        cmds.text(l="func arg", w=60, align='left')
        cmds.textField('function_arg')

        cmds.setParent('..')
        cmds.setParent('..')
        cmds.setParent('..')

        # ------------------------------
        # 実行履歴
        cmds.columnLayout(adj=True, rs=5)
        cmds.rowColumnLayout(nc=3, adj=2)
        cmds.text(
            l=u'  < old',
            fn='smallObliqueLabelFont',
            w=50,
            bgc=[0.2, 0.2, 0.2],
            al='left'
        )
        cmds.text(
            l=u'-- 履歴 --',
            h=16,
            bgc=[0.2, 0.2, 0.2],
            al='center'
        )
        cmds.text(
            l=u'new >  ',
            fn='smallObliqueLabelFont',
            w=50,
            bgc=[0.2, 0.2, 0.2],
            al='right'
        )
        cmds.setParent('..')
        cmds.scrollLayout(h=56, bgc=[0.24, 0.24, 0.24])
        cmds.rowColumnLayout('run_history', nc=100)
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.setParent('..')

        # ------------------------------
        # セパレータ
        cmds.text(l='', h=2, bgc=[0.2, 0.2, 0.2])

        # ------------------------------
        cmds.rowColumnLayout(nc=3, adj=2)
        cmds.text(l='', w=5)
        cmds.button('run_script', l="Run Script", h=60, c=self.execute_script)
        cmds.text(l='', w=5)

        cmds.setParent('..')

        cmds.text(l='', h=1)
        cmds.setParent('..')

        cmds.showWindow(window)

        # ------------------------------
        # 前回使用時の設定読み込み
        self.__load_options(self.setting_file_path)

    # ========================================
    def __load_options(self, setting_file_path, *args):

        if not os.path.exists(setting_file_path):
            return

        tree = et.parse(setting_file_path)
        settings = tree.getroot()

        script_path = settings.find('ScriptPath')
        cmds.textField('script_path', e=True, tx=script_path.text)

        iterate_enable = settings.find('IterateEnable')
        cmds.checkBox('for', e=True, v=int(iterate_enable.text))

        iterate_var_name = settings.find('IterateValueName')
        cmds.textField('iterate_var_name', e=True, tx=iterate_var_name.text)

        iterate_var = settings.find('IterateValue')
        cmds.textField('iterate_var', e=True, tx=iterate_var.text)

        pre_command_enable = settings.find('PreCommandEnable')
        cmds.checkBox('pre_cmd', e=True, v=int(pre_command_enable.text))

        pre_command_var = settings.find('PreCommand')
        cmds.textField('pre_command_text', e=True, tx=pre_command_var.text)

        class_name = settings.find('ClassName')
        cmds.textField('class_name', e=True, tx=class_name.text)

        class_arg = settings.find('ClassArgument')
        cmds.textField('class_arg', e=True, tx=class_arg.text)

        function_name = settings.find('FunctionName')
        cmds.textField('function_name', e=True, tx=function_name.text)

        function_arg = settings.find('FunctionArgument')
        cmds.textField('function_arg', e=True, tx=function_arg.text)

        # ------------------------------
        # 情報の更新
        self.__refresh_function_info(None)

    # ========================================
    def __save_options(self, setting_file_path, *args):

        settings = et.Element('Settings')

        script_path = et.SubElement(settings, 'ScriptPath')
        script_path.text = cmds.textField('script_path', q=True, tx=True)

        iterate_enable = et.SubElement(settings, 'IterateEnable')
        iterate_enable.text = str(int(cmds.checkBox('for', q=True, v=True)))

        iterate_var_name = et.SubElement(settings, 'IterateValueName')
        iterate_var_name.text = cmds.textField('iterate_var_name', q=True, tx=True)

        iterate_var = et.SubElement(settings, 'IterateValue')
        iterate_var.text = cmds.textField('iterate_var', q=True, tx=True)

        iterate_enable = et.SubElement(settings, 'PreCommandEnable')
        iterate_enable.text = str(int(cmds.checkBox('pre_cmd', q=True, v=True)))

        pre_command_var = et.SubElement(settings, 'PreCommand')
        pre_command_var.text = cmds.textField('pre_command_text', q=True, tx=True)

        class_name = et.SubElement(settings, 'ClassName')
        class_name.text = cmds.textField('class_name', q=True, tx=True)

        class_arg = et.SubElement(settings, 'ClassArgument')
        class_arg.text = cmds.textField('class_arg', q=True, tx=True)

        function_name = et.SubElement(settings, 'FunctionName')
        function_name.text = cmds.textField('function_name', q=True, tx=True)

        function_arg = et.SubElement(settings, 'FunctionArgument')
        function_arg.text = cmds.textField('function_arg', q=True, tx=True)

        tree = et.ElementTree(settings)

        if not os.path.exists(os.path.dirname(setting_file_path)):
            os.makedirs(os.path.dirname(setting_file_path))

        tree.write(setting_file_path, encoding="UTF-8")

    # ========================================
    def __set_script_path(self, arg):
        """
        スクリプトファイルの参照ウィンドウと読み込み
        """

        before_path = cmds.textField('script_path', q=True, tx=True)
        script_path = cmds.fileDialog(dm='*.py')

        if not script_path:
            return
        if before_path == script_path:
            return

        cmds.textField('script_path', e=True, tx=script_path)

        # ------------------------------
        # 情報の更新
        self.__refresh_function_info(None)

    # ========================================
    def __refresh_cls_func_field(self):
        """
        クラス、関数リストのクリック時に、対応したテキスト入力欄を更新
        """

        func_item = cmds.textScrollList('function_list', q=True, si=True)[0]

        if not func_item:
            return

        func_info_re = \
            re.search(r'^(\w+)?\s?\(?(.*?)\)?:\s(\w+)\s?\(?(self,?\s?|cls,?\s?)?(.*?)\)?$', func_item)

        cmds.textField('class_name', e=True, tx=func_info_re.group(1))

        if func_info_re.group(2):
            class_arg_text = ','.join(
                [arg+'=' if not '=' in arg and not '*' in arg else arg for arg in self.func_class_dict[func_item]['init_func_args'].split(',')])
        else:
            class_arg_text = ''
        cmds.textField('class_arg', e=True, tx=class_arg_text)

        cmds.textField('function_name', e=True, tx=func_info_re.group(3))

        if func_info_re.group(5):
            function_arg_text = ','.join(
                [arg+'=' if not '=' in arg and not '*' in arg else arg for arg in func_info_re.group(5).split(',')])
        else:
            function_arg_text = ''
        cmds.textField('function_arg', e=True, tx=function_arg_text)

    # ========================================
    def __view_code(self, *args):
        """
        クラス、関数リストのダブルクリック時に、対応した関数のコードをプレビュー
        """
        func_item = cmds.textScrollList('function_list', q=True, si=True)[0]
        func_info = self.func_class_dict[func_item]
        # print(func_info.get_script())

        this_title = "ScriptPreview"

        self.__remove_same_window(this_title)

        this_window = cmds.window(
            this_title,
            title=this_title,
            s=True,
            mnb=False,
            mxb=False,
            rtf=True)
        cmds.scrollLayout(bgc=[0.2, 0.2, 0.2])
        cmds.rowColumnLayout(adj=2, nc=3)
        cmds.text(l='', w=5)
        cmds.columnLayout(adj=True)

        cmds.text(l='', h=5)
        cmds.text(l=func_info.get_script(), align='left')
        cmds.text(l='', h=5)

        cmds.setParent('..')
        cmds.text(l='', w=5)

        cmds.showWindow(this_window)

    # ========================================
    def execute_script(self, arg):
        """
        設定した情報でスクリプトを実行

        """
        # problem: ロードしたスクリプト外のモジュールで変更があると処理に反映されない。（初回ロードの状態が使われてしまうため、呼び出し関数内にreload()の記述が必要）
        # problem: UIから実行の情報を参照しているためバッチ処理等ができない。値の保持と実行処理を分けたい。-プリセット保存を検討
        # problem: 既存ディレクトリの親がドライブとして扱われている場合(substコマンド等)、スクリプトのパスが一致せずエラーになる

        # ------------------------------
        # 情報の設定
        self.class_name = cmds.textField('class_name', q=True, tx=True)
        self.function_name = cmds.textField('function_name', q=True, tx=True)

        self.class_arg = cmds.textField('class_arg', q=True, tx=True)
        self.function_arg = cmds.textField('function_arg', q=True, tx=True)

        self.exec_cmd = ""

        # ------------------------------
        # ほかスクリプトを読み込んだ際に被らないようにインポート後のモジュール名を作成
        # 例："(2つ親のフォルダ名_1つ親のフォルダ名_)スクリプト名"
        module_dirname_list = self.module_path.lower().split('/')
        module_root_name = ""

        # ディレクトリ名にPythonのワイルドカードが含まれていた場合の対応
        module_dirname_list = [re.sub(r'\W', '_', dn) for dn in module_dirname_list]

        # ドライブ表記が含まれていたら以前の表記を除外
        if ':' in module_dirname_list[-1]:
            pass
        elif ':' in module_dirname_list[-2]:
            module_root_name = module_dirname_list[-1] + "_"
        else:
            module_root_name = \
                module_dirname_list[-2] + "_" + module_dirname_list[-1] + "_"

        self.imported_module_name = module_root_name + self.script_name

        # ------------------------------
        # スクリプトパスとモジュール名の設定
        self.module_name = self.script_name

        is_sys_path_contains_module_path = False

        for p in sys.path:
            p = p.replace('\\', '/')

            # Pythonパスとモジュールパスが完全一致かチェック
            if p == self.module_path:
                is_sys_path_contains_module_path = True
                break

            # Pythonパスとモジュールパスが部分一致かチェック
            elif p in self.module_path:
                # 既存Pythonパスとの相対パスからモジュール名を作成
                self.module_name = "{0}.{1}".format(
                    os.path.relpath(self.module_path, p).replace('\\', '.'),
                    self.script_name)
                is_sys_path_contains_module_path = True
                break

        # モジュールパスが既存Pythonパスと一致しなかった場合、追加
        if not is_sys_path_contains_module_path:
            sys.path.append(self.module_path)

        # ------------------------------
        # スクリプトのインポート
        this_indent = ''
        self.exec_cmd += "import {0} as {1};\nreload({1});".format(
            self.module_name, self.imported_module_name)

        # ------------------------------
        # 繰り返し処理の設定
        self.iterate_var_name = cmds.textField('iterate_var_name', q=True, tx=True)
        self.iterate_var = cmds.textField('iterate_var', q=True, tx=True)

        if cmds.checkBox('for', q=True, v=True) and self.iterate_var:
            self.exec_cmd += "\n{2}for {0} in {1}:".format(
                self.iterate_var_name,
                self.iterate_var,
                this_indent)
            this_indent += '    '
            self.exec_cmd += "\n{0}print('{1}: ' + {1});".format(
                this_indent,
                self.iterate_var_name)

        self.pre_command_var = cmds.textField('pre_command_text', q=True, tx=True).replace(
            '; ', ';\n' + this_indent).replace(';', ';\n' + this_indent)

        if cmds.checkBox('pre_cmd', q=True, v=True) and self.pre_command_var:
            self.exec_cmd += "\n{0}{1}".format(this_indent, self.pre_command_var)

        # ------------------------------
        # 引数の設定
        # arg1, arg2 のような記述使用可、式の使用も可
        this_class_arg = self.class_arg
        this_function_arg = self.function_arg

        # ------------------------------
        # クラスがない関数、ベタ書きスクリプトを実行する場合
        if not self.class_name:
            self.exec_cmd += \
                "\n{3}result = {0}.{1}({2});".format(
                    self.imported_module_name,
                    self.function_name,
                    this_function_arg,
                    this_indent)

        # ------------------------------
        # クラスのインスタンス生成のみを実行する場合
        elif not self.function_name:
            self.exec_cmd += \
                "\n{3}class_obj = {0}.{1}({2});".format(
                    self.imported_module_name,
                    self.class_name,
                    this_class_arg,
                    this_indent)

        # ------------------------------
        # クラスのある関数を実行する場合
        else:
            self.exec_cmd += \
                "\n{5}class_obj = {0}.{1}({2});\n{5}result = class_obj.{3}({4});".format(
                    self.imported_module_name,
                    self.class_name,
                    this_class_arg,
                    self.function_name,
                    this_function_arg,
                    this_indent)

        if not self.exec_cmd:
            print("実行するコマンドが設定されていません")
            return

        self.exec_cmd += "\n{0}print('result : ' + str(result));".format(
            this_indent)

        print("\n[ScriptRunner] 以下のスクリプトを実行します:\n" + self.exec_cmd + '\n')

        try:
            exec(self.exec_cmd)
            cmds.button('run_script', e=True, bgc=[0.6, 0.9, 0.7])
            self.__add_run_history([0.6, 0.9, 0.7], self.imported_module_name+'.'+self.class_name+'.'+self.function_name)
            print("[ScriptRunner] 実行が正常に完了しました\n")

        except BaseException:
            cmds.button('run_script', e=True, bgc=[0.9, 0.6, 0.7])
            self.__add_run_history([0.9, 0.6, 0.7], self.imported_module_name+'.'+self.class_name+'.'+self.function_name)
            print("\n[ScriptRunner] 実行中にエラーが発生しました:")
            try:
                cmds.error(traceback.format_exc().decode('unicode_escape'))
            except ValueError:
                cmds.error("\n[ScriptRunner] スクリプトのエラー表記に日本語を含めないでください。\n")

    # ========================================
    def __add_run_history(self, button_color, message=''):
        """
        実行履歴参照用のボタンを作成
        """
        # problem: ボタンがタイムラインの一番左ではなく一番右に作成されてしまう
        # todo: 実行結果に対してラベルが数字だと分かりづらいので代替方法がないか検討
        this_history_count = len(self.history_button_list) + 1

        cmds.setParent('run_history')
        self.history_button_list.append(
            cmds.button(
                'run_history_%d' % this_history_count,
                l=this_history_count, bgc=button_color, w=40, h=40,
                sbm=message))

        this_save_path = self.script_runner_path + '/.history/history_{0}.xml'.format(this_history_count)
        self.__save_options(this_save_path)

        cmds.button(self.history_button_list[-1], e=True, c=partial(self.__load_options, this_save_path))

    # ========================================
    def __refresh_function_info(self, *args):
        """
        実行に必要な情報作成とUIの更新
        """

        self.script_path = cmds.textField('script_path', q=True, tx=True).replace('\\', '/')

        if not self.script_path:
            return
        if not os.path.exists(self.script_path):
            cmds.textScrollList('function_list', e=True, ra=True)
            return

        # ------------------------------
        # スクリプトパスからパッケージパスとスクリプト名取得
        script_path_re = \
            re.search(r'(^[A-Z]:/?\S*)/(\w+).py$', str(self.script_path))

        self.module_path = script_path_re.group(1)
        self.script_name = script_path_re.group(2)

        # ------------------------------
        # スクリプトを開いてクラスと関数の情報読み込み
        if sys.version_info.major is 2:
            with open(self.script_path, 'r') as script_file:
                script_string = script_file.read().decode('utf-8')
                self.__set_func_class_dict(script_string)
        else:
            with open(self.script_path, 'r', encoding='utf-8') as script_file:
                script_string = script_file.read()
                self.__set_func_class_dict(script_string)

        # ------------------------------
        # UIの更新
        self.__refresh_script_list()

    # ========================================
    def __set_func_class_dict(self, script_string):
        """
        渡されたスクリプトのテキスト情報からクラスと関数の関係性の辞書作成
        """

        parent_class_list = []
        current_depth = 0
        indent_count = 0

        func_info = None
        init_args = ''

        this_class = ""
        self.func_class_dict = OrderedDict()

        # ------------------------------
        for line in script_string.split(u'\n'):

            # ------------------------------
            # クラスを宣言している行の処理
            if 'class ' in line:
                class_re = \
                    re.search(r'(\s*)class\s(((\w)+)\s?\(?.*?\)?)\s?:', line)

                if not class_re:
                    class_re = re.search(r'class\s((\w)+)\s?:', line)

                if class_re:
                    init_args = ''

                    # クラスのネスト対応処理
                    if len(class_re.group(1)) > indent_count * current_depth:
                        # ネスト階層+1
                        indent_count = len(class_re.group(1)) if not current_depth else indent_count
                        parent_class_list.append(this_class)
                        current_depth = int(len(class_re.group(1)) / indent_count)
                    else:
                        # ネスト階層の修正
                        last_current_depth = current_depth
                        current_depth = int(len(class_re.group(1)) / indent_count) if len(class_re.group(1)) else 0
                        for i in range(last_current_depth-current_depth):
                            parent_class_list.pop()

                    if parent_class_list:
                        this_class = '.'.join(parent_class_list) + '.' + class_re.group(3)
                    else:
                        this_class = class_re.group(3)

            # ------------------------------
            # 関数を宣言している行の処理
            elif 'def ' in line:
                func_info = FuncInfo()
                func_info.append_script_line(line)
                if indent_count and current_depth:
                    func_info.set_base_indent(' ' * indent_count * current_depth)

                func_re = \
                    re.search(r'(\s*)def\s((\w)+\s?\(?(.*?)\)?)\s?:', line)

                if not func_re:
                    func_re = re.search(r'def\s((\w)+)\s?:', line)
                    if not func_re: continue

                special_func_re = re.search(r'__(\S*)__', func_re.group(2))
                if special_func_re:
                    if special_func_re.group(1) == 'init':
                        init_args = re.search(r'((self,?\s?)|(cls,?\s?))?(.*)', func_re.group(4)).group(4)
                    continue

                func_info.set_init_func_args(init_args)

                # ネスト対応処理
                if len(func_re.group(1)) > indent_count * current_depth:
                    # ネスト階層+1
                    indent_count = len(func_re.group(1)) if not current_depth else indent_count
                    current_depth = int(len(func_re.group(1)) / indent_count)
                    parent_class_list.append(this_class)
                else:
                    # ネスト階層の修正
                    last_current_depth = current_depth
                    current_depth = int(len(func_re.group(1)) / indent_count) if len(func_re.group(1)) else 0
                    for i in range(last_current_depth-current_depth):
                        parent_class_list.pop()

                if not func_re.group(1):
                    self.func_class_dict[': ' + func_re.group(2)] = func_info
                    continue

                if func_info['init_func_args']:
                    self.func_class_dict[this_class + '(' + func_info['init_func_args'] + '): ' + func_re.group(2)] = func_info
                else:
                    self.func_class_dict[this_class + ': ' + func_re.group(2)] = func_info

            # ------------------------------
            # クラスも関数も宣言していない行
            else:
                if func_info and not re.search(r'(\s*)(.*)', line).group(2).startswith('#'):
                    func_info.append_script_line(line)

    # ========================================
    def __refresh_script_list(self):
        """
        クラスと関数のテキストスクロールリスト更新
        """

        cmds.textScrollList('function_list', e=True, ra=True)

        if not self.func_class_dict:
            return

        for func in self.func_class_dict.keys():
            cmds.textScrollList(
                'function_list',
                e=True,
                a=func)

    # ========================================
    def __remove_same_window(self, window_name):
        """
        同じウィンドウがすでに開いていたら閉じる
        """

        if cmds.window(window_name, ex=True):
            cmds.deleteUI(window_name, wnd=True)

        elif cmds.windowPref(window_name, ex=True):
            cmds.windowPref(window_name, r=True)

# ++++++++++++++++++++++++++++++++++++++++++++++++++
class FuncInfo(dict):
    def __init__(self):
        try:
            super(FuncInfo, self).__init__()
        except:
            super().__init__()

        self.initialize()

    # ========================================
    def initialize(self):
        self['base_indent'] = ''
        self['script_lines'] = []
        self['init_func_args'] = ''
        self['new_func_args'] = ''

    # ========================================
    def append_script_line(self, line):
        self['script_lines'].append(line)

    # ========================================
    def get_script(self, indent_str=''):
        if not indent_str and self['base_indent']:
            indent_str = self['base_indent']

        if len(indent_str) > 0:
            return '+' * 50 + '\n' + '\n'.join([re.search(r'^(' + indent_str + r')?(.*)', l).group(2) for l in self['script_lines']]) + '+' * 50 + '\n'
        else:
            return '+' * 50 + '\n' + '\n'.join(self['script_lines']) + '+' * 50 + '\n'

    # ========================================
    def set_init_func_args(self, func_args):
        self['init_func_args'] = func_args

    # ========================================
    def set_new_func_args(self, func_args):
        self['new_func_args'] = func_args

    # ========================================
    def set_base_indent(self, indent):
        self['base_indent'] = indent
