"""Decompress potential LZNT1 compression."""


def as_uint(b: bytes, index: int, count: int) -> int:
    """Convert input bytes into a little endian uint."""
    return int.from_bytes(b[index : index + count], "little")


def as_bytes(b: bytes, index: int, count: int) -> int:
    """Take a slice of the provided bytes."""
    return b[index : index + count]


def lznt1_decompress(comp_buffer: bytes) -> tuple[int, bytes]:
    """Attempts to decode using the LZNT1 spec.

    LZNT1 SPEC FOUND AT https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-xca
    Returns compressed size and decompressed buffer.
    """
    buffer_cursor = 0
    decomp_buffer: bytes = b""

    while buffer_cursor < len(comp_buffer):
        decomp_chunk_size: int = 0
        chunk_header: int = as_uint(comp_buffer, buffer_cursor, 2)
        if chunk_header == 0:
            # END OF BUFFER
            if buffer_cursor > 0:
                buffer_cursor += 2
            break
        if (chunk_header >> 12) & 7 != 3:
            # INVALID CHUNK - invalid header, spec says header bits 14-12 are always == 3
            break
        # chunk size (including header) in bits 11-0
        chunk_size = (chunk_header & 0xFFF) + 3
        if buffer_cursor + chunk_size > len(comp_buffer):
            # INVALID CHUNK - the chunk will overrun the buffer.
            break
        # bit 15 is a flag for whether the chunk is compressed
        if chunk_header & 0x8000 != 0:
            # COMPRESSED CHUNK
            chunk_cursor: int = 2
            chunk_error = False
            while chunk_cursor < chunk_size and not chunk_error:
                flags_byte: int = as_uint(comp_buffer, buffer_cursor + chunk_cursor, 1)
                chunk_cursor += 1
                for flag_index in range(0, 8):
                    if chunk_cursor == chunk_size:
                        # we have processed the whole chunk, move on to the next one
                        break
                    if flags_byte & (1 << flag_index) != 0:
                        # NEXT 2 BYTES ARE DISPLACEMENT/LENGTH
                        if chunk_cursor + 2 > chunk_size:
                            # INVALID CHUNK - will overread the chunk
                            chunk_error = True
                            break
                        # get displacement/length bit split (according to formula in spec)
                        displacement_bytes: int = 4
                        for m in range(11, 2, -1):
                            if 1 << m < decomp_chunk_size:
                                displacement_bytes = m + 1
                                break
                        displacement_length = as_uint(comp_buffer, buffer_cursor + chunk_cursor, 2)
                        displacement: int = (
                            (displacement_length >> 16 - displacement_bytes) & (0xFFFF >> 16 - displacement_bytes)
                        ) + 1
                        length: int = (displacement_length & (0xFFFF >> displacement_bytes)) + 3

                        if displacement > decomp_chunk_size:
                            # INVALID CHUNK - will underread the chunk
                            chunk_error = True
                            break

                        # while length > displacement, just keep looping over the bytes
                        decomp_chunk_size += length
                        while length > 0:
                            read_length: int = length
                            if read_length > displacement:
                                read_length = displacement
                            decomp_buffer += as_bytes(decomp_buffer, len(decomp_buffer) - displacement, read_length)
                            length -= read_length
                        chunk_cursor += 2
                    else:
                        # NEXT BYTE IS UNCOMPRESSED
                        decomp_buffer += as_bytes(comp_buffer, buffer_cursor + chunk_cursor, 1)
                        decomp_chunk_size += 1
                        chunk_cursor += 1
            if chunk_error:
                # INVALID CHUNK - error in chunk decompression
                decomp_buffer = decomp_buffer[: len(decomp_buffer) - decomp_chunk_size]
                break
        else:
            # UNCOMPRESSED CHUNK
            decomp_buffer += as_bytes(comp_buffer, buffer_cursor + 2, chunk_size - 2)
        buffer_cursor += chunk_size
    return buffer_cursor, decomp_buffer
