"""
.. defgroup:: ids_peak_icv_python Python
.. ingroup:: ids_peak_icv_library

@brief
  The Python interface for the IDS peak ICV library.

The interface is delivered as a wheel via the Python Package Index (PyPI).
It can be installed using `pip`:

```bash
pip install ids_peak_icv
```

To use @htmlonly IDS peak ICV @endhtmlonly in your project import ids_peak_icv by calling:

```python
import ids_peak_icv
```


.. defgroup:: ids_peak_icv_python_pipeline Image Pipeline
.. ingroup:: ids_peak_icv_python

@brief
  Comprehensive image processing pipeline system for real-time image transformation and enhancement.

The Image Pipeline provides a complete, modular framework for processing raw sensor data through
a series of configurable transformation stages. It supports a wide range of image processing
operations from basic format conversions to advanced enhancement algorithms.

## Architecture Overview

The pipeline follows a modular design with two main component types:
- **Modules**: Core processing units that perform specific image transformations
- **Features**: High-level interfaces that provide user-friendly access to module functionality

## Processing Flow

The pipeline processes images through sequential stages:

- **Data Unpacking** - Converts packed sensor formats to standard representations
- **Defect Correction** - Removes hot pixels and other sensor artifacts
- **Geometric Transformations** - Handles binning, decimation, rotation, and mirroring
- **Gain Control** - Applies brightness and white balance adjustments
- **Color Processing** - Performs debayering and color space transformations
- **Enhancement** - Applies sharpening, gamma correction, and tone mapping
- **Format Conversion** - Converts to the desired output pixel format

For more information refer to the @ref guide_pipeline Guide.


.. defgroup:: ids_peak_icv_python_serialization Serialization
.. ingroup:: ids_peak_icv_python

@brief
  Functions and classes for converting objects into a storable format.

Serialization refers to the process of transforming
an object’s state or a data structure
into a format suitable for storage or transmission
(e.g., files, databases, or network streams).
This allows data to be persisted
and later reconstructed through deserialization,
restoring the original structure and values.

Typical use cases include:
- Saving application state to disk
- Transferring data between processes or systems


.. defgroup:: ids_peak_icv_python_types Types
.. ingroup:: ids_peak_icv_python

@brief
  Collection of fundamental data types used throughout the library.


.. defgroup:: ids_peak_icv_python_calibration Calibration
.. ingroup:: ids_peak_icv_python

@brief
Group of functions for calibration.


.. defgroup:: ids_peak_icv_python_filters Filters
.. ingroup:: ids_peak_icv_python

@brief
Image filters.


.. defgroup:: ids_peak_icv_python_painting Painting
.. ingroup:: ids_peak_icv_python

@brief
Functions for painting on an image.


.. defgroup:: ids_peak_icv_python_selectors Selectors
.. ingroup:: ids_peak_icv_python

@brief
Provides utilities to filter objects from a given set.

A Selector encapsulates a filtering operation
applied to a given set of objects.
Instead of modifying the original set,
each selection function returns a new Selector object
that represents the filtered subset.

This design enables the chaining of multiple selection criteria.

To access the currently selected objects,
use the respective accessor functions,
such as `RegionSelector.regions`.


.. defgroup:: ids_peak_icv_python_thresholds Thresholds
.. ingroup:: ids_peak_icv_python

@brief
Group of functions for thresholding images.


.. defgroup:: ids_peak_icv_python_transformations Transformations
.. ingroup:: ids_peak_icv_python

@brief
A collection of classes that implement
geometric transformations for image processing


.. defgroup:: ids_peak_icv_python_types Types
.. ingroup:: ids_peak_icv_python

@brief
Collection of fundamental data types used throughout the library.


.. defgroup:: ids_peak_icv_python_types_geometry Geometry
.. ingroup:: ids_peak_icv_python_types

@brief Types representing geometric concepts such as polygons and 3D points.

"""

from .backend.utils import Loader

lib_loader = Loader()

from .datatypes import (BinningFactor, Image, Region, Rotation)
from . import pipeline
from . import serialization
from .exceptions import (CorruptedException, IOException, MismatchException, NotSupportedException,
                         NotPossibleException, TargetNotFoundException, OutOfRangeException, InternalErrorException,
                         MathErrorException, NullPointerException, InvalidConfigurationException,
                         ICVException)
from . import (selectors, thresholds, calibration, transformations, filters)
from .datatypes import (PointCloud, XYZImage, Polygon, PointXYZ, PointXYZI, CoordinateSystem)
