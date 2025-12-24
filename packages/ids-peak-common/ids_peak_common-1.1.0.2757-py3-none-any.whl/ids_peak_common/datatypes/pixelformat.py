from __future__ import annotations

from enum import Enum
from typing import Tuple, Union, NamedTuple, cast

from ids_peak_common._internal.constants import FLOAT32_MAX, FLOAT32_MIN
from ids_peak_common.datatypes.geometry.size import Size
from ids_peak_common.exceptions import NotSupportedException


class Channel(Enum):
    """
    Channels

    .. ingroup:: ids_peak_common_python_types
    """

    INTENSITY = 0,
    """
    Luminance or grayscale intensity channel. Common in single-channel images.
    """

    RED = 1,
    """
    Red color channel. May appear in various layouts (e.g., RGB, ARGB).
    """

    GREEN = 2,
    """
    Green color channel. Commonly part of multichannel color formats.
    """

    BLUE = 3,
    """
    Blue color channel. Present in formats like BGR, RGBA, etc.
    """

    ALPHA = 4,
    """
    Alpha (opacity or transparency) channel. Often used for blending and masking.
    """

    X = 5,
    """
    Represents the X coordinate channel (e.g., in point clouds).
    """

    Y = 6,
    """
    Represents the Y coordinate channel (e.g., in point clouds).
    """

    Z = 7,
    """
    Represents the Z coordinate channel (e.g., in point clouds).
    """

    BAYER = 8,
    """
    Raw Bayer pattern data from image sensors (e.g., BGGR, RGGB).
    """

    CHROMA_U = 9,
    """
    Chrominance U channel (Cb). Represents the blue-difference chroma component in YUV/YCbCr color spaces.
    """

    CHROMA_V = 10
    """
    Chrominance V channel (Cr). Represents the red-difference chroma component in YUV/YCbCr color spaces.
    """


class _PixelFormatMetadata(NamedTuple):
    string_value: str
    channels: tuple[Channel, ...]
    storage_bits_per_channel: int
    allocated_bits_per_pixel: int
    numpy_dtype: str
    is_packed: bool
    unpacked_format: PixelFormat


class PixelFormat(Enum):
    """
    Enum listing all supported pixel formats and their internal IDs.

    Each enumerator represents a specific pixel layout and bit depth,
    used for interpreting raw image data correctly.

    This class also offers methods to query characteristics of specific
    pixel formats, such as value ranges, storage sizes, and channel configurations.

    .. ingroup:: ids_peak_common_python_types
    """

    BAYER_GR_8 = 0x01080008
    BAYER_GR_10 = 0x0110000C
    BAYER_GR_12 = 0x01100010

    BAYER_RG_8 = 0x01080009
    BAYER_RG_10 = 0x0110000D
    BAYER_RG_12 = 0x01100011

    BAYER_GB_8 = 0x0108000A
    BAYER_GB_10 = 0x0110000E
    BAYER_GB_12 = 0x01100012

    BAYER_BG_8 = 0x0108000B
    BAYER_BG_10 = 0x0110000F
    BAYER_BG_12 = 0x01100013

    MONO_8 = 0x01080001
    MONO_10 = 0x01100003
    MONO_12 = 0x01100005
    MONO_16 = 0x01100007

    CONFIDENCE_8 = 0x010800C6
    CONFIDENCE_16 = 0x011000C7

    COORD3D_C8 = 0x010800B1
    COORD3D_C16 = 0x011000B8
    COORD3D_C32F = 0x012000BF

    COORD3D_ABC32F = 0x026000C0

    YUV420_8_YY_UV_SEMIPLANAR_IDS = 0x420C0001
    YUV420_8_YY_VU_SEMIPLANAR_IDS = 0x420C0002

    YUV422_8_UYVY = 0x0210001F

    RGB_8 = 0x02180014
    RGB_10 = 0x02300018
    RGB_12 = 0x0230001A

    BGR_8 = 0x02180015
    BGR_10 = 0x02300019
    BGR_12 = 0x0230001B

    RGBA_8 = 0x02200016
    RGBA_10 = 0x0240005F
    RGBA_12 = 0x02400061

    BGRA_8 = 0x02200017
    BGRA_10 = 0x0240004C
    BGRA_12 = 0x0240004E

    BAYER_BG_10_PACKED = 0x010A0052
    BAYER_BG_12_PACKED = 0x010C0053

    BAYER_GB_10_PACKED = 0x010A0054
    BAYER_GB_12_PACKED = 0x010C0055

    BAYER_GR_10_PACKED = 0x010A0056
    BAYER_GR_12_PACKED = 0x010C0057

    BAYER_RG_10_PACKED = 0x010A0058
    BAYER_RG_12_PACKED = 0x010C0059

    MONO_10_PACKED = 0x010A0046
    MONO_12_PACKED = 0x010C0047

    RGB_10_PACKED_32 = 0x0220001D
    BGR_10_PACKED_32 = 0x0220001E

    BAYER_RG_10_GROUPED_40_IDS = 0x40000001
    BAYER_GB_10_GROUPED_40_IDS = 0x40000002
    BAYER_GR_10_GROUPED_40_IDS = 0x40000003
    BAYER_BG_10_GROUPED_40_IDS = 0x40000004

    BAYER_RG_12_GROUPED_24_IDS = 0x40000011
    BAYER_GB_12_GROUPED_24_IDS = 0x40000012
    BAYER_GR_12_GROUPED_24_IDS = 0x40000013
    BAYER_BG_12_GROUPED_24_IDS = 0x40000014

    MONO_10_GROUPED_40_IDS = 0x4000000f
    MONO_12_GROUPED_24_IDS = 0x4000001f

    @staticmethod
    def create_from_string_value(string_value: str) -> PixelFormat:
        for pixelformat in _pixel_format_metadata:
            if pixelformat.string_value == string_value:
                return pixelformat

        raise NotSupportedException(f"The given pixelformat is not supported. Given: {string_value}")

    def __str__(self) -> str:
        """
        Return a human-readable string of the PixelFormat object.
        """
        return self.name

    def __repr__(self) -> str:
        """
        Return an unambiguous string of the PixelFormat object.
        """
        return f"PixelFormat.{self.name}(value={hex(self._value_)}, string_value={self.string_value!r})"

    @property
    def minimum_value_per_channel(self) -> Union[int, float]:
        """
        Returns the minimum possible value per channel for the pixel format.
        """
        if not self.is_float:
            return 0
        else:
            return FLOAT32_MIN

    @property
    def maximum_value_per_channel(self) -> Union[int, float]:
        """
        Returns the maximum possible value per channel for the pixel format.
        """
        if not self.is_float:
            return int(2 ** self.storage_bits_per_channel - 1)
        else:
            return FLOAT32_MAX

    @property
    def storage_bits_per_channel(self) -> int:
        """
        Returns the number of bits used per channel for storage.
        """
        return self._metadata.storage_bits_per_channel

    @property
    def storage_bits_per_pixel(self) -> int:
        """
        Returns the total number of bits used per pixel for storage.
        """
        return self._metadata.storage_bits_per_channel * self.number_of_channels

    @property
    def string_value(self) -> str:
        """
        Returns the human-readable name of the pixel format.
        """
        return self._metadata.string_value

    @property
    def channels(self) -> Tuple[Channel, ...]:
        """
        Returns the list of channels in the pixel format.
        """
        return self._metadata.channels

    @property
    def allocated_bits_per_pixel(self) -> int:
        """
        Returns the number of allocated bits per pixel.
        """
        return self._metadata.allocated_bits_per_pixel

    @property
    def numpy_dtype(self) -> str:
        """
        Returns the numpy dtype string for this pixel format.
        """
        return self._metadata.numpy_dtype

    @property
    def has_intensity_channel(self) -> bool:
        """
        Returns True if the pixel format has an intensity channel.
        """
        return Channel.INTENSITY in self.channels

    @property
    def number_of_channels(self) -> int:
        """
        Returns the total number of channels in the pixel format.
        """
        return len(self.channels)

    @property
    def is_single_channel(self) -> bool:
        """
        Returns True if the pixel format has only a single channel.
        """
        return len(self.channels) == 1

    @property
    def is_packed(self) -> bool:
        """
        Returns True if the pixel format is packed.
        """
        return self._metadata.is_packed

    @property
    def unpacked_format(self) -> PixelFormat:
        """
        Returns the unpacked pixel format for a packed pixel format.
        If the pixel format is already unpacked,
        the same format is returned.
        """
        return self._metadata.unpacked_format

    def get_channel_index(self, channel: Channel) -> int:
        """
        Returns the index of a specific channel within the pixel format.
        """
        return self.channels.index(channel)

    def has_channel(self, channel: Channel) -> bool:
        """
        Returns True if the pixel format has a specific channel.
        """
        return channel in self.channels

    def get_size_in_bytes(self, size: Size) -> int:
        """
        Calculates the memory size in bytes for a given image size.
        """
        area = size.width * size.height
        return int((area * self.allocated_bits_per_pixel + 7) // 8)

    @property
    def _metadata(self) -> _PixelFormatMetadata:
        return cast(_PixelFormatMetadata, _pixel_format_metadata.get(self))

    @property
    def is_float(self) -> bool:
        return self._metadata.numpy_dtype == "float32"


_pixel_format_metadata = {
    PixelFormat.BAYER_GR_8: _PixelFormatMetadata(
        string_value="BayerGR8",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=8,
        allocated_bits_per_pixel=8,
        numpy_dtype="uint8",
        is_packed=False,
        unpacked_format=PixelFormat.BAYER_GR_8
    ),

    PixelFormat.BAYER_GR_10: _PixelFormatMetadata(
        string_value="BayerGR10",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=16,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.BAYER_GR_10
    ),

    PixelFormat.BAYER_GR_12: _PixelFormatMetadata(
        string_value="BayerGR12",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=12,
        allocated_bits_per_pixel=16,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.BAYER_GR_12
    ),

    PixelFormat.BAYER_RG_8: _PixelFormatMetadata(
        string_value="BayerRG8",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=8,
        allocated_bits_per_pixel=8,
        numpy_dtype="uint8",
        is_packed=False,
        unpacked_format=PixelFormat.BAYER_RG_8
    ),

    PixelFormat.BAYER_RG_10: _PixelFormatMetadata(
        string_value="BayerRG10",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=16,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.BAYER_RG_10
    ),

    PixelFormat.BAYER_RG_12: _PixelFormatMetadata(
        string_value="BayerRG12",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=12,
        allocated_bits_per_pixel=16,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.BAYER_RG_12
    ),

    PixelFormat.BAYER_GB_8: _PixelFormatMetadata(
        string_value="BayerGB8",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=8,
        allocated_bits_per_pixel=8,
        numpy_dtype="uint8",
        is_packed=False,
        unpacked_format=PixelFormat.BAYER_GB_8
    ),

    PixelFormat.BAYER_GB_10: _PixelFormatMetadata(
        string_value="BayerGB10",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=16,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.BAYER_GB_10
    ),

    PixelFormat.BAYER_GB_12: _PixelFormatMetadata(
        string_value="BayerGB12",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=12,
        allocated_bits_per_pixel=16,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.BAYER_GB_12
    ),

    PixelFormat.BAYER_BG_8: _PixelFormatMetadata(
        string_value="BayerBG8",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=8,
        allocated_bits_per_pixel=8,
        numpy_dtype="uint8",
        is_packed=False,
        unpacked_format=PixelFormat.BAYER_BG_8
    ),

    PixelFormat.BAYER_BG_10: _PixelFormatMetadata(
        string_value="BayerBG10",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=16,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.BAYER_BG_10
    ),

    PixelFormat.BAYER_BG_12: _PixelFormatMetadata(
        string_value="BayerBG12",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=12,
        allocated_bits_per_pixel=16,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.BAYER_BG_12
    ),

    PixelFormat.MONO_8: _PixelFormatMetadata(
        string_value="Mono8",
        channels=(Channel.INTENSITY,),
        storage_bits_per_channel=8,
        allocated_bits_per_pixel=8,
        numpy_dtype="uint8",
        is_packed=False,
        unpacked_format=PixelFormat.MONO_8
    ),

    PixelFormat.MONO_10: _PixelFormatMetadata(
        string_value="Mono10",
        channels=(Channel.INTENSITY,),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=16,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.MONO_10
    ),

    PixelFormat.MONO_12: _PixelFormatMetadata(
        string_value="Mono12",
        channels=(Channel.INTENSITY,),
        storage_bits_per_channel=12,
        allocated_bits_per_pixel=16,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.MONO_12
    ),

    PixelFormat.MONO_16: _PixelFormatMetadata(
        string_value="Mono16",
        channels=(Channel.INTENSITY,),
        storage_bits_per_channel=16,
        allocated_bits_per_pixel=16,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.MONO_16
    ),

    PixelFormat.CONFIDENCE_8: _PixelFormatMetadata(
        string_value="Confidence8",
        channels=(Channel.INTENSITY,),
        storage_bits_per_channel=8,
        allocated_bits_per_pixel=8,
        numpy_dtype="uint8",
        is_packed=False,
        unpacked_format=PixelFormat.CONFIDENCE_8
    ),

    PixelFormat.CONFIDENCE_16: _PixelFormatMetadata(
        string_value="Confidence16",
        channels=(Channel.INTENSITY,),
        storage_bits_per_channel=16,
        allocated_bits_per_pixel=16,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.CONFIDENCE_16
    ),

    PixelFormat.COORD3D_C8: _PixelFormatMetadata(
        string_value="Coord3D_C8",
        channels=(Channel.INTENSITY,),
        storage_bits_per_channel=8,
        allocated_bits_per_pixel=8,
        numpy_dtype="uint8",
        is_packed=False,
        unpacked_format=PixelFormat.COORD3D_C8
    ),

    PixelFormat.COORD3D_C16: _PixelFormatMetadata(
        string_value="Coord3D_C16",
        channels=(Channel.INTENSITY,),
        storage_bits_per_channel=16,
        allocated_bits_per_pixel=16,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.COORD3D_C16
    ),

    PixelFormat.COORD3D_C32F: _PixelFormatMetadata(
        string_value="Coord3D_C32f",
        channels=(Channel.INTENSITY,),
        storage_bits_per_channel=32,
        allocated_bits_per_pixel=32,
        numpy_dtype="float32",
        is_packed=False,
        unpacked_format=PixelFormat.COORD3D_C32F
    ),

    PixelFormat.COORD3D_ABC32F: _PixelFormatMetadata(
        string_value="Coord3D_ABC32f",
        channels=(Channel.X, Channel.Y, Channel.Z),
        storage_bits_per_channel=32,
        allocated_bits_per_pixel=96,
        numpy_dtype="float32",
        is_packed=False,
        unpacked_format=PixelFormat.COORD3D_ABC32F
    ),

    PixelFormat.YUV420_8_YY_UV_SEMIPLANAR_IDS: _PixelFormatMetadata(
        string_value="YUV420_8_YY_UV_SemiplanarIDS",
        channels=(Channel.INTENSITY, Channel.CHROMA_U, Channel.CHROMA_V),
        storage_bits_per_channel=8,
        allocated_bits_per_pixel=12,
        numpy_dtype="uint8",
        is_packed=False,
        unpacked_format=PixelFormat.YUV420_8_YY_UV_SEMIPLANAR_IDS
    ),

    PixelFormat.YUV420_8_YY_VU_SEMIPLANAR_IDS: _PixelFormatMetadata(
        string_value="YUV420_8_YY_VU_SemiplanarIDS",
        channels=(Channel.INTENSITY, Channel.CHROMA_V, Channel.CHROMA_U),
        storage_bits_per_channel=8,
        allocated_bits_per_pixel=12,
        numpy_dtype="uint8",
        is_packed=False,
        unpacked_format=PixelFormat.YUV420_8_YY_VU_SEMIPLANAR_IDS
    ),

    PixelFormat.YUV422_8_UYVY: _PixelFormatMetadata(
        string_value="YUV422_8_UYVY",
        channels=(Channel.INTENSITY, Channel.CHROMA_U, Channel.CHROMA_V),
        storage_bits_per_channel=8,
        allocated_bits_per_pixel=16,
        numpy_dtype="uint8",
        is_packed=False,
        unpacked_format=PixelFormat.YUV422_8_UYVY
    ),

    PixelFormat.RGB_8: _PixelFormatMetadata(
        string_value="RGB8",
        channels=(Channel.RED, Channel.GREEN, Channel.BLUE),
        storage_bits_per_channel=8,
        allocated_bits_per_pixel=24,
        numpy_dtype="uint8",
        is_packed=False,
        unpacked_format=PixelFormat.RGB_8
    ),

    PixelFormat.RGB_10: _PixelFormatMetadata(
        string_value="RGB10",
        channels=(Channel.RED, Channel.GREEN, Channel.BLUE),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=48,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.RGB_10
    ),

    PixelFormat.RGB_12: _PixelFormatMetadata(
        string_value="RGB12",
        channels=(Channel.RED, Channel.GREEN, Channel.BLUE),
        storage_bits_per_channel=12,
        allocated_bits_per_pixel=48,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.RGB_12
    ),

    PixelFormat.BGR_8: _PixelFormatMetadata(
        string_value="BGR8",
        channels=(Channel.BLUE, Channel.GREEN, Channel.RED),
        storage_bits_per_channel=8,
        allocated_bits_per_pixel=24,
        numpy_dtype="uint8",
        is_packed=False,
        unpacked_format=PixelFormat.BGR_8
    ),

    PixelFormat.BGR_10: _PixelFormatMetadata(
        string_value="BGR10",
        channels=(Channel.BLUE, Channel.GREEN, Channel.RED),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=48,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.BGR_10
    ),

    PixelFormat.BGR_12: _PixelFormatMetadata(
        string_value="BGR12",
        channels=(Channel.BLUE, Channel.GREEN, Channel.RED),
        storage_bits_per_channel=12,
        allocated_bits_per_pixel=48,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.BGR_12
    ),

    PixelFormat.RGBA_8: _PixelFormatMetadata(
        string_value="RGBa8",
        channels=(Channel.RED, Channel.GREEN, Channel.BLUE, Channel.ALPHA),
        storage_bits_per_channel=8,
        allocated_bits_per_pixel=32,
        numpy_dtype="uint8",
        is_packed=False,
        unpacked_format=PixelFormat.RGBA_8
    ),

    PixelFormat.RGBA_10: _PixelFormatMetadata(
        string_value="RGBa10",
        channels=(Channel.RED, Channel.GREEN, Channel.BLUE, Channel.ALPHA),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=64,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.RGBA_10
    ),

    PixelFormat.RGBA_12: _PixelFormatMetadata(
        string_value="RGBa12",
        channels=(Channel.RED, Channel.GREEN, Channel.BLUE, Channel.ALPHA),
        storage_bits_per_channel=12,
        allocated_bits_per_pixel=64,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.RGBA_12
    ),

    PixelFormat.BGRA_8: _PixelFormatMetadata(
        string_value="BGRa8",
        channels=(Channel.BLUE, Channel.GREEN, Channel.RED, Channel.ALPHA),
        storage_bits_per_channel=8,
        allocated_bits_per_pixel=32,
        numpy_dtype="uint8",
        is_packed=False,
        unpacked_format=PixelFormat.BGRA_8
    ),

    PixelFormat.BGRA_10: _PixelFormatMetadata(
        string_value="BGRa10",
        channels=(Channel.BLUE, Channel.GREEN, Channel.RED, Channel.ALPHA),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=64,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.BGRA_10
    ),

    PixelFormat.BGRA_12: _PixelFormatMetadata(
        string_value="BGRa12",
        channels=(Channel.BLUE, Channel.GREEN, Channel.RED, Channel.ALPHA),
        storage_bits_per_channel=12,
        allocated_bits_per_pixel=64,
        numpy_dtype="uint16",
        is_packed=False,
        unpacked_format=PixelFormat.BGRA_12
    ),

    PixelFormat.BAYER_BG_10_PACKED: _PixelFormatMetadata(
        string_value="BayerBG10p",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=10,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.BAYER_BG_10
    ),

    PixelFormat.BAYER_BG_12_PACKED: _PixelFormatMetadata(
        string_value="BayerBG12p",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=12,
        allocated_bits_per_pixel=12,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.BAYER_BG_12
    ),

    PixelFormat.BAYER_GB_10_PACKED: _PixelFormatMetadata(
        string_value="BayerGB10p",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=10,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.BAYER_GB_10
    ),

    PixelFormat.BAYER_GB_12_PACKED: _PixelFormatMetadata(
        string_value="BayerGB12p",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=12,
        allocated_bits_per_pixel=12,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.BAYER_GB_12
    ),

    PixelFormat.BAYER_GR_10_PACKED: _PixelFormatMetadata(
        string_value="BayerGR10p",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=10,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.BAYER_GR_10
    ),

    PixelFormat.BAYER_GR_12_PACKED: _PixelFormatMetadata(
        string_value="BayerGR12p",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=12,
        allocated_bits_per_pixel=12,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.BAYER_GR_12
    ),

    PixelFormat.BAYER_RG_10_PACKED: _PixelFormatMetadata(
        string_value="BayerRG10p",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=10,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.BAYER_RG_10
    ),

    PixelFormat.BAYER_RG_12_PACKED: _PixelFormatMetadata(
        string_value="BayerRG12p",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=12,
        allocated_bits_per_pixel=12,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.BAYER_RG_12
    ),

    PixelFormat.MONO_10_PACKED: _PixelFormatMetadata(
        string_value="Mono10p",
        channels=(Channel.INTENSITY,),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=10,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.MONO_10
    ),

    PixelFormat.MONO_12_PACKED: _PixelFormatMetadata(
        string_value="Mono12p",
        channels=(Channel.INTENSITY,),
        storage_bits_per_channel=12,
        allocated_bits_per_pixel=12,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.MONO_12
    ),

    PixelFormat.RGB_10_PACKED_32: _PixelFormatMetadata(
        string_value="RGB10p32",
        channels=(Channel.RED, Channel.GREEN, Channel.BLUE),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=32,
        numpy_dtype="uint32",
        is_packed=True,
        unpacked_format=PixelFormat.RGB_10
    ),

    PixelFormat.BGR_10_PACKED_32: _PixelFormatMetadata(
        string_value="BGR10p32",
        channels=(Channel.BLUE, Channel.GREEN, Channel.RED),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=32,
        numpy_dtype="uint32",
        is_packed=True,
        unpacked_format=PixelFormat.BGR_10
    ),

    PixelFormat.BAYER_RG_10_GROUPED_40_IDS: _PixelFormatMetadata(
        string_value="BayerRG10g40IDS",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=10,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.BAYER_RG_10
    ),

    PixelFormat.BAYER_GB_10_GROUPED_40_IDS: _PixelFormatMetadata(
        string_value="BayerGB10g40IDS",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=10,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.BAYER_GB_10
    ),

    PixelFormat.BAYER_GR_10_GROUPED_40_IDS: _PixelFormatMetadata(
        string_value="BayerGR10g40IDS",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=10,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.BAYER_GR_10
    ),

    PixelFormat.BAYER_BG_10_GROUPED_40_IDS: _PixelFormatMetadata(
        string_value="BayerBG10g40IDS",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=10,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.BAYER_BG_10
    ),

    PixelFormat.BAYER_RG_12_GROUPED_24_IDS: _PixelFormatMetadata(
        string_value="BayerRG12g24IDS",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=12,
        allocated_bits_per_pixel=12,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.BAYER_RG_12
    ),

    PixelFormat.BAYER_GB_12_GROUPED_24_IDS: _PixelFormatMetadata(
        string_value="BayerGB12g24IDS",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=12,
        allocated_bits_per_pixel=12,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.BAYER_GB_12
    ),

    PixelFormat.BAYER_GR_12_GROUPED_24_IDS: _PixelFormatMetadata(
        string_value="BayerGR12g24IDS",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=12,
        allocated_bits_per_pixel=12,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.BAYER_GR_12
    ),

    PixelFormat.BAYER_BG_12_GROUPED_24_IDS: _PixelFormatMetadata(
        string_value="BayerBG12g24IDS",
        channels=(Channel.BAYER,),
        storage_bits_per_channel=12,
        allocated_bits_per_pixel=12,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.BAYER_BG_12
    ),

    PixelFormat.MONO_10_GROUPED_40_IDS: _PixelFormatMetadata(
        string_value="Mono10g40IDS",
        channels=(Channel.INTENSITY,),
        storage_bits_per_channel=10,
        allocated_bits_per_pixel=10,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.MONO_10
    ),

    PixelFormat.MONO_12_GROUPED_24_IDS: _PixelFormatMetadata(
        string_value="Mono12g24IDS",
        channels=(Channel.INTENSITY,),
        storage_bits_per_channel=12,
        allocated_bits_per_pixel=12,
        numpy_dtype="uint16",
        is_packed=True,
        unpacked_format=PixelFormat.MONO_12
    )
}
