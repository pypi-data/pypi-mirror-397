import io
import os
import struct
import unittest
import zipfile
import zlib
from base64 import b64encode
from binascii import hexlify
from io import BytesIO

from azul_bedrock.test_utils import file_manager

from malcarve_cbl import (
    EncodedSection,
    EncodingEnum,
    EncodingInfo,
    FormatEnum,
    FoundFormat,
)
from malcarve_cbl.find_formats import add_valid_formats
from malcarve_cbl.interop import (
    BasicCrypt,
    ComplexCrypt,
    add_find,
    rol_find,
    rolling_xor_find,
    xor_decrypt,
    xor_find,
)
from malcarve_cbl.malcarve import carve_buffer
from malcarve_cbl.unkeyed_encoding_find import (
    find_base64,
    find_charcodes,
    find_deflate_compression,
    find_hex,
    find_reverse,
)


def rolling_xor_encode(input: bytes, start_index: int, length: int, key: int) -> bytes:
    output: bytes = input[0:start_index]

    output += bytes([input[start_index] ^ key])

    input_index: int = start_index + 1
    while input_index < length:
        key = output[len(output) - 1]
        key += 1 << 8
        key %= 1 << 8
        output += bytes([input[input_index] ^ key])
        input_index += 1
    if start_index + length < len(input):
        output += input[start_index + length :]
    return output


def xor_encode(input: bytes, key: int, key_size: int, ignore_zero: bool, key_increment: int) -> bytes:
    output: bytes = b""

    input_index: int = 0
    while input_index < len(input):
        if ignore_zero and input[input_index : input_index + key_size] == b"\0" * key_size:
            output += b"\0" * key_size
            input_index += key_size
            continue
        if key_size > len(input) - input_index:
            key_size = len(input) - input_index
        output += (
            int.from_bytes(input[input_index : input_index + key_size], "little") ^ (key & (1 << key_size * 8) - 1)
        ).to_bytes(key_size, "little")
        key += key_increment
        key %= 1 << (key_size * 8)
        input_index += key_size
    return output


def add_encode(input: bytes, key: int) -> bytes:
    output: bytes = b""

    input_index: int = 0
    while input_index < len(input):
        output += bytes([(input[input_index] + key) % 256])
        input_index += 1
    return output


def rol(byte: int, rotate_bits: int) -> int:
    return (byte << rotate_bits % 8) & 255 | (byte >> (8 - rotate_bits % 8))


def rol_encode(input: bytes, key: int) -> bytes:
    output: bytes = b""

    input_index: int = 0
    while input_index < len(input):
        output += bytes([rol(input[input_index], key)])
        input_index += 1
    return output


def to_charcodes(input: bytes) -> bytes:
    output: bytes = b""
    for byte in input:
        output += str(byte).encode() + b" "
    # strip final space
    return output[:-1]


def assert_class_attrs_equal(test: unittest.TestCase, a: object, b: object):
    for attr_name in dir(a):
        attr = getattr(a, attr_name)
        attr_type = type(attr).__name__
        if not (attr_name.startswith("_") or callable(attr)):
            test.assertTrue(attr_name in dir(b))
            if (isinstance(__builtins__, dict) and attr_type in list(__builtins__)) or attr_type in dir(__builtins__):
                test.assertEqual(attr, getattr(b, attr_name))
            else:
                assert_class_attrs_equal(test, attr, getattr(b, attr_name))


class TestKeyedFind(unittest.TestCase):
    def test_xor_1_unobfuscated(self):
        input: bytes = b"abcdefg"
        results, result_count = xor_find(2, 2, input, len(input), input, len(input), 0)
        self.assertEqual(result_count, 1)

        assert_class_attrs_equal(
            self, results[0], ComplexCrypt(key_size=1, ignore_zero=False, offset=0, starting_key=0, key_increment=0)
        )

    def test_xor_1_simple(self):
        input: bytes = b"abcdefg"
        encoded: bytes = xor_encode(input, 13, 1, False, 0)
        results, result_count = xor_find(2, 2, encoded, len(encoded), input, len(input), 0)
        self.assertEqual(result_count, 1)

        assert_class_attrs_equal(
            self, results[0], ComplexCrypt(key_size=1, ignore_zero=False, offset=0, starting_key=13, key_increment=0)
        )

    def test_xor_1_overlapping(self):
        pattern: bytes = b"abcdef"
        input: bytes = b"abcabcdef"
        encoded: bytes = xor_encode(input, 101, 1, False, 0)
        results, result_count = xor_find(2, 2, encoded, len(encoded), pattern, len(pattern), 0)
        self.assertEqual(result_count, 1)

        assert_class_attrs_equal(
            self, results[0], ComplexCrypt(key_size=1, ignore_zero=False, offset=3, starting_key=101, key_increment=0)
        )

    def test_xor_1_ignore_zero(self):
        input: bytes = b"abc\0defghij\0\0\0klm"
        encoded: bytes = xor_encode(input, 13, 1, True, 0)
        results, result_count = xor_find(2, 2, encoded, len(encoded), input, len(input), 0)
        self.assertEqual(result_count, 1)

        assert_class_attrs_equal(
            self, results[0], ComplexCrypt(key_size=1, ignore_zero=True, offset=0, starting_key=13, key_increment=0)
        )

        found_encoded: bytes = encoded[results[0].offset :]
        found_decoded = xor_decrypt(
            len(found_encoded),
            found_encoded,
            len(found_encoded),
            results[0].starting_key,
            results[0].key_size,
            results[0].key_increment,
            results[0].ignore_zero,
        )
        self.assertEqual(found_decoded, input)

    def test_xor_3_simple(self):
        input: bytes = b"abcdefghijklm"
        encoded: bytes = xor_encode(input, 13, 3, False, 0)
        results, result_count = xor_find(2, 2, encoded, len(encoded), input, len(input), 0)
        self.assertEqual(result_count, 1)

        assert_class_attrs_equal(
            self, results[0], ComplexCrypt(key_size=3, ignore_zero=False, offset=0, starting_key=13, key_increment=0)
        )

    def test_pattern_too_short(self):
        pattern: bytes = b"abcdefghijklmnopqrstuvwxyz"
        input: bytes = b"this is offset - " + pattern + b" - this is the rest"
        unimportant_bytes = b"this is not important - "

        key = 1000000000000
        pattern_offset = 17

        encoded: bytes = unimportant_bytes + xor_encode(input, key, 8, False, 0)
        results, result_count = xor_find(2, 2, encoded, len(encoded), pattern, len(pattern), pattern_offset)
        self.assertEqual(result_count, 0)

    def test_xor_8_increment(self):
        pattern: bytes = b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        input: bytes = b"this is offset - " + pattern + b" - this is the rest"
        unimportant_bytes = b"this is not important - "

        key = 0
        increment = 5678901234567890123
        pattern_offset = 17

        encoded: bytes = unimportant_bytes + xor_encode(input, key, 8, False, increment)
        results, result_count = xor_find(2, 2, encoded, len(encoded), pattern, len(pattern), pattern_offset)
        self.assertEqual(result_count, 1)

        assert_class_attrs_equal(
            self,
            results[0],
            ComplexCrypt(
                key_size=8, ignore_zero=False, offset=len(unimportant_bytes), starting_key=key, key_increment=increment
            ),
        )

        found_encoded: bytes = encoded[results[0].offset :]
        found_decoded = xor_decrypt(
            len(found_encoded),
            found_encoded,
            len(found_encoded),
            results[0].starting_key,
            results[0].key_size,
            results[0].key_increment,
            results[0].ignore_zero,
        )
        self.assertEqual(found_decoded, input)

    def test_xor_1_incrementing_more_results_than_max(self):
        pattern: bytes = b"abcdef"
        input: bytes = b"abcdefabcdefabcdef"
        encoded: bytes = xor_encode(input, 101, 1, False, 5)
        results, result_count = xor_find(2, 2, encoded, len(encoded), pattern, len(pattern), 0)
        self.assertEqual(result_count, 2)

        assert_class_attrs_equal(
            self, results[0], ComplexCrypt(key_size=1, ignore_zero=False, offset=0, starting_key=101, key_increment=5)
        )
        assert_class_attrs_equal(
            self, results[1], ComplexCrypt(key_size=1, ignore_zero=False, offset=6, starting_key=131, key_increment=5)
        )

    def test_xor_3_increment_zero_ignore_offset(self):
        pattern: bytes = b"abcd\0\0\0efghij\0\0\0klm"
        input: bytes = b"this is offset - " + pattern + b" - this is the rest"
        unimportant_bytes = b"this is not important - "

        key = 27
        increment = 111
        pattern_offset = 17

        encoded: bytes = unimportant_bytes + xor_encode(input, key, 3, True, increment)
        results, result_count = xor_find(2, 2, encoded, len(encoded), pattern, len(pattern), pattern_offset)
        self.assertEqual(result_count, 1)

        assert_class_attrs_equal(
            self,
            results[0],
            ComplexCrypt(
                key_size=3, ignore_zero=True, offset=len(unimportant_bytes), starting_key=key, key_increment=increment
            ),
        )

        found_encoded: bytes = encoded[results[0].offset :]
        found_decoded = xor_decrypt(
            len(found_encoded),
            found_encoded,
            len(found_encoded),
            results[0].starting_key,
            results[0].key_size,
            results[0].key_increment,
            results[0].ignore_zero,
        )
        self.assertEqual(found_decoded, input)

    def test_rolling_xor_find(self):
        pattern: bytes = b"abcabcdefdef"
        # since this has repeated substrings of the pattern, we are also checking that no skipping occurs
        input: bytes = b"abcdefabcabcdefdefdef"
        encoded: bytes = rolling_xor_encode(input, 0, len(input), 51)
        results, result_count = rolling_xor_find(2, 2, encoded, len(encoded), pattern, len(pattern), 0)
        self.assertEqual(result_count, 1)
        self.assertEqual(results[0], 6)

    def test_add_find(self):
        pattern: bytes = b"abcabcdefdef"
        input: bytes = b"abcabcabcdefdefdef"
        # if we encode it with -241, we would expect the deob key to be 241
        encoded: bytes = add_encode(input, -241)
        results, result_count = add_find(2, 2, encoded, len(encoded), pattern, len(pattern), 0)
        self.assertEqual(result_count, 1)

        assert_class_attrs_equal(
            self,
            results[0],
            BasicCrypt(
                deob_key=241,
                offset=3,
            ),
        )

    def test_rol_find(self):
        pattern: bytes = b"abcabcdefdef"
        input: bytes = b"abcabcabcdefdefdef"
        # if we encode it with 3, we would expect the deob key to be 5
        encoded: bytes = rol_encode(input, 3)
        results, result_count = rol_find(2, 2, encoded, len(encoded), pattern, len(pattern), 0)
        self.assertEqual(result_count, 1)

        assert_class_attrs_equal(
            self,
            results[0],
            BasicCrypt(
                deob_key=5,
                offset=3,
            ),
        )


class TestUnkeyedFind(unittest.TestCase):
    def test_charcode_find(self):
        expected_output: bytes = b"these are charcodes\xff\xf0\x00"
        charcodes: bytes = to_charcodes(expected_output)
        section: EncodedSection = EncodedSection(EncodingEnum.NONE, 0, len(charcodes), charcodes, None, [])
        find_charcodes(section)
        self.assertEqual(len(section.child_sections), 1)
        assert_class_attrs_equal(
            self,
            section.child_sections[0],
            EncodedSection(
                encoding=EncodingEnum.CHARCODES,
                start_offset=0,
                end_offset=len(charcodes),
                content=expected_output,
                parent=section,
                grouped_sections=[],
            ),
        )

    def test_hex_find(self):
        expected_output: bytes = b"here is some hex\xff\xf0\x00"

        hex: bytes = hexlify(expected_output)
        section: EncodedSection = EncodedSection(EncodingEnum.NONE, 0, len(hex), hex, None, [])
        find_hex(section)
        self.assertEqual(len(section.child_sections), 1)
        assert_class_attrs_equal(
            self,
            section.child_sections[0],
            EncodedSection(
                encoding=EncodingEnum.BASE16,
                start_offset=0,
                end_offset=len(hex),
                content=expected_output,
                parent=section,
                grouped_sections=[],
            ),
        )

        # mixed casing
        hex = hex[:-4] + hex[-4:].upper()
        section = EncodedSection(EncodingEnum.NONE, 0, len(hex), hex, None, [])
        find_hex(section)
        self.assertEqual(len(section.child_sections), 1)
        assert_class_attrs_equal(
            self,
            section.child_sections[0],
            EncodedSection(
                encoding=EncodingEnum.BASE16,
                start_offset=0,
                end_offset=len(hex),
                content=expected_output,
                parent=section,
                grouped_sections=[],
            ),
        )

        # not aligned by 2 - will find both possibilities
        hex = b"A" + hex
        section = EncodedSection(EncodingEnum.NONE, 0, len(hex), hex, None, [])
        find_hex(section)
        self.assertEqual(len(section.child_sections), 2)
        assert_class_attrs_equal(
            self,
            section.child_sections[0],
            EncodedSection(
                encoding=EncodingEnum.BASE16,
                start_offset=0,
                end_offset=len(hex) - 1,
                content=b"\xa6\x86W&R\x06\x972\x076\xf6\xd6R\x06\x86W\x8f\xff\x00",
                parent=section,
                grouped_sections=[],
            ),
        )
        assert_class_attrs_equal(
            self,
            section.child_sections[1],
            EncodedSection(
                encoding=EncodingEnum.BASE16,
                start_offset=1,
                end_offset=len(hex),
                content=expected_output,
                parent=section,
                grouped_sections=[],
            ),
        )

    def test_base_64_find(self):
        expected_output: bytes = b"here is some base64\xff\x00"

        base64: bytes = b64encode(expected_output)
        section: EncodedSection = EncodedSection(EncodingEnum.NONE, 0, len(base64), base64, None, [])
        find_base64(section)
        # finds the 4 possible alignments
        self.assertEqual(len(section.child_sections), 4)
        assert_class_attrs_equal(
            self,
            section.child_sections[0],
            EncodedSection(
                encoding=EncodingEnum.BASE64,
                start_offset=0,
                end_offset=len(base64),
                content=expected_output,
                parent=section,
                grouped_sections=[],
            ),
        )

        base64 = b"a" + base64
        section: EncodedSection = EncodedSection(EncodingEnum.NONE, 0, len(base64), base64, None, [])
        find_base64(section)
        self.assertEqual(len(section.child_sections), 4)
        self.assertTrue(expected_output in section.child_sections[1].content)

        base64 = b"a" + base64
        section: EncodedSection = EncodedSection(EncodingEnum.NONE, 0, len(base64), base64, None, [])
        find_base64(section)
        self.assertEqual(len(section.child_sections), 4)
        self.assertTrue(expected_output in section.child_sections[2].content)

        base64 = b"a" + base64
        section: EncodedSection = EncodedSection(EncodingEnum.NONE, 0, len(base64), base64, None, [])
        find_base64(section)
        self.assertEqual(len(section.child_sections), 4)
        self.assertTrue(expected_output in section.child_sections[3].content)

    def test_deflate_find(self):
        expected_output: bytes = b"here is some deflate-compressed content" * 100
        deflated: bytes = b"abc" + zlib.compress(expected_output)

        section: EncodedSection = EncodedSection(EncodingEnum.NONE, 0, len(deflated), deflated, None, [])
        find_deflate_compression(section)

        self.assertEqual(len(section.child_sections), 1)
        assert_class_attrs_equal(
            self,
            section.child_sections[0],
            EncodedSection(
                encoding=EncodingEnum.DEFLATE,
                start_offset=3,
                # we currently can't calculate an end offset for deflate
                end_offset=-1,
                content=expected_output,
                parent=section,
                grouped_sections=[],
            ),
        )

    def test_reverse_find(self):
        expected_output: bytes = b"reversed"
        section: EncodedSection = EncodedSection(
            EncodingEnum.NONE, 0, len(expected_output), expected_output[::-1], None, []
        )
        find_reverse(section)
        self.assertEqual(len(section.child_sections), 1)
        assert_class_attrs_equal(
            self,
            section.child_sections[0],
            EncodedSection(
                encoding=EncodingEnum.REVERSE,
                start_offset=0,
                end_offset=-1,
                content=expected_output,
                parent=section,
                grouped_sections=[],
            ),
        )


class TestGrouping(unittest.TestCase):
    def test_grouped_section_hex(self):
        non_contiguous_hex: bytes = hexlify(b"https") + b"\0" * 20 + hexlify(b"://test.com")
        formats = carve_buffer(non_contiguous_hex, 1)
        self.assertEqual(formats[0].encoding_info.encoding_offsets_string, "base16(0x1e-0x34, non-contiguous)")
        self.assertEqual(formats[0].content, b"https://test.com")

    def test_grouped_section_base_64(self):
        non_contiguous_b64: bytes = b64encode(b"https://test.com/base/64/grouping")
        non_contiguous_b64 = non_contiguous_b64[0:18] + b"\0" * 20 + non_contiguous_b64[18:]
        formats = carve_buffer(non_contiguous_b64, 1)
        self.assertEqual(formats[0].encoding_info.encoding_offsets_string, "base64(0x0-0x40, non-contiguous)")
        self.assertEqual(formats[0].content, b"https://test.com/base/64/grouping")

    def test_dont_extract_from_zip(self):
        """Don't extract a bad zip file (one with no header) from a zip file."""
        fm = file_manager.FileManager()
        # Benign Zip archive that's missing parts of its header.
        raw_data = fm.download_file_bytes("b5b170ca412115c9512f733de7ed51fdd64bf7f8fb6c8369a1cf735a8b061ed7")
        formats = carve_buffer(raw_data, 4)
        self.assertEqual(formats, [])


class TestFormatFind(unittest.TestCase):
    def test_find_string(self):
        url: bytes = b"https://url.com"
        user_agent: bytes = b"Mozilla/9000 useragent"
        input = url + b"\0" + user_agent + b"\0"

        found_url: FoundFormat = FoundFormat()
        found_url.encoding_info = EncodingInfo(0, len(url))
        found_url.encoding_info.encoding_offsets_string = "(0x0-0xf)"
        found_url.content = url
        found_url.type = FormatEnum.URL
        found_url.keyed_encoding = None

        found_user_agent: FoundFormat = FoundFormat()
        found_user_agent.encoding_info = EncodingInfo(len(url) + 1, len(user_agent))
        found_user_agent.encoding_info.encoding_offsets_string = "(0x10-0x26)"
        found_user_agent.content = user_agent
        found_user_agent.type = FormatEnum.USER_AGENT
        found_user_agent.keyed_encoding = None

        formats: list[FoundFormat] = []
        section: EncodedSection = EncodedSection(EncodingEnum.NONE, 0, len(input), input, None, [])

        add_valid_formats(formats, input, 0, section, FormatEnum.URL, None, False)
        self.assertEqual(len(formats), 1)
        assert_class_attrs_equal(self, formats[0], found_url)

        add_valid_formats(formats, input, 0, section, FormatEnum.USER_AGENT, None, False)
        self.assertEqual(len(formats), 2)
        assert_class_attrs_equal(self, formats[1], found_user_agent)

    def test_find_zip(self):
        zipped_bytes_io = BytesIO()
        with zipfile.ZipFile(zipped_bytes_io, "w", zipfile.ZIP_DEFLATED) as zip:
            zip.writestr("file", b"this is test data that will get zipped.")
        input: bytes = b"padding" + zipped_bytes_io.getvalue() + b"padding"

        found_zip: FoundFormat = FoundFormat()
        found_zip.encoding_info = EncodingInfo(7, len(zipped_bytes_io.getvalue()))
        found_zip.encoding_info.encoding_offsets_string = "(0x7-0x98)"
        found_zip.content = zipped_bytes_io.getvalue()
        found_zip.type = FormatEnum.ZIP
        found_zip.keyed_encoding = None

        formats: list[FoundFormat] = []
        section: EncodedSection = EncodedSection(EncodingEnum.NONE, 0, len(input), input, None, [])

        add_valid_formats(formats, input, 0, section, FormatEnum.ZIP, None, False)
        self.assertEqual(len(formats), 1)
        assert_class_attrs_equal(self, formats[0], found_zip)

    def test_find_ole2_msi(self):
        """Load a MSI Ole2 file and extract nothing because it's already an MSI."""
        fm = file_manager.FileManager()
        # Benign OLE2 MSI.
        raw_data = fm.download_file_bytes("9c4893b9c6b8dd78d0e43e0365ae8d9e7bc90f599e2993f7a55fa300eb691bb2")
        formats = carve_buffer(raw_data, 4)
        self.assertEqual(formats, [])
