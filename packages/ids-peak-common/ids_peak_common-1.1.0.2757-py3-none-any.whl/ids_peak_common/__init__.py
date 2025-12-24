r"""!
.. defgroup:: ids_peak_common_python Python
.. ingroup:: ids_peak_common

@brief
  The Python interface for the IDS peak common library.

The Python binding for the \htmlonly IDS peak common \endhtmlonly library
is delivered as a wheel via the Python Package Index (PyPI).
It can be installed using `pip`:

```
pip install ids_peak_common
```

To use \htmlonly IDS peak common \endhtmlonly in your project import ids_peak_common by calling:

```{.python}
from ids_peak_common import *
```


.. defgroup:: ids_peak_common_python_exceptions Exceptions
.. ingroup:: ids_peak_common_python

@brief Custom exceptions used throughout the library.


.. defgroup:: ids_peak_common_python_pipeline Image Pipeline
.. ingroup:: ids_peak_common_python

@brief Interfaces and types for defining and controlling data processing pipelines.

This group contains the core interfaces for creating and managing pipelines,
which process input data through a sequence of configurable modules to produce output.
It provides the foundational classes and utilities for pipeline configuration,
execution, and lifecycle management.


.. defgroup:: ids_peak_common_python_serialization Serialization
.. ingroup:: ids_peak_common_python

@brief Interfaces for defining serialization and deserialization behavior.

It focuses on the contract layer without providing concrete serialization logic
or implementations.

These interfaces are intended to be implemented by other components
or libraries to support specific serialization formats (e.g., binary,
text-based formats, or custom protocols).

The goal of this module is to ensure a consistent and extensible
approach to serialization throughout the library ecosystem.


.. defgroup:: ids_peak_common_python_types Types
.. ingroup:: ids_peak_common_python

@brief General-purpose types and interfaces used throughout the library.

This module contains a collection of core types that are widely used across
different components of the library.
These types among others include utility types
such as intervals, pixel formats, image view interfaces,
and other foundational constructs.

The types in this group are intended to provide reusable, versatile building blocks
for applications and other libraries built on top of this component.
"""
from . import pipeline
from . import serialization
from .datatypes import (Range, Channel, PixelFormat, IImageView, Metadata, MetadataKey, Vector, Size, Point, Interval,
                        Rectangle)
from .exceptions import (IOException, NotSupportedException, InternalErrorException, OutOfRangeException,
                         TimeoutException, LibraryNotInitializedException, BadAllocException, InvalidCastException,
                         InvalidParameterException, CommonException)
