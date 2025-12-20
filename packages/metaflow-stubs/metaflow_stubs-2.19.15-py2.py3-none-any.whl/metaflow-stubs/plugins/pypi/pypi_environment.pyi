######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.19.15                                                                                #
# Generated on 2025-12-19T02:58:53.795785                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.plugins.pypi.conda_environment

from .conda_environment import CondaEnvironment as CondaEnvironment

class PyPIEnvironment(metaflow.plugins.pypi.conda_environment.CondaEnvironment, metaclass=type):
    ...

