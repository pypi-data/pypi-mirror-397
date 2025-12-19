"""Detects and extracts obfuscated, embedded content from files."""

from __future__ import annotations

from enum import Enum, auto


class EncodingEnum(Enum):
    """Type of encoding/obfuscation."""

    NONE = auto()
    XOR = auto()
    ROL = auto()
    ADD = auto()
    ROLLING_XOR = auto()
    CHARCODES = auto()
    BASE16 = auto()
    BASE64 = auto()
    DEFLATE = auto()
    REVERSE = auto()


class FormatEnum(Enum):
    """Type of format that detection is attempted for."""

    URL = auto()
    USER_AGENT = auto()
    ZIP = auto()
    OLE2 = auto()
    PE = auto()


class FormatPattern:
    """Pattern/Offset pair for a format."""

    offset: int
    pattern: bytes

    def __init__(self, offset: int, pattern: bytes):
        self.offset = offset
        self.pattern = pattern


class FormatInfo:
    """Information about how to search for a format."""

    type: FormatEnum
    # (offset, pattern_bytes)
    patterns: list[FormatPattern]
    # first bytes that are expected to already be there.
    # this is used to determine the first key in a rolling obfuscation.
    # only necessary if pattern.offset > 0.
    header: bytes

    def __init__(self, type: FormatEnum, patterns: list, header: bytes):
        self.type = type
        self.patterns = patterns
        self.header = header


class KeyedEncoding:
    """Additional information for an encoding that requires a key."""

    encoding: EncodingEnum
    key: int
    key_size: int
    increment: int
    ignore_zero: int

    def __init__(self, encoding: EncodingEnum, key: int, key_size: int, increment: int, ignore_zero: bool):
        self.encoding = encoding
        self.key = key
        self.key_size = key_size
        self.increment = increment
        self.ignore_zero = ignore_zero


class EncodingInfo:
    """Encoding information in readable form."""

    base_offset: int
    base_size: int
    encodings_string: str
    encoding_offsets_string: str
    keyed_encoding_string: str

    def __init__(self, base_offset: int, base_size: int):
        self.base_offset = base_offset
        self.base_size = base_size

        # these get filled in the call to get_encoding_info()
        self.encodings_string = ""
        self.encoding_offsets_string = ""
        self.keyed_encoding_string = ""


class FoundFormat:
    """Information about a format that has been detected in data."""

    encoding_info: EncodingInfo
    content: bytes
    type: FormatEnum
    keyed_encoding: KeyedEncoding


class EncodedSection:
    """Section of data that has been found, either plain or deobfuscated."""

    encoding: EncodingEnum
    # these are offsets within the parent section
    start_offset: int
    end_offset: int
    parent_section: EncodedSection
    child_sections: list[EncodedSection]

    # these are only used during the search, content should be cleared when done
    content: bytes
    depth: int
    grouped_sections: list[EncodedSection]

    def __init__(
        self,
        encoding: EncodingEnum,
        start_offset: int,
        end_offset: int,
        content: bytes,
        parent: EncodedSection,
        grouped_sections: list[EncodedSection],
    ):
        self.encoding = encoding
        self.start_offset = start_offset
        self.end_offset = end_offset
        self.parent_section = parent
        if parent is not None:
            parent.child_sections.append(self)
        self.child_sections = []
        self.content = content
        if parent is None:
            self.depth = 0
        else:
            self.depth = parent.depth + 1
        self.grouped_sections = grouped_sections.copy()


def try_create_section(
    encoding: EncodingEnum,
    start_offset: int,
    end_offset: int,
    content: bytes,
    parent: EncodedSection,
    grouped_sections: list[EncodedSection],
) -> EncodedSection | None:
    """Attempt to create a new EncodedSection.

    a new section will not be created if it is a duplicate due to grouping.
    """
    new_section: EncodedSection = None
    valid: bool = True

    # if this content is not contiguous, only add it if the same content has not been found contiguously
    for parent_grouped_section in parent.grouped_sections:
        if content == parent_grouped_section.content:
            valid = False
            break
    if valid:
        # this adds a reference to the new section to parent.child_sections -
        # the new section is only passed back out in case more processing needs to be done on it immediately.
        new_section = EncodedSection(encoding, start_offset, end_offset, content, parent, grouped_sections)
    return new_section


# default list of formats to search for
format_scanners: list[FormatInfo] = [
    FormatInfo(FormatEnum.URL, [FormatPattern(0, b"http://"), FormatPattern(0, b"https://")], None),
    FormatInfo(FormatEnum.USER_AGENT, [FormatPattern(0, b"Mozilla/")], None),
    FormatInfo(
        FormatEnum.ZIP, [FormatPattern(0, b"PK\x03\x04\x00\x00"), FormatPattern(0, b"PK\x03\x04\x14\x00")], None
    ),
    FormatInfo(
        FormatEnum.OLE2,
        [FormatPattern(0, b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00>")],
        None,
    ),
    FormatInfo(
        FormatEnum.PE,
        [
            FormatPattern(64, b"\x0e\x1f\xba\x0e\x00\xb4\t\xcd!\xb8\x01L\xcd!This program cannot"),
            FormatPattern(64, b"\xba\x10\x00\x0e\x1f\xb4\t\xcd!\xb8\x01L\xcd!\x90\x90This program must"),
            FormatPattern(33, b"\x0e\x1f\x00\xba\x0e\x00\xb4\t\xcd!\xb8\x00\x01L\xcd!This\x00 program\x00 "),
        ],
        b"MZ",
    ),
]


def get_encoding_info(
    section: EncodedSection, start: int, end: int, keyed_encoding: KeyedEncoding, lznt1_encoded: bool
) -> EncodingInfo:
    """Generate readable encoding info for a found obfuscation."""
    locationInfo: EncodingInfo = EncodingInfo(start, end - start)

    if keyed_encoding is not None:
        str(keyed_encoding.encoding).split(".")[-1].lower()
        key_string = keyed_encoding.key.to_bytes(keyed_encoding.key_size, "little").hex()
        key_string = "0x" + key_string

        locationInfo.keyed_encoding_string = (
            f"{str(keyed_encoding.encoding).split('.')[-1].lower()}"
            f"(key:{key_string}, bytes:{keyed_encoding.key_size}"
        )
        if keyed_encoding.increment != 0:
            locationInfo.keyed_encoding_string += f", increment:{keyed_encoding.increment}"
        if keyed_encoding.ignore_zero:
            locationInfo.keyed_encoding_string += ", ignores zero"
        locationInfo.keyed_encoding_string += ")"

        locationInfo.encodings_string = str(keyed_encoding.encoding).split(".")[-1].lower()
        locationInfo.encoding_offsets_string = f"{locationInfo.encodings_string}(0x{start:x}-0x{end:x})"
        # lznt1 decompression takes place after keyed decoding
        if lznt1_encoded:
            locationInfo.encodings_string += "->lznt1"
            locationInfo.encoding_offsets_string += f"->lznt1(0x0-0x{end - start:x})"
    elif lznt1_encoded:
        locationInfo.encodings_string = "lznt1"
        locationInfo.encoding_offsets_string += f"lznt1(0x{start:x}-0x{end:x})"
    elif (start != section.start_offset or end != section.end_offset) and len(section.grouped_sections) == 0:
        locationInfo.encoding_offsets_string += f"(0x{start:x}-0x{end:x})"

    current_section = section
    while current_section.parent_section is not None:
        encoding: str = str(current_section.encoding).split(".")[-1].lower()
        encoding_offset: str
        if current_section.encoding == EncodingEnum.REVERSE:
            encoding_offset = encoding
        elif current_section.encoding == EncodingEnum.DEFLATE:
            encoding_offset: str = f"{encoding}(0x{current_section.start_offset:x})"
        else:
            encoding_offset: str = f"{encoding}(0x{current_section.start_offset:x}-0x{current_section.end_offset:x}"
            if len(current_section.grouped_sections) > 0:
                encoding_offset += ", non-contiguous"
            encoding_offset += ")"

        if len(locationInfo.encodings_string) > 0:
            locationInfo.encodings_string = "->" + locationInfo.encodings_string
        if len(locationInfo.encoding_offsets_string) > 0:
            locationInfo.encoding_offsets_string = "->" + locationInfo.encoding_offsets_string

        locationInfo.encodings_string = encoding + locationInfo.encodings_string
        locationInfo.encoding_offsets_string = encoding_offset + locationInfo.encoding_offsets_string

        # if one lower than the base section, use the offset and size
        if current_section.parent_section.parent_section is None:
            if current_section.encoding == EncodingEnum.REVERSE:
                locationInfo.base_offset = None
                locationInfo.base_size = None
            elif current_section.encoding == EncodingEnum.DEFLATE:
                locationInfo.base_offset = current_section.start_offset
                locationInfo.base_size = None
            else:
                locationInfo.base_offset = current_section.start_offset
                locationInfo.base_size = current_section.end_offset - current_section.start_offset

        current_section = current_section.parent_section

    return locationInfo


def try_add_found_format(
    found_format_list: list[FoundFormat],
    section: EncodedSection,
    start: int,
    end: int,
    content: bytes,
    type: FormatEnum,
    keyed_encoding: KeyedEncoding,
    lznt1_encoded: bool,
):
    """Attempt to add an identified instance of a format that has been found.

    a new section will not be created if it is a duplicate due to grouping.
    """
    # for simplicity in detecting duplicate formats due to grouped content (currently hex and base64)
    # if a format with the same content has already been found, the new format is ignored.
    valid: bool = True
    if len(section.grouped_sections) > 0:
        for found_format in found_format_list:
            if content == found_format.content:
                valid = False
                break
    if valid:
        found_format = FoundFormat()
        found_format.encoding_info = get_encoding_info(section, start, end, keyed_encoding, lznt1_encoded)
        found_format.content = content
        found_format.type = type
        found_format.keyed_encoding = keyed_encoding
        found_format_list.append(found_format)
