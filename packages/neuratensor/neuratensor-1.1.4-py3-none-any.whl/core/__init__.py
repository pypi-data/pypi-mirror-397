"""
NeuraTensor Core Module
=======================

Core components including model and fused layers.

⚠️ WARNING: INTERNAL MODULE - DO NOT IMPORT DIRECTLY
   
   This module is for internal use only. If you are using the NeuraTensor SDK,
   you should NEVER import from here.
   
   Use the public API instead:
   
       from neuratensor import NeuraTensor, NeuraTensorConfig
       
       config = NeuraTensorConfig.preset("64m")
       model = NeuraTensor(config)
   
   Direct imports from core.* are NOT supported and may break in future versions.
"""

import os

# Product discipline: prevent accidental imports from SDK users
if "NEURATENSOR_INTERNAL" not in os.environ:
    raise ImportError(
        "\n\n"
        "=" * 70 + "\n"
        "ERROR: Cannot import from neuratensor.core directly.\n"
        "=" * 70 + "\n"
        "\n"
        "This module is for internal use only.\n"
        "\n"
        "If you are using the NeuraTensor SDK, please use the public API:\n"
        "\n"
        "    from neuratensor import NeuraTensor, NeuraTensorConfig\n"
        "    \n"
        "    config = NeuraTensorConfig.preset('64m')\n"
        "    model = NeuraTensor(config)\n"
        "\n"
        "If you are a NeuraTensor developer, set:\n"
        "\n"
        "    export NEURATENSOR_INTERNAL=1\n"
        "\n"
        "=" * 70 + "\n"
    )

from .model import NeuraTensorModel
from .fused_layer import FusedSNNSSMLayer

__all__ = ['NeuraTensorModel', 'FusedSNNSSMLayer']
