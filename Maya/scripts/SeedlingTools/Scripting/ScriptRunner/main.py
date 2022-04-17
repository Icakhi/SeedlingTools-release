# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function

# import ScriptRunner.core as script_runner_core
import SeedlingTools.Scripting.ScriptRunner.core as script_runner_core


# ++++++++++++++++++++++++++++++++++++++++++++++++++
def main():
    reload(script_runner_core)

    script_runner = script_runner_core.ScriptRunner()
    script_runner.create_ui()


# ++++++++++++++++++++++++++++++++++++++++++++++++++
if __name__ == '__main__':
    main()
