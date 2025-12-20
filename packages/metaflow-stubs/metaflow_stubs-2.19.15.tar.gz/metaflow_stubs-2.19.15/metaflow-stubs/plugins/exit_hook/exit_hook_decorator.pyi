######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.19.15                                                                                #
# Generated on 2025-12-19T02:58:53.810137                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.decorators

from ...exception import MetaflowException as MetaflowException

class ExitHookDecorator(metaflow.decorators.FlowDecorator, metaclass=type):
    def flow_init(self, flow, graph, environment, flow_datastore, metadata, logger, echo, options):
        ...
    ...

