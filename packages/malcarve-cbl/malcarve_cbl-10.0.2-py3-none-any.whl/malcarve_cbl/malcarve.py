"""Main method for malcarve to extract hidden content from files with."""

from . import EncodedSection, EncodingEnum, FoundFormat, format_scanners
from .keyed_encoding_find import (
    add_valid_formats,
    find_adds,
    find_rolling_xors,
    find_rols,
    find_xors,
)
from .unkeyed_encoding_find import (
    find_base64,
    find_charcodes,
    find_deflate_compression,
    find_hex,
    find_reverse,
)


def get_next_section(current_section: EncodedSection) -> EncodedSection:
    """Get the next section of a file to be decoded."""
    next_section: EncodedSection = None

    if len(current_section.child_sections) > 0:
        next_section = current_section.child_sections[0]
    else:
        while next_section is None:
            if current_section.parent_section is not None:
                # delete the current section from the parent
                del current_section.parent_section.child_sections[0]
                # if there is a sibling, switch to it
                if len(current_section.parent_section.child_sections) > 0:
                    next_section = current_section.parent_section.child_sections[0]
                else:
                    # we are out of siblings, switch to the parent
                    current_section = current_section.parent_section
            else:
                # we are done, just return None
                break
    return next_section


def carve_buffer(input_buffer: bytes, max_depth: int) -> list[FoundFormat]:
    """Carve out potentially interesting content and PEs from a buffer of bytes."""
    found_formats: list[FoundFormat] = []

    current_section: EncodedSection = EncodedSection(EncodingEnum.NONE, 0, len(input_buffer), input_buffer, None, [])
    while current_section is not None:
        for format in format_scanners:
            # check if the format exists in the section unencrypted
            add_valid_formats(found_formats, current_section.content, 0, current_section, format.type, None, False)
            for pattern in format.patterns:
                find_xors(found_formats, current_section, pattern, format)
                find_rolling_xors(found_formats, current_section, pattern, format)
                find_rols(found_formats, current_section, pattern, format)
                find_adds(found_formats, current_section, pattern, format)
        if current_section.depth < max_depth:
            find_charcodes(current_section)
            find_hex(current_section)
            find_base64(current_section)
            find_deflate_compression(current_section)
            find_reverse(current_section)
        current_section = get_next_section(current_section)
    return found_formats
