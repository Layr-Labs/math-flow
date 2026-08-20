#!/usr/bin/env python3
"""Minimal, deterministic text extraction for the pinned GLN source PDF.

This is intentionally not a general PDF implementation.  It parses the exact
pdfTeX structures used by the committed source: the two Appendix B page
content streams, their resource dictionaries, and the referenced one-byte
ToUnicode CMaps.  Every structural assertion fails closed.
"""

from __future__ import annotations

import re
import zlib
from dataclasses import dataclass


PAGE_BINDINGS = (
    (14, 29, 30, 108),
    (15, 31, 32, 109),
)
OBJECT_STREAM_NUMBER = 53


@dataclass(frozen=True)
class ExtractedPage:
    number: int
    text: str


def _direct_object(pdf: bytes, number: int) -> bytes:
    marker = f"{number} 0 obj".encode("ascii")
    starts = [match.start() for match in re.finditer(re.escape(marker), pdf)]
    if len(starts) != 1:
        raise AssertionError(f"expected one direct PDF object {number}, got {starts}")
    start = starts[0]
    end = pdf.find(b"endobj", start)
    if end < 0:
        raise AssertionError(f"unterminated direct PDF object {number}")
    return pdf[start + len(marker) : end]


def _stream_data(pdf: bytes, number: int) -> bytes:
    obj = _direct_object(pdf, number)
    stream_at = obj.find(b"stream")
    if stream_at < 0:
        raise AssertionError(f"PDF object {number} has no stream")
    header = obj[:stream_at]
    length_match = re.search(rb"/Length\s+([0-9]+)\b", header)
    if length_match is None:
        raise AssertionError(f"PDF object {number} has no direct stream length")
    length = int(length_match.group(1))
    data_at = stream_at + len(b"stream")
    if obj[data_at : data_at + 2] == b"\r\n":
        data_at += 2
    elif obj[data_at : data_at + 1] in (b"\r", b"\n"):
        data_at += 1
    else:
        raise AssertionError(f"PDF object {number} has malformed stream separator")
    encoded = obj[data_at : data_at + length]
    if len(encoded) != length:
        raise AssertionError(f"truncated stream in PDF object {number}")
    if b"/FlateDecode" not in header:
        raise AssertionError(f"PDF object {number} is not FlateDecode")
    return zlib.decompress(encoded)


def _compressed_objects(pdf: bytes) -> dict[int, bytes]:
    obj = _direct_object(pdf, OBJECT_STREAM_NUMBER)
    header = obj[: obj.find(b"stream")]
    n_match = re.search(rb"/N\s+([0-9]+)\b", header)
    first_match = re.search(rb"/First\s+([0-9]+)\b", header)
    if n_match is None or first_match is None:
        raise AssertionError("object stream lacks N/First")
    count = int(n_match.group(1))
    first = int(first_match.group(1))
    decoded = _stream_data(pdf, OBJECT_STREAM_NUMBER)
    index_values = [int(value) for value in decoded[:first].split()]
    if len(index_values) != 2 * count:
        raise AssertionError("object-stream index length mismatch")
    result: dict[int, bytes] = {}
    for index in range(count):
        number = index_values[2 * index]
        offset = index_values[2 * index + 1]
        next_offset = (
            index_values[2 * (index + 1) + 1]
            if index + 1 < count
            else len(decoded) - first
        )
        body = decoded[first + offset : first + next_offset].strip()
        if not body or number in result:
            raise AssertionError(f"invalid compressed PDF object {number}")
        result[number] = body
    return result


def _unicode_from_hex(value: bytes) -> str:
    raw = bytes.fromhex(value.decode("ascii"))
    if len(raw) % 2:
        raise AssertionError(f"odd UTF-16BE CMap value {value!r}")
    return raw.decode("utf-16-be")


def _parse_cmap(data: bytes) -> dict[int, str]:
    lines = [line.strip() for line in data.splitlines()]
    result: dict[int, str] = {}
    mode: str | None = None
    for line in lines:
        if line.endswith(b"beginbfchar"):
            mode = "char"
            continue
        if line == b"endbfchar":
            mode = None
            continue
        if line.endswith(b"beginbfrange"):
            mode = "range"
            continue
        if line == b"endbfrange":
            mode = None
            continue
        values = re.findall(rb"<([0-9A-Fa-f]+)>", line)
        if mode == "char" and len(values) == 2:
            source = int(values[0], 16)
            result[source] = _unicode_from_hex(values[1])
        elif mode == "range" and len(values) == 3:
            first, last, target = (int(value, 16) for value in values)
            if first > last:
                raise AssertionError("descending CMap range")
            for offset, source in enumerate(range(first, last + 1)):
                result[source] = chr(target + offset)
    if not result:
        raise AssertionError("empty ToUnicode CMap")
    return result


def _font_maps(pdf: bytes, compressed: dict[int, bytes], resource: int) -> dict[str, dict[int, str]]:
    resource_body = compressed.get(resource)
    if resource_body is None:
        raise AssertionError(f"resource object {resource} is not in the pinned object stream")
    fonts_match = re.search(rb"/Font\s*<<(.*?)>>", resource_body, re.DOTALL)
    if fonts_match is None:
        raise AssertionError(f"resource object {resource} has no font dictionary")
    references = re.findall(rb"/(F[0-9]+)\s+([0-9]+)\s+0\s+R", fonts_match.group(1))
    if not references:
        raise AssertionError(f"resource object {resource} has no fonts")
    maps: dict[str, dict[int, str]] = {}
    for raw_name, raw_number in references:
        name = raw_name.decode("ascii")
        font_number = int(raw_number)
        font_body = compressed.get(font_number)
        if font_body is None:
            raise AssertionError(f"font object {font_number} is not compressed as expected")
        unicode_match = re.search(rb"/ToUnicode\s+([0-9]+)\s+0\s+R", font_body)
        if unicode_match is None:
            raise AssertionError(f"font {name} has no ToUnicode map")
        cmap_number = int(unicode_match.group(1))
        maps[name] = _parse_cmap(_stream_data(pdf, cmap_number))
    return maps


def _literal_string(content: bytes, start: int) -> tuple[bytes, int]:
    if content[start] != ord("("):
        raise AssertionError("literal-string parser called at wrong position")
    result = bytearray()
    depth = 1
    index = start + 1
    while index < len(content) and depth:
        value = content[index]
        index += 1
        if value == ord("\\"):
            if index >= len(content):
                raise AssertionError("trailing PDF string escape")
            escaped = content[index]
            index += 1
            if escaped in b"nrtbf":
                result.append({
                    ord("n"): 10,
                    ord("r"): 13,
                    ord("t"): 9,
                    ord("b"): 8,
                    ord("f"): 12,
                }[escaped])
            elif escaped in b"()\\":
                result.append(escaped)
            elif ord("0") <= escaped <= ord("7"):
                digits = bytearray([escaped])
                while (
                    len(digits) < 3
                    and index < len(content)
                    and ord("0") <= content[index] <= ord("7")
                ):
                    digits.append(content[index])
                    index += 1
                result.append(int(digits.decode("ascii"), 8))
            elif escaped == 13:
                if index < len(content) and content[index] == 10:
                    index += 1
            elif escaped == 10:
                pass
            else:
                result.append(escaped)
        elif value == ord("("):
            depth += 1
            result.append(value)
        elif value == ord(")"):
            depth -= 1
            if depth:
                result.append(value)
        else:
            result.append(value)
    if depth:
        raise AssertionError("unterminated PDF literal string")
    return bytes(result), index


def _tokens(content: bytes) -> list[object]:
    tokens: list[object] = []
    index = 0
    whitespace = b"\x00\x09\x0a\x0c\x0d\x20"
    delimiters = b"()<>[]{}/%"
    while index < len(content):
        value = content[index]
        if value in whitespace:
            index += 1
            continue
        if value == ord("%"):
            line_end = content.find(b"\n", index)
            index = len(content) if line_end < 0 else line_end + 1
            continue
        if value == ord("("):
            token, index = _literal_string(content, index)
            tokens.append(token)
            continue
        if value in b"[]":
            tokens.append(chr(value))
            index += 1
            continue
        if value == ord("/"):
            end = index + 1
            while end < len(content) and content[end] not in whitespace + delimiters:
                end += 1
            tokens.append(content[index:end].decode("ascii"))
            index = end
            continue
        end = index
        while end < len(content) and content[end] not in whitespace + delimiters:
            end += 1
        raw = content[index:end]
        try:
            token: object = float(raw) if b"." in raw else int(raw)
        except ValueError:
            token = raw.decode("ascii")
        tokens.append(token)
        index = end
    return tokens


def _decode_text(content: bytes, font_maps: dict[str, dict[int, str]]) -> str:
    operands: list[object] = []
    array_markers: list[int] = []
    current_font: str | None = None
    output: list[str] = []

    def decode(raw: bytes) -> str:
        if current_font is None:
            raise AssertionError("text shown before a font is selected")
        cmap = font_maps.get(current_font)
        if cmap is None:
            raise AssertionError(f"font {current_font} absent from page resources")
        # Some CMEX glyphs in the proof preceding Appendix B have no ToUnicode
        # entry.  Preserve each such byte as an explicit sentinel; the caller
        # later requires that the isolated Theorem 9 slice contain none.
        return "".join(
            cmap.get(value, f"⟦{current_font}:{value:02X}⟧") for value in raw
        )

    for token in _tokens(content):
        if token == "[":
            array_markers.append(len(operands))
            continue
        if token == "]":
            if not array_markers:
                raise AssertionError("unmatched PDF content array")
            start = array_markers.pop()
            values = operands[start:]
            del operands[start:]
            operands.append(values)
            continue
        if isinstance(token, (bytes, int, float)) or (
            isinstance(token, str) and token.startswith("/")
        ):
            operands.append(token)
            continue
        if token == "Tf":
            if len(operands) < 2 or not isinstance(operands[-2], str):
                raise AssertionError("malformed Tf operator")
            current_font = operands[-2][1:]
        elif token == "Tj":
            if not operands or not isinstance(operands[-1], bytes):
                raise AssertionError("malformed Tj operator")
            output.append(decode(operands[-1]))
        elif token == "TJ":
            if not operands or not isinstance(operands[-1], list):
                raise AssertionError("malformed TJ operator")
            for item in operands[-1]:
                if isinstance(item, bytes):
                    output.append(decode(item))
                elif not isinstance(item, (int, float)):
                    raise AssertionError("invalid TJ array item")
        operands.clear()
    if array_markers:
        raise AssertionError("unterminated PDF content array")
    return "".join(output)


def extract_appendix_pages(pdf: bytes) -> tuple[ExtractedPage, ...]:
    compressed = _compressed_objects(pdf)
    pages: list[ExtractedPage] = []
    for page, page_object, content_object, resource_object in PAGE_BINDINGS:
        page_body = _direct_object(pdf, page_object)
        expected_contents = f"/Contents {content_object} 0 R".encode("ascii")
        expected_resources = f"/Resources {resource_object} 0 R".encode("ascii")
        if expected_contents not in page_body or expected_resources not in page_body:
            raise AssertionError(f"page {page} structure does not match pinned bindings")
        content = _stream_data(pdf, content_object)
        maps = _font_maps(pdf, compressed, resource_object)
        pages.append(ExtractedPage(page, _decode_text(content, maps)))
    return tuple(pages)
