"""
.. defgroup:: ids_peak_icv_python_pipeline_features Pipeline Features
.. ingroup:: ids_peak_icv_python_pipeline

\brief
  High-level user interfaces for configuring and controlling pipeline processing stages.

Pipeline features provide intuitive, user-friendly interfaces for configuring the various
image processing operations in the pipeline. Each feature corresponds to one or more
underlying modules and abstracts away the low-level implementation details.

## Feature Categories

### Geometric Features
- **BinningFeature**: Combines adjacent pixels to reduce resolution and improve SNR
- **DecimationFeature**: Reduces resolution by skipping pixels in a pattern
- **MirrorFeature**: Flips images horizontally and/or vertically
- **RotationFeature**: Rotates images in 90-degree increments

### Color and Brightness Features
- **GainFeature**: Controls overall brightness and individual color channel gains
- **ColorCorrectionFeature**: Applies color correction matrices for color space conversion
- **SaturationFeature**: Adjusts color saturation levels
- **GammaFeature**: Applies gamma correction for brightness and contrast adjustment
- **DigitalBlackFeature**: Compensates for sensor digital black offsets

### Enhancement Features
- **SharpeningFeature**: Enhances image detail and perceived sharpness
- **HotpixelCorrectionFeature**: Removes defective pixels from sensor data


.. defgroup:: ids_peak_icv_python_pipeline_modules Pipeline Modules
.. ingroup:: ids_peak_icv_python_pipeline

@brief
  Core processing modules that perform specific image transformation operations.

Pipeline modules are the fundamental building blocks of the image processing pipeline.
Each module encapsulates a specific image processing algorithm and can be configured
independently. Modules are typically not accessed directly by users; instead, they
are controlled through the higher-level Feature interfaces.

## Module Categories

### Format Conversion Modules
- **UnpackModule**: Converts packed sensor data to standard formats
- **DebayerModule**: Converts Bayer pattern data to RGB
- **MonoConversionModule**: Converts color images to monochrome
- **PixelFormatConversionModule**: Final format conversion and bit depth adjustment

### Enhancement Modules
- **GainModule**: Applies digital gain for brightness and white balance
- **SharpeningModule**: Enhances image detail using edge-based filters
- **ToneCurveCorrectionModule**: Applies gamma correction and tone mapping
- **ColorMatrixTransformationModule**: Performs color space transformations

### Geometric Transformation Modules
- **TransformationModule**: Handles rotation and mirroring operations
- **DownsamplingModule**: Performs binning and decimation operations

### Correction Modules
- **HotpixelCorrectionModule**: Identifies and corrects defective pixels

@note
  Modules are typically accessed through Feature interfaces
  rather than directly.
  Direct module access is primarily for advanced use cases
  and internal pipeline logic.


.. defgroup:: ids_peak_icv_python_pipeline_types Special Pipeline Types
.. ingroup:: ids_peak_icv_python_pipeline

@brief
  Supporting data structures, enumerations, and type definitions for pipeline configuration.

This group contains the specialized types used throughout the pipeline system
for configuration, control, and data representation.
These types provide type-safe interfaces for pipeline parameters
and ensure consistent behavior across the system.
"""

from .default_pipeline import DefaultPipeline
from .processing_policy import ProcessingPolicy
from . import features
