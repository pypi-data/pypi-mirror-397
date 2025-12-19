"""Find and validate the existence of formats from input data."""

import re
from io import BytesIO
from zipfile import BadZipFile, ZipFile

from olefile import OleFileIO

from malcarve_cbl import (
    EncodedSection,
    FormatEnum,
    FoundFormat,
    KeyedEncoding,
    try_add_found_format,
)

from .lznt1_decompress import lznt1_decompress


def validate_pe_end(buffer: bytes, start: int) -> int:
    """Validate that the buffer data is a PE, and find it's end offset."""
    end: int = -1
    dos_to_pe_offset = 0x3C
    pe_header_size_offset = 0x18
    section_count_offset = 0x6
    optional_header_size_offset = 0x14
    image_size_offset = 56

    section_raw_size_offset = 0x10
    section_raw_addr_offset = 0x14
    section_info_size = 40

    pe_offset_max = 0x200

    pe_offset: int = extract_int(buffer, start + dos_to_pe_offset, 4)
    section_count: int = extract_int(buffer, start + pe_offset + section_count_offset, 2)
    optional_header_size: int = extract_int(buffer, start + pe_offset + optional_header_size_offset, 2)

    if pe_offset <= pe_offset_max and buffer[start + pe_offset : start + pe_offset + 4] == b"PE\x00\x00":
        if section_count > 0:
            section_infos_offset: int = pe_offset + pe_header_size_offset + optional_header_size
            last_section_start: int = 0
            last_section_end: int = 0

            for section_index in range(section_count):
                section_info_offset = section_infos_offset + section_index * section_info_size
                section_size: int = extract_int(buffer, start + section_info_offset + section_raw_size_offset, 4)
                section_offset: int = extract_int(buffer, start + section_info_offset + section_raw_addr_offset, 4)

                if section_offset > last_section_start:
                    last_section_start = section_offset
                if section_offset + section_size > last_section_end:
                    last_section_end = section_offset + section_size

            if last_section_start >= section_infos_offset + section_count * section_info_size:
                if start + last_section_end <= len(buffer):
                    end = start + last_section_end
                elif start + last_section_end > len(buffer) and start + last_section_start < len(buffer):
                    # if the last section overruns the buffer, just use what there is.
                    end = len(buffer)
        else:
            # just use the image size if there are no sections
            image_size: int = extract_int(buffer, pe_offset + pe_header_size_offset + image_size_offset, 4)
            if start + image_size <= len(buffer):
                end = start + image_size
            else:
                end = len(buffer)
            pass
    return end


def extract_int(buffer: bytes, offset: int, byte_count: int) -> int:
    """Extract unsigned int from byte buffer."""
    extracted_int: int = -1
    if offset + byte_count < len(buffer):
        extracted_int = int.from_bytes(buffer[offset : offset + byte_count], "little")
    return extracted_int


class RegexPatterns:
    """Compiled regex patterns for each format type."""

    url: re.Pattern = re.compile(
        rb"((ftp|http)s?://[a-z\-0-9]{1,256}\.[a-z\-0-9]{1,256}([a-z\-0-9\_./:\%\?\#\=\+\~])*)", re.I
    )
    user_agent: re.Pattern = re.compile(rb"(Mozilla/\d([ A-Za-z\-0-9\_./:\%\?\#\=\+\~\(\);,]){2,256})")
    zip: re.Pattern = re.compile(b"PK")
    ole: re.Pattern = re.compile(b"\xd0\xcf\x11\xe0")
    pe: re.Pattern = re.compile(b"MZ")


def add_valid_formats(
    valid_formats: list[FoundFormat],
    buffer: bytes,
    offset_to_buffer: int,
    section: EncodedSection,
    format_type: FormatEnum,
    encoding: KeyedEncoding,
    single_result: bool,
):
    """Checks to validate the existence of a format and add it to the list."""
    if format_type == FormatEnum.URL:
        # at least 2 domains deep and optionally any valid chars after (including ports).. no checking for user:pass
        # PE certificate urls will often run into ascii numbers
        fixers = (
            b".cer0",
            b".com0",
            b".com1",
            b".com/0",
            b".crl0",
            b".crt0",
            b".htm0",
            b".html0",
            b"/ca10",
            b"/CPS0",
            b"/cps0",
            b"/DPM0",
            b"/policy/0",
            b"/repository0",
            b"/rpa0",
            b"/ts0",
            # happens with add encoding list of urls (comma gets translated)
            b"+",
        )
        for match in RegexPatterns.url.finditer(buffer):
            if single_result and match.start() != 0:
                break
            url: bytes = match.group(0)
            # strip the last character from the end if it matches one of the above patterns.
            if url.endswith(fixers):
                try_add_found_format(
                    valid_formats,
                    section,
                    offset_to_buffer + match.start(),
                    offset_to_buffer + match.end() - 1,
                    buffer[match.start() : match.end() - 1],
                    format_type,
                    encoding,
                    False,
                )
            elif url[:-1].endswith(fixers):
                try_add_found_format(
                    valid_formats,
                    section,
                    offset_to_buffer + match.start(),
                    offset_to_buffer + match.end() - 2,
                    buffer[match.start() : match.end() - 2],
                    format_type,
                    encoding,
                    False,
                )
                if single_result:
                    break
            else:
                try_add_found_format(
                    valid_formats,
                    section,
                    offset_to_buffer + match.start(),
                    offset_to_buffer + match.end(),
                    buffer[match.start() : match.end()],
                    format_type,
                    encoding,
                    False,
                )
                if single_result:
                    break
    elif format_type == FormatEnum.USER_AGENT:
        for match in RegexPatterns.user_agent.finditer(buffer):
            if single_result and match.start() != 0:
                break
            try_add_found_format(
                valid_formats,
                section,
                offset_to_buffer + match.start(),
                offset_to_buffer + match.end(),
                buffer[match.start() : match.end()],
                format_type,
                encoding,
                False,
            )
            if single_result:
                break
    elif format_type == FormatEnum.ZIP:
        # keep track of last end of directory index, to avoid adding subsets of matches
        last_eocd_index: int = 0

        # ensure starts with magic
        for match in RegexPatterns.zip.finditer(buffer):
            if single_result and match.start() != 0:
                break
            try:
                potential_zip = ZipFile(BytesIO(buffer[match.start() :]))
                # Raises ValueError if the zip file is missing header information
                # (especially useful when running over a zip file).
                potential_zip.testzip()
            except BadZipFile:  # Zip fails to be created ZipFile initalisation fails.
                continue
            except ValueError:  # Zip fails testzip
                continue
            try:
                end_of_central_directory_index: int = buffer.index(b"\x50\x4b\x05\x06\x00\x00\x00\x00")
            except ValueError:
                continue

            if end_of_central_directory_index > last_eocd_index:
                if single_result or section.depth > 0 or match.start() > 0:
                    try_add_found_format(
                        valid_formats,
                        section,
                        offset_to_buffer + match.start(),
                        offset_to_buffer + end_of_central_directory_index + 22,
                        buffer[match.start() : end_of_central_directory_index + 22],
                        format_type,
                        encoding,
                        False,
                    )
                    last_eocd_index = end_of_central_directory_index
    elif format_type == FormatEnum.OLE2:
        for match in RegexPatterns.ole.finditer(buffer):
            # Don't get an ole2 file from the start of a file because if it's a valid OLE2 we already have it.
            if match.start() == 0:
                if single_result:
                    break
                continue
            try:
                with OleFileIO(buffer[match.start() :]) as ole:
                    # +1 because nb_sect is the number of sectors minus the header sector.
                    ole_end = min((ole.nb_sect + 1) * ole.sector_size, len(buffer))
            except Exception:  # noqa: S112  # nosec: B112
                continue

            # sometimes seems to include/exclude header
            if single_result or section.depth > 0 or match.start() > 0 or ole_end < len(buffer):
                try_add_found_format(
                    valid_formats,
                    section,
                    offset_to_buffer + match.start(),
                    offset_to_buffer + ole_end,
                    buffer[match.start() : ole_end],
                    format_type,
                    encoding,
                    False,
                )
                if single_result:
                    break
    elif format_type == FormatEnum.PE:
        for match in RegexPatterns.pe.finditer(buffer):
            if single_result and not (match.start() == 0 or match.start() == 3):
                break
            # Note - this will sometimes drop null bytes off th end of a valid PE which is a good thing.
            # This is because it typically happens when the PE has been extracted from somewhere else and
            #   has extra data appended.
            # With that data removed it is more likely to find a correlation with an existing binary.
            pe_end: int = validate_pe_end(buffer, match.start())
            if pe_end >= 0:
                if single_result or section.depth > 0 or match.start() > 0 or pe_end < len(buffer):
                    try_add_found_format(
                        valid_formats,
                        section,
                        offset_to_buffer + match.start(),
                        offset_to_buffer + pe_end,
                        buffer[match.start() : pe_end],
                        format_type,
                        encoding,
                        False,
                    )
                    if single_result:
                        break
            # if this wasn't a valid PE, check if it is LZNT1 compressed
            elif match.start() >= 3:
                encoded_size, lznt1_decoded = lznt1_decompress(buffer[match.start() - 3 :])
                pe_end: int = validate_pe_end(lznt1_decoded, 0)
                if pe_end >= 0:
                    try_add_found_format(
                        valid_formats,
                        section,
                        offset_to_buffer + match.start() - 3,
                        offset_to_buffer + match.start() - 3 + encoded_size,
                        lznt1_decoded,
                        format_type,
                        encoding,
                        True,
                    )

                    if single_result:
                        break
