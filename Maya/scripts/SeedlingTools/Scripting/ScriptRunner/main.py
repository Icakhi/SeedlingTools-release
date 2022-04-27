# -*- coding: utf-8 -*-

# ****************************************************************
# SeedlingTools - ScriptRunner
# version: 0.2.0
# ****************************************************************
# This tool is license-free and may be used commercially and modified for personal use only.
# However, secondary distribution, sale, or transfer of modified data is prohibited. Please do not do so.
# Licenses are subject to change in the future. We will announce any changes on Twitter.

# Please read the initial release document for more information:
# https://github.com/Icakhi/SeedlingTools-release/releases/tag/v0.1.0

# This is a pre-release and may have some issues.
# If you encounter any errors, please contact me.
# ****************************************************************
# Created by: icakhi
# Twitter: @icakhi
# Github: https://github.com/Icakhi/SeedlingTools-release
# ****************************************************************

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function

import sys

# import ScriptRunner.core as script_runner_core
import SeedlingTools.Scripting.ScriptRunner.core as script_runner_core


# ++++++++++++++++++++++++++++++++++++++++++++++++++
def main():
    if sys.version_info.major is 3:
        import importlib
        importlib.reload(script_runner_core)
    else:
        reload(script_runner_core)

    script_runner = script_runner_core.ScriptRunner()
    script_runner.create_ui()


# ++++++++++++++++++++++++++++++++++++++++++++++++++
if __name__ == '__main__':
    main()
