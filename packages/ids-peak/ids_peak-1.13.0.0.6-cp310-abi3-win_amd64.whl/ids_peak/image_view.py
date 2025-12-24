from __future__ import annotations

from typing import TYPE_CHECKING, overload, Union

import ids_peak_common.datatypes.pixelformat

if TYPE_CHECKING:
    import numpy as np

from ids_peak_common.datatypes import Size, PixelFormat, IImageView, Metadata
from ids_peak.ids_peak import Buffer, BufferPart


class ImageView(IImageView):
    """
    ImageView from a Buffer or BufferPart

    Implementation of the #ids_peak_common.datatypes.IImageView interface for viewing
    image pixel data from arbitrary sources.

    This interface defines a standard way to access image properties and raw pixel data,
    enabling interoperability with different image processing libraries or backends.

    Note: This object does not own the image memory. Lifetime management must be handled externally.
    """

    @overload
    def __init__(self, buffer: Buffer): ...

    @overload
    def __init__(self, part: BufferPart): ...

    def __init__(self, arg : Union[Buffer | BufferPart]):
        """
        Initialize an ImageView.

        :raises TypeError: If the input type is unsupported.
        """
        assert arg is not None, "Buffer or BufferPart must not be None"

        from ids_peak.ids_peak import _ExtractPayloadFromBuffer, _ExtractPayloadFromBufferPart, _ExtractMetadataFromBuffer

        if isinstance(arg, Buffer):
            self._buffer = arg
            self._payload = _ExtractPayloadFromBuffer(self._buffer)
        elif isinstance(arg, BufferPart):
            self._buffer = arg.ParentBuffer()
            self._payload = _ExtractPayloadFromBufferPart(arg)
        else:
            raise TypeError(f"Unsupported input type: {type(arg)}")

        self._metadata = _ExtractMetadataFromBuffer(self._buffer)

    @property
    def pixel_format(self) -> PixelFormat:
        """
        Returns the pixel format of the image.
        """
        return self._payload.pixel_format

    @property
    def size(self) -> Size:
        """
        Returns the image dimensions as a Size object.
        """
        return self._payload.size

    @property
    def width(self) -> int:
        """
        Returns the width of the image in pixels.
        """
        return self._payload.size.width

    @property
    def height(self) -> int:
        """
        Returns the height of the image in pixels.
        """
        return self._payload.size.height

    @property
    def metadata(self) -> Metadata:
        """
        Returns the metadata object which can be used to retrieve or set metadata belonging to the image.
        """
        return self._metadata

    @property
    def parent_buffer(self) -> Buffer:
        """
        Returns the parent buffer object, the image view was created from.

        If the image was created from a buffer part, the parent buffer is the same
        as returned by BufferPart.ParentBuffer().
        """
        return self._buffer

    def to_memoryview(self) -> memoryview:
        """
        Return a zero-copy memoryview of the image data.

        The returned memoryview provides direct access to the underlying image data
        without copying data. Modifying the memoryview will modify the image data itself.
        Ensure that the image view and its underlying buffer remain valid before
        accessing or using the memoryview.
        """
        from ctypes import c_uint8, c_uint16, c_uint32, c_float
        import functools
        import weakref

        addr = int(self._payload.data_ptr)
        size = self._payload.data_size

        if self.pixel_format.numpy_dtype == "uint16":
            c_array = (c_uint16 * (size // 2)).from_address(addr)
        elif self.pixel_format.numpy_dtype == "float32":
            c_array = (c_float * (size // 4)).from_address(addr)
        elif self.pixel_format.numpy_dtype == "uint32":
            c_array = (c_uint32 * (size // 4)).from_address(addr)
        else:
            c_array = (c_uint8 * size).from_address(addr)

        memory = memoryview(c_array)
        weakref.finalize(memory, functools.partial(lambda x: None, self))
        return memory

    def to_numpy_array(self, copy=True) -> np.ndarray:
        """
        Returns the image data as a NumPy array.

        By default, the data is copied. Setting copy=False makes the array share memory with
        the internal buffer, so any changes to the array will be reflected in the image data.

        The dimensionality of the returned NumPy array varies according to the pixel format:
        * Packed formats produce a 1-dimensional array.
        * Single-channel formats (for example, Mono8) produce a 2-dimensional array with shape (height, width).
        * Multi-channel formats (for example, RGB8) produce a 3-dimensional array with shape (height, width, num_channels).

        :param copy: Whether to copy the data. Default is True.
        :return: The image data as a NumPy array.
        """
        from numpy import frombuffer

        data = frombuffer(self.to_memoryview(), dtype=self.pixel_format.numpy_dtype)

        if copy:
            data = data.copy()

        pixel_format = ids_peak_common.datatypes.pixelformat.PixelFormat(self.pixel_format)
        num_channels = len(pixel_format.channels)
        multi_channel = num_channels > 1
        is_packed = pixel_format.is_packed
        if is_packed:
            return data
        elif multi_channel:
            return data.reshape((self.height, self.width, num_channels))
        else:
            return data.reshape((self.height, self.width))
