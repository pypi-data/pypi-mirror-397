"""Find keyed encodings by calling out to corresponding C functions."""

from malcarve_cbl.find_formats import add_valid_formats
from malcarve_cbl.interop import (
    add_decrypt,
    add_find,
    rol_decrypt,
    rol_find,
    rolling_xor_decrypt,
    rolling_xor_find,
    xor_decrypt,
    xor_find,
)

from . import (
    EncodedSection,
    EncodingEnum,
    FormatEnum,
    FormatInfo,
    FormatPattern,
    FoundFormat,
    KeyedEncoding,
)


def find_rolling_xors(
    found_formats: list[FoundFormat],
    section: EncodedSection,
    pattern: FormatPattern,
    format_info: FormatInfo,
) -> list[FoundFormat]:
    """Decodes a rolling xor cipher and returns the matches.

    For the maximum number of results, the maximum number of non-overlapping instances of the pattern in the content
    is used.
    This is capped to a minimum of 10 (in case there are overlapping pattern instances found in a small buffer)
    and capped to a maximum of 1000 (so that there isn't an un-necessary amount of memory allocated for a large buffer)
    """
    offset_count_max: int = min(max(len(section.content) // len(pattern.pattern), 10), 1000)
    offsets, offset_count = rolling_xor_find(
        offset_count_max,
        offset_count_max,
        section.content,
        len(section.content),
        pattern.pattern,
        len(pattern.pattern),
        pattern.offset,
    )

    offsets_index: int = 0
    while offsets_index < offset_count:
        if pattern.offset == 0:
            first_key = pattern.pattern[0] ^ section.content[offsets[offsets_index]]
        elif format_info.header is not None:
            # try to use the format's header to determine the first key
            matching_header: bool = True
            header_index: int = 1
            while header_index < len(format_info.header):
                if (
                    section.content[offsets[offsets_index] + header_index] ^ section.content[offsets[offsets_index]]
                    != format_info.header[header_index]
                ):
                    matching_header = False
                    break
                header_index += 1
            if matching_header:
                first_key = format_info.header[0] ^ section.content[offsets[offsets_index]]
            else:
                # we can't figure out what the first byte is, so skip this one.
                # if this is an lznt1-encoded PE, we can't decode further anyway since we need that byte.
                offsets_index += 1
                continue
        else:
            # we can't figure out what the first byte is, so skip this one.
            # if this is an lznt1-encoded PE, we can't decode further anyway since we need that byte.
            offsets_index += 1
            continue

        keyed_encoding = KeyedEncoding(EncodingEnum.ROLLING_XOR, first_key, 1, 0, False)

        end: int = len(section.content)
        if (format_info.type == FormatEnum.URL or format_info.type == FormatEnum.USER_AGENT) and offsets[
            offsets_index
        ] + 512 < end:
            # only extract the next 512 bytes
            end = offsets[offsets_index] + 512
        content: bytes = rolling_xor_decrypt(
            end - offsets[offsets_index],
            section.content[offsets[offsets_index] : end],
            end - offsets[offsets_index],
            first_key,
        )
        add_valid_formats(
            found_formats, content, offsets[offsets_index], section, format_info.type, keyed_encoding, True
        )

        offsets_index += 1

    return found_formats


def find_xors(
    found_formats: list[FoundFormat], section: EncodedSection, pattern: FormatPattern, format_info: FormatInfo
):
    """Searches for xor'd content within a file section."""
    result_count_max: int = min(max(len(section.content) // len(pattern.pattern), 10), 1000)
    results, result_count = xor_find(
        result_count_max,
        result_count_max,
        section.content,
        len(section.content),
        pattern.pattern,
        len(pattern.pattern),
        pattern.offset,
    )

    results_index: int = 0
    while results_index < result_count:
        keyed_encoding = KeyedEncoding(
            EncodingEnum.XOR,
            results[results_index].starting_key,
            results[results_index].key_size,
            results[results_index].key_increment,
            results[results_index].ignore_zero,
        )

        end: int = len(section.content)
        if (format_info.type == FormatEnum.URL or format_info.type == FormatEnum.USER_AGENT) and results[
            results_index
        ].offset + 512 < end:
            # only extract the next 512 bytes
            end = results[results_index].offset + 512

        if results[results_index].starting_key == 0 and results[results_index].key_increment == 0:
            results_index += 1
            continue

        content: bytes = xor_decrypt(
            end - results[results_index].offset,
            section.content[results[results_index].offset : end],
            end - results[results_index].offset,
            results[results_index].starting_key,
            results[results_index].key_size,
            results[results_index].key_increment,
            results[results_index].ignore_zero,
        )

        add_valid_formats(
            found_formats, content, results[results_index].offset, section, format_info.type, keyed_encoding, True
        )

        results_index += 1


def find_rols(
    found_formats: list[FoundFormat],
    section: EncodedSection,
    pattern: FormatPattern,
    format_info: FormatInfo,
):
    """Search for rotated content within a PE section."""
    result_count_max: int = min(max(len(section.content) // len(pattern.pattern), 10), 1000)
    results, result_count = rol_find(
        result_count_max,
        result_count_max,
        section.content,
        len(section.content),
        pattern.pattern,
        len(pattern.pattern),
        pattern.offset,
    )

    results_index: int = 0
    while results_index < result_count:
        # reversed hex rotated by 4 un-reverses the hex, so this has already been covered.
        if (
            results[results_index].deob_key == 4
            and (section.encoding == EncodingEnum.BASE16 or section.encoding == EncodingEnum.REVERSE)
            and (
                section.parent_section.encoding == EncodingEnum.BASE16
                or section.parent_section.encoding == EncodingEnum.REVERSE
            )
        ):
            continue

        keyed_encoding = KeyedEncoding(EncodingEnum.ROL, 8 - results[results_index].deob_key, 1, 0, False)

        end: int = len(section.content)
        if (format_info.type == FormatEnum.URL or format_info.type == FormatEnum.USER_AGENT) and results[
            results_index
        ].offset + 512 < end:
            # only extract the next 512 bytes
            end = results[results_index].offset + 512
        content: bytes = rol_decrypt(
            end - results[results_index].offset,
            section.content[results[results_index].offset : end],
            end - results[results_index].offset,
            results[results_index].deob_key,
        )

        add_valid_formats(
            found_formats, content, results[results_index].offset, section, format_info.type, keyed_encoding, True
        )

        results_index += 1


def find_adds(
    found_formats: list[FoundFormat],
    section: EncodedSection,
    pattern: FormatPattern,
    format_info: FormatInfo,
):
    """Find adds."""
    result_count_max: int = min(max(len(section.content) // len(pattern.pattern), 10), 1000)
    results, result_count = add_find(
        result_count_max,
        result_count_max,
        section.content,
        len(section.content),
        pattern.pattern,
        len(pattern.pattern),
        pattern.offset,
    )

    results_index: int = 0
    while results_index < result_count:
        # don't add unencoded data
        if results[results_index].deob_key != 0:
            keyed_encoding = KeyedEncoding(EncodingEnum.ADD, 256 - results[results_index].deob_key, 1, 0, False)

            end: int = len(section.content)
            if (format_info.type == FormatEnum.URL or format_info.type == FormatEnum.USER_AGENT) and results[
                results_index
            ].offset + 512 < end:
                # only extract the next 512 bytes
                end = results[results_index].offset + 512
            content: bytes = add_decrypt(
                end - results[results_index].offset,
                section.content[results[results_index].offset : end],
                end - results[results_index].offset,
                results[results_index].deob_key,
            )

            add_valid_formats(
                found_formats, content, results[results_index].offset, section, format_info.type, keyed_encoding, True
            )

        results_index += 1
