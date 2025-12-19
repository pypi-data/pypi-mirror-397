"""Methods to help find various kinds of encodings within a files bytes."""

import re
import zlib
from binascii import unhexlify

from malcarve_cbl import EncodedSection, EncodingEnum, try_create_section

# base16 and base64 check for obfuscated content
# that have been separated by less than this amount of bytes
max_join_gap: int = 50


# do all of the regex compiles once only.
class RegexPatterns:
    """Compiled Regex for finding encodings."""

    # looking for sequence of codes 1-3 digits, maybe wrapped in Chr().
    # Chr() is a visual basic standard library function.
    charcode_all: re.Pattern = re.compile(
        rb"(Chr\()?\d{1,3}\)?(\s{,5}[\s\-\,\&\|O\%\^\.\;]\s{,5}(Chr\()?\d{1,3}\)?){9,}"
    )
    charcode_code: re.Pattern = re.compile(rb"(\d{1,3})")
    hex: re.Pattern = re.compile(rb"([a-fA-F0-9]{1,}[\,\^\%]?\s*){10,}")
    whitespace: re.Pattern = re.compile(rb"\s+")
    base64: re.Pattern = re.compile(rb"[a-zA-Z0-9+/]{16,}={0,2}")
    # 0x4889 - 4K Window size common in PDF Deflate Filter
    # 0x7801 - 32K Window Low Compression
    # 0x789C - 32K Window Default Compression
    # 0x78DA - 32K Window Best Compression
    # this is probably not exhaustive and there aren't really fixed bytes
    deflate: re.Pattern = re.compile(
        rb"((\x48\x89)|(\x78\x01)|(\x78\x9c)|(\x78\xda)|(\xec\xfd)|(\xed\x7c)"
        rb"|(\xe4\x5c)|(\x7c\x92)|(\x9c\x53)|(\x8c\x8f)|(\xec\x9d)|(\xec\x59)"
        rb"|(\xc4\x54)|(\xc4\x53)|(\x84\xd0)|(\x9d\x54)|(\xcc\x58)|(\xac\x95)"
        rb"|(\x8c\x92)|(\xc4\x96))"
    )


def different_bytes(buffer: bytes) -> bool:
    """Check that the stream isn't just all the same byte."""
    has_different_byte: bool = False
    for byte in buffer:
        if byte != buffer[0]:
            has_different_byte = True
            break
    return has_different_byte


def find_charcodes(parent_section: EncodedSection):
    """Find charcodes in section."""
    for regex_match in re.finditer(RegexPatterns.charcode_all, parent_section.content):
        match_content: bytes = b""
        for digit_group in re.finditer(RegexPatterns.charcode_code, regex_match.group(0)):
            extracted_code: int = int(digit_group.group(1))
            if extracted_code <= 0xFF:
                match_content += extracted_code.to_bytes(1, "little")
            else:
                break
        if different_bytes(match_content):
            try_create_section(
                EncodingEnum.CHARCODES, regex_match.start(), regex_match.end(), match_content, parent_section, []
            )


def find_hex(parent_section: EncodedSection):
    """Find base16 in section."""
    grouped_hex: bytes = b""
    grouped_count: int = 0
    grouped_sections: list[EncodedSection] = []
    last_end_offset: int = 0

    for regex_match in re.finditer(RegexPatterns.hex, parent_section.content):
        # if this content is not going to be added to the grouping,
        # create new sections from the grouping and clear it.
        if regex_match.start() > last_end_offset + max_join_gap:
            if grouped_count > 1:
                if len(grouped_hex) % 2 != 0:
                    unhexed: bytes = unhexlify(grouped_hex[:-1])
                    if different_bytes(unhexed):
                        try_create_section(
                            EncodingEnum.BASE16,
                            regex_match.start(),
                            regex_match.end() - 1,
                            unhexed,
                            parent_section,
                            grouped_sections,
                        )
                    unhexed: bytes = unhexlify(grouped_hex[1:])
                    if different_bytes(unhexed):
                        try_create_section(
                            EncodingEnum.BASE16,
                            regex_match.start() + 1,
                            regex_match.end(),
                            unhexed,
                            parent_section,
                            grouped_sections,
                        )
                else:
                    unhexed: bytes = unhexlify(grouped_hex)
                    if different_bytes(unhexed):
                        try_create_section(
                            EncodingEnum.BASE16,
                            regex_match.start(),
                            regex_match.end(),
                            unhexed,
                            parent_section,
                            grouped_sections,
                        )
            grouped_hex = b""
            grouped_count = 0
            grouped_sections.clear()

        match = regex_match.group(0).lower()

        # remove any symbol characters
        match = match.replace(b",", b"")
        match = match.replace(b"%", b"")
        match = match.replace(b"^", b"")

        # remove whitespace
        match = re.sub(RegexPatterns.whitespace, b"", match)

        # if the number of hex characters is odd try dropping both the first and the last characters.
        if len(match) % 2 != 0:
            unhexed: bytes = unhexlify(match[:-1])
            if different_bytes(unhexed):
                new_section: EncodedSection = try_create_section(
                    EncodingEnum.BASE16, regex_match.start(), regex_match.end() - 1, unhexed, parent_section, []
                )
                if new_section is not None:
                    grouped_sections.append(new_section)

            unhexed: bytes = unhexlify(match[1:])
            if different_bytes(unhexed):
                new_section: EncodedSection = try_create_section(
                    EncodingEnum.BASE16, regex_match.start() + 1, regex_match.end(), unhexed, parent_section, []
                )
                if new_section is not None:
                    grouped_sections.append(new_section)
        else:
            unhexed: bytes = unhexlify(match)
            if different_bytes(unhexed):
                new_section: EncodedSection = try_create_section(
                    EncodingEnum.BASE16, regex_match.start(), regex_match.end(), unhexed, parent_section, []
                )
                if new_section is not None:
                    grouped_sections.append(new_section)

        grouped_hex += match
        grouped_count += 1
        last_end_offset = regex_match.end()

    # if there is unadded grouped content, add it.
    if grouped_count > 1:
        if len(grouped_hex) % 2 != 0:
            unhexed: bytes = unhexlify(grouped_hex[:-1])
            if different_bytes(unhexed):
                try_create_section(
                    EncodingEnum.BASE16,
                    regex_match.start(),
                    regex_match.end() - 1,
                    unhexed,
                    parent_section,
                    grouped_sections,
                )
            unhexed: bytes = unhexlify(grouped_hex[1:])
            if different_bytes(unhexed):
                try_create_section(
                    EncodingEnum.BASE16,
                    regex_match.start() + 1,
                    regex_match.end(),
                    unhexed,
                    parent_section,
                    grouped_sections,
                )
        else:
            unhexed: bytes = unhexlify(grouped_hex)
            if different_bytes(unhexed):
                try_create_section(
                    EncodingEnum.BASE16,
                    regex_match.start(),
                    regex_match.end(),
                    unhexed,
                    parent_section,
                    grouped_sections,
                )


def get_base64_char_codes(base64: bytes) -> list[int]:
    """Return list of base64 character codes as integers."""
    codes: list[int] = []
    for char in base64:
        if char >= ord("A") and char <= ord("Z"):
            codes.append(char - ord("A"))
        elif char >= ord("a") and char <= ord("z"):
            codes.append(char - ord("a") + 26)
        elif char >= ord("0") and char <= ord("9"):
            codes.append(char - ord("0") + 52)
        elif char == ord("+"):
            codes.append(62)
        elif char == ord("/"):
            codes.append(63)
        else:
            # currently ignoring chars that aren't base64 -
            # since we are putting it through regex first, this should never occur.
            pass
    return codes


def get_base64_possibilities(content: bytes) -> list[bytes]:
    """Get the 4 base64 decode possibilities for the input data."""
    codes: list[int] = get_base64_char_codes(content)
    decodes: list[list[int]] = [[], [0], [0], [0]]

    index: int = 0
    while index < len(codes):
        decodes[(index + 0) % 4].append((codes[index] << 2) % 256)
        decodes[(index + 1) % 4][-1] |= codes[index]
        decodes[(index + 2) % 4][-1] |= codes[index] >> 2
        decodes[(index + 2) % 4].append((codes[index] << 6) % 256)
        decodes[(index + 3) % 4][-1] |= codes[index] >> 4
        decodes[(index + 3) % 4].append((codes[index] << 4) % 256)

        index += 1

    decode_bytes: list[bytes] = []
    for int_list in decodes:
        decode_bytes.append(bytes(int_list))

    return decode_bytes


def find_base64(parent_section: EncodedSection):
    """Find base64 in section."""
    new_sections: list[EncodedSection] = []

    grouped_base64: bytes = b""
    grouped_count: int = 0
    grouped_sections: list[EncodedSection] = []
    group_first_offset: int = 0
    last_end_offset: int = 0

    for regex_match in re.finditer(RegexPatterns.base64, parent_section.content):
        # check for uppercase chars
        upper_exists: bool = False
        lower_exists: bool = False
        # to lower false positive rate, check there is at least an upper and lower case character in the encoding.
        for char in regex_match.group(0):
            if char >= 65 and char <= 90:
                upper_exists = True
            if char >= 97 and char <= 122:
                lower_exists = True
            if upper_exists and lower_exists:
                break

        if upper_exists and lower_exists:
            # if this content is not going to be added to the grouping,
            # create new sections from the grouping and clear it.
            if regex_match.start() > last_end_offset + max_join_gap or grouped_base64.endswith(b"="):
                if grouped_count > 1:
                    grouped_base64_decodes: list[bytes] = get_base64_possibilities(grouped_base64.strip(b"="))
                    for base64_decoded in grouped_base64_decodes:
                        if different_bytes(base64_decoded):
                            try_create_section(
                                EncodingEnum.BASE64,
                                group_first_offset,
                                regex_match.end(),
                                base64_decoded,
                                parent_section,
                                grouped_sections,
                            )
                grouped_base64 = b""
                grouped_count = 0
                grouped_sections.clear()
                group_first_offset = regex_match.start()

            base64_content = re.sub(RegexPatterns.whitespace, b"", regex_match.group(0))

            base64_decodes: list[bytes] = get_base64_possibilities(base64_content.strip(b"="))
            for base64_decoded in base64_decodes:
                if different_bytes(base64_decoded):
                    new_section: EncodedSection = try_create_section(
                        EncodingEnum.BASE64,
                        regex_match.start(),
                        regex_match.end(),
                        base64_decoded,
                        parent_section,
                        [],
                    )
                    if new_section is not None:
                        grouped_sections.append(new_section)

            grouped_base64 += base64_content
            grouped_count += 1
            last_end_offset = regex_match.end()

    # if there is unadded grouped content, add it.
    if grouped_count > 1:
        grouped_base64_decodes: list[bytes] = get_base64_possibilities(grouped_base64.strip(b"="))
        for base64_decoded in grouped_base64_decodes:
            if different_bytes(base64_decoded):
                try_create_section(
                    EncodingEnum.BASE64,
                    group_first_offset,
                    last_end_offset,
                    base64_decoded,
                    parent_section,
                    grouped_sections,
                )

    return new_sections


def find_deflate_compression(parent_section: EncodedSection):
    """Find deflate compression in section."""
    for regex_match in re.finditer(RegexPatterns.deflate, parent_section.content):
        try:
            # try with zlib header, 0 = auto detect wbits
            found_content = zlib.decompress(parent_section.content[regex_match.start() :], 0)
            if different_bytes(found_content):
                try_create_section(EncodingEnum.DEFLATE, regex_match.start(), -1, found_content, parent_section, [])
        except zlib.error:
            try:
                # try without zlib header 'raw'
                found_content: bytes = zlib.decompress(parent_section.content[regex_match.start() :], -15)
                if different_bytes(found_content):
                    try_create_section(
                        EncodingEnum.DEFLATE, regex_match.start(), -1, found_content, parent_section, []
                    )
            except zlib.error:
                pass


def find_reverse(parent_section: EncodedSection):
    """Reverse section and add as new section."""
    # don't perform multiple reverse operations
    reversed: bool = False
    check_section: EncodedSection = parent_section
    while check_section is not None:
        if check_section.encoding == EncodingEnum.REVERSE:
            reversed = True
            break
        else:
            check_section = check_section.parent_section
    if not reversed:
        try_create_section(EncodingEnum.REVERSE, 0, -1, parent_section.content[::-1], parent_section, [])
