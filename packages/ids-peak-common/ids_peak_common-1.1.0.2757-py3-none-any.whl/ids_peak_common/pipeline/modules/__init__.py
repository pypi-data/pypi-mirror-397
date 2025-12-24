"""
.. defgroup:: ids_peak_common_python_pipeline_modules Pipeline Modules
.. ingroup:: ids_peak_common_python_pipeline

@brief Interface definitions for individual module types used within a pipeline.

This module defines the interfaces for pipeline modules, which represent individual
processing steps within a pipeline. Modules can be chained together to form flexible
and reusable data processing flows, each module focusing on a specific transformation
or operation.
"""

from .iautofeature_module import IAutoFeature
from .igain_module import IGain
from .imodule import IModule
