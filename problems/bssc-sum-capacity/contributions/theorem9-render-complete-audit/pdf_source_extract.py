#!/usr/bin/env python3
"""Fail-closed rendering audit for the pinned GLN Theorem 9 source pages.

This is deliberately a verifier for one authenticated pdfTeX artifact, not a
general PDF reader. It resolves the complete page/resource envelope for PDF
pages 14--15, inventories every content-stream operator, tracks the exact text
and graphics state used by those streams, and rejects anything outside the
observed profile. No text-showing, clipping, transparency, image, Form
XObject, optional-content, or painting operation is silently ignored.
"""

from __future__ import annotations

import hashlib
import math
import re
import zlib
from collections import Counter
from dataclasses import dataclass


PAGE_BINDINGS = ((14, 29, 30, 108), (15, 31, 32, 109))
CATALOG_OBJECT = 49
LATEST_XREF_OBJECT = 48
PREVIOUS_XREF_OBJECT = 46
PAGE_TREE_ROOT = 145
OBJECT_STREAM_NUMBER = 53
MEDIA_BOX = (0.0, 0.0, 612.0, 792.0)
EXPECTED_OPERATOR_COUNTS = {
    14: {
        "BT": 1, "ET": 1, "Tf": 1100, "Td": 1123, "TJ": 1123,
        "g": 8, "G": 8, "rg": 2, "RG": 2,
    },
    15: {
        "BT": 1, "ET": 1, "Tf": 862, "Td": 868, "TJ": 868,
        "g": 4, "G": 4,
    },
}
EXPECTED_PAGE_RESOURCES = {
    108: (
        b"<< /ColorSpace 74 0 R /ExtGState 72 0 R /Font << "
        b"/F13 88 0 R /F19 83 0 R /F20 79 0 R /F22 81 0 R "
        b"/F23 80 0 R /F25 82 0 R /F26 77 0 R /F78 76 0 R "
        b"/F81 78 0 R /F85 84 0 R >> /Pattern 73 0 R "
        b"/ProcSet [ /PDF /Text ] >>"
    ),
    109: (
        b"<< /ColorSpace 74 0 R /ExtGState 72 0 R /Font << "
        b"/F19 83 0 R /F20 79 0 R /F21 90 0 R /F22 81 0 R "
        b"/F23 80 0 R /F25 82 0 R /F26 77 0 R /F78 76 0 R "
        b"/F85 84 0 R >> /Pattern 73 0 R /ProcSet [ /PDF /Text ] >>"
    ),
}
EXPECTED_FONT_PROGRAM_SHA256 = {
    33: "cd29a743fcd639bccfee39e588498f69a5eab2f5d7361a59f6e840f4b008195a",
    34: "facee11a0964a7248c0376bf1245201bfd917d35a8b0b5b700f3744740cb7b95",
    54: "41cf6e5701d367303f6840757f9976a3d1b5c5546ff10aa78f0e1cb70b0ba062",
    55: "1b829731e5c68add65e0f268663c4f1dc835a9afa9f182464f14cc7b9ed2f2de",
    56: "30ed29fadc673f43e6804d9ae028efa46401aca88530a3d991224fe18a2e23ce",
    57: "3f212fc86e4ac515748f614efd4d5459d2ac5a25bb9e4a8ad68fe411dd03e4db",
    58: "82edbea4aa9d0d3d7b57a860e3138cdd53431d995641d85ae5f143be0f30ca4f",
    59: "4dd83fd75ff52484280f23a4786bd51c5c8927aeac49c2a6e954858b34d71a30",
    60: "22b691da2ac9de7c06fba8ac696f04fcbe089f8b9383ab733f15ef6b43db60ce",
    61: "88de7a5bb6c635a2648e216cf9d0a3b60c2920955bda76c3567b9f4c1a1a1f0f",
    62: "25769e5e69bdfc6e15f06c2676b4752b3f997caca03d93c1d54a3282c15f6788",
}


@dataclass(frozen=True)
class FontInfo:
    name: str
    cmap: dict[int, str]
    glyph_names: dict[int, str]
    widths: dict[int, float]
    bbox: tuple[float, float, float, float]
    charset: frozenset[str]
    charstrings: frozenset[str]


@dataclass(frozen=True)
class Glyph:
    text: str
    code: int
    glyph_name: str
    font: str
    font_size: float
    x: float
    y: float
    bbox: tuple[float, float, float, float]
    fill_color: tuple[str, float, float, float]


@dataclass(frozen=True)
class ExtractedPage:
    number: int
    text: str
    glyphs: tuple[Glyph, ...]
    media_box: tuple[float, float, float, float]
    operator_counts: tuple[tuple[str, int], ...]
    resource_closure: tuple[int, ...]


def _direct_object(pdf: bytes, number: int) -> bytes:
    pattern = re.compile(
        rb"(?m)^" + re.escape(f"{number} 0 obj".encode("ascii")) + rb"\r?$"
    )
    matches = list(pattern.finditer(pdf))
    if len(matches) != 1:
        raise AssertionError(
            f"expected one direct PDF object {number}, got "
            f"{[match.start() for match in matches]}"
        )
    start = matches[0].end()
    end = pdf.find(b"endobj", start)
    if end < 0:
        raise AssertionError(f"unterminated direct PDF object {number}")
    return pdf[start:end]


def _stream_data(pdf: bytes, number: int) -> bytes:
    obj = _direct_object(pdf, number)
    stream_at = obj.find(b"stream")
    if stream_at < 0:
        raise AssertionError(f"PDF object {number} has no stream")
    header = obj[:stream_at]
    length_matches = re.findall(rb"/Length\b\s+([0-9]+)\b", header)
    if len(length_matches) != 1:
        raise AssertionError(f"PDF object {number} has no direct stream length")
    if len(re.findall(rb"/Filter\b", header)) != 1 or len(
        re.findall(rb"/Filter\s*/FlateDecode\b", header)
    ) != 1:
        raise AssertionError(f"PDF object {number} is not one FlateDecode stream")
    if b"/DecodeParms" in header:
        raise AssertionError(f"PDF object {number} has unsupported decode parameters")
    length = int(length_matches[0])
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
    decoder = zlib.decompressobj()
    decoded = decoder.decompress(encoded) + decoder.flush()
    if decoder.unused_data or decoder.unconsumed_tail or not decoder.eof:
        raise AssertionError(f"PDF object {number} has a non-terminal Flate payload")
    return decoded


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


def _object_body(pdf: bytes, compressed: dict[int, bytes], number: int) -> bytes:
    return compressed[number] if number in compressed else _direct_object(pdf, number)


def _object_header(pdf: bytes, compressed: dict[int, bytes], number: int) -> bytes:
    return _object_body(pdf, compressed, number).split(b"stream", 1)[0]


def _indirect_references(body: bytes) -> tuple[int, ...]:
    return tuple(int(value) for value in re.findall(rb"\b([0-9]+)\s+0\s+R\b", body))


def _xref_entries(
    pdf: bytes,
    object_number: int,
    first_object: int,
    count: int,
) -> dict[int, tuple[int, int, int]]:
    obj = _direct_object(pdf, object_number)
    stream_at = obj.find(b"stream")
    if stream_at < 0:
        raise AssertionError(f"xref object {object_number} has no stream")
    header = b" ".join(obj[:stream_at].split())
    required = (
        b"/Type /XRef",
        b"/Filter /FlateDecode",
        b"/DecodeParms << /Columns 5 /Predictor 12 >>",
        b"/W [ 1 3 1 ]",
    )
    if any(field not in header for field in required):
        raise AssertionError(f"xref object {object_number} is outside the pinned profile")
    length_match = re.search(rb"/Length\s+([0-9]+)\b", header)
    if length_match is None:
        raise AssertionError(f"xref object {object_number} lacks a direct length")
    data_at = stream_at + len(b"stream")
    if obj[data_at : data_at + 2] == b"\r\n":
        data_at += 2
    elif obj[data_at : data_at + 1] in (b"\r", b"\n"):
        data_at += 1
    else:
        raise AssertionError(f"xref object {object_number} has a malformed separator")
    length = int(length_match.group(1))
    encoded = obj[data_at : data_at + length]
    decoder = zlib.decompressobj()
    decoded = decoder.decompress(encoded) + decoder.flush()
    if decoder.unused_data or decoder.unconsumed_tail or not decoder.eof:
        raise AssertionError(f"xref object {object_number} has a non-terminal Flate payload")
    if len(decoded) != 6 * count:
        raise AssertionError(f"xref object {object_number} has the wrong row count")

    previous = bytes(5)
    result: dict[int, tuple[int, int, int]] = {}
    for index in range(count):
        row = decoded[6 * index : 6 * (index + 1)]
        if row[0] != 2:
            raise AssertionError("pinned xref rows must use only PNG Up prediction")
        current = bytes((row[position + 1] + previous[position]) & 0xFF for position in range(5))
        previous = current
        result[first_object + index] = (
            current[0],
            int.from_bytes(current[1:4], "big"),
            current[4],
        )
    return result


def _audit_document_root(pdf: bytes, compressed: dict[int, bytes]) -> None:
    if not pdf.startswith(b"%PDF-1.5\n%"):
        raise AssertionError("pinned source has an unexpected PDF header")

    xref_pattern = re.compile(
        rb"(?m)^" + str(LATEST_XREF_OBJECT).encode("ascii") + rb" 0 obj\r?$"
    )
    xref_matches = list(xref_pattern.finditer(pdf))
    if len(xref_matches) != 1:
        raise AssertionError("latest cross-reference stream is not uniquely bound")
    startxref_matches = re.findall(rb"startxref\s+([0-9]+)\s+%%EOF\s*$", pdf)
    if len(startxref_matches) != 1 or int(startxref_matches[0]) != xref_matches[0].start():
        raise AssertionError("startxref does not select the pinned latest xref stream")

    xref_header = b" ".join(_direct_object(pdf, LATEST_XREF_OBJECT).split(b"stream", 1)[0].split())
    expected_xref_header = (
        b"<< /Type /XRef /Length 108 /Filter /FlateDecode /DecodeParms << "
        b"/Columns 5 /Predictor 12 >> /W [ 1 3 1 ] /Index [ 47 99 ] "
        b"/Info 45 0 R /Root 49 0 R /Size 146 /Prev 254718 /ID "
        b"[<7b8bcbe4b474fd0e75c1671cffa705b1>"
        b"<e926657c0e97ab670f3543cd1269cc2d>] >>"
    )
    if xref_header != expected_xref_header:
        raise AssertionError("latest xref stream is outside the pinned document profile")
    root_keys = re.findall(rb"/Root\b", xref_header)
    root_match = re.search(rb"/Root\b\s+([0-9]+)\s+0\s+R(?=\s|/|>>)", xref_header)
    if len(root_keys) != 1 or root_match is None or int(root_match.group(1)) != CATALOG_OBJECT:
        raise AssertionError("latest xref stream does not uniquely select the pinned catalog")

    previous_pattern = re.compile(
        rb"(?m)^" + str(PREVIOUS_XREF_OBJECT).encode("ascii") + rb" 0 obj\r?$"
    )
    previous_matches = list(previous_pattern.finditer(pdf))
    if len(previous_matches) != 1 or previous_matches[0].start() != 254718:
        raise AssertionError("latest xref /Prev does not select the pinned prior xref stream")
    previous_header = b" ".join(
        _direct_object(pdf, PREVIOUS_XREF_OBJECT).split(b"stream", 1)[0].split()
    )
    expected_previous_header = (
        b"<< /Type /XRef /Length 146 /Filter /FlateDecode /DecodeParms << "
        b"/Columns 5 /Predictor 12 >> /W [ 1 3 1 ] /Size 47 /ID "
        b"[<7b8bcbe4b474fd0e75c1671cffa705b1>"
        b"<e926657c0e97ab670f3543cd1269cc2d>] >>"
    )
    if previous_header != expected_previous_header:
        raise AssertionError("prior xref stream is outside the pinned document profile")
    if b"/Root" in previous_header:
        raise AssertionError("prior xref stream unexpectedly shadows the document root")

    latest_entries = _xref_entries(pdf, LATEST_XREF_OBJECT, 47, 99)
    previous_entries = _xref_entries(pdf, PREVIOUS_XREF_OBJECT, 0, 47)
    entries = previous_entries | latest_entries
    if set(entries) != set(range(146)) or entries[0] != (0, 0, 0):
        raise AssertionError("xref chain does not cover the exact pinned object range")

    compressed_indices = {number: index for index, number in enumerate(compressed)}
    direct_numbers: set[int] = set()
    for number in range(1, 146):
        entry_type, location, generation_or_index = entries[number]
        if number in compressed_indices:
            expected = (2, OBJECT_STREAM_NUMBER, compressed_indices[number])
            if entries[number] != expected:
                raise AssertionError(f"xref entry for compressed object {number} is wrong")
            continue
        if entry_type != 1 or generation_or_index != 0:
            raise AssertionError(f"xref entry for direct object {number} is wrong")
        pattern = re.compile(
            rb"(?m)^" + str(number).encode("ascii") + rb" 0 obj\r?$"
        )
        matches = list(pattern.finditer(pdf))
        if len(matches) != 1 or matches[0].start() != location:
            raise AssertionError(f"xref/direct-byte mismatch for object {number}")
        direct_numbers.add(number)

    all_headers = {
        int(match.group(1))
        for match in re.finditer(rb"(?m)^([0-9]+) 0 obj\r?$", pdf)
    }
    if all_headers != direct_numbers:
        raise AssertionError("unindexed or shadow direct object header in pinned PDF")

    catalog = b" ".join(_direct_object(pdf, CATALOG_OBJECT).split())
    expected_catalog = f"<< /Pages {PAGE_TREE_ROOT} 0 R /Type /Catalog >>".encode("ascii")
    if catalog != expected_catalog:
        raise AssertionError("pinned catalog does not select the audited page-tree root")


def _page_tree_order(pdf: bytes, compressed: dict[int, bytes]) -> tuple[int, ...]:
    active: set[int] = set()

    def visit(number: int, parent: int | None) -> tuple[int, ...]:
        if number in active:
            raise AssertionError("cycle in pinned PDF page tree")
        active.add(number)
        body = _object_header(pdf, compressed, number)
        if re.search(rb"/Type\s*/Page\b", body):
            if parent is None or f"/Parent {parent} 0 R".encode("ascii") not in body:
                raise AssertionError(f"page object {number} has the wrong parent")
            result = (number,)
        elif re.search(rb"/Type\s*/Pages\b", body):
            inherited = (b"/MediaBox", b"/CropBox", b"/Rotate", b"/Resources")
            if any(marker in body for marker in inherited):
                raise AssertionError(
                    f"page-tree node {number} overrides a pinned inheritable page attribute"
                )
            parent_match = re.search(rb"/Parent\s+([0-9]+)\s+0\s+R", body)
            if parent is None:
                if parent_match is not None:
                    raise AssertionError("page-tree root unexpectedly has a parent")
            elif parent_match is None or int(parent_match.group(1)) != parent:
                raise AssertionError(f"page-tree node {number} has the wrong parent")
            kids_match = re.search(rb"/Kids\s*\[(.*?)\]", body, re.DOTALL)
            count_match = re.search(rb"/Count\s+([0-9]+)\b", body)
            if kids_match is None or count_match is None:
                raise AssertionError(f"page-tree node {number} lacks Kids/Count")
            kids = _indirect_references(kids_match.group(1))
            if not kids:
                raise AssertionError(f"page-tree node {number} has no children")
            result = tuple(page for kid in kids for page in visit(kid, number))
            if int(count_match.group(1)) != len(result):
                raise AssertionError(f"page-tree Count mismatch at object {number}")
        else:
            raise AssertionError(f"page-tree object {number} has no Page(s) type")
        active.remove(number)
        return result

    order = visit(PAGE_TREE_ROOT, None)
    if len(order) != 15 or order[13:15] != (29, 31):
        raise AssertionError(f"pinned source page order mismatch: {order}")
    return order


def _audit_page_envelope(
    pdf: bytes,
    page_object: int,
    content_object: int,
    resource_object: int,
) -> None:
    actual = b" ".join(_direct_object(pdf, page_object).split())
    expected = (
        f"<< /Contents {content_object} 0 R /MediaBox [ 0 0 612 792 ] "
        f"/Parent 107 0 R /Resources {resource_object} 0 R /Type /Page >>"
    ).encode("ascii")
    if actual != expected:
        raise AssertionError(
            f"page object {page_object} is not the exact single-stream, "
            "annotation-free pinned envelope"
        )


def _audit_resource_graph(
    pdf: bytes,
    compressed: dict[int, bytes],
    resource_object: int,
) -> tuple[int, ...]:
    root = _object_header(pdf, compressed, resource_object)
    normalized = b" ".join(root.split())
    if normalized != EXPECTED_PAGE_RESOURCES[resource_object]:
        raise AssertionError(
            f"page resource object {resource_object} is not the exact reviewed dictionary"
        )
    if b"/ProcSet [ /PDF /Text ]" not in normalized:
        raise AssertionError("page resource ProcSet is not exactly PDF/Text")
    if b"/XObject" in root:
        raise AssertionError("pinned page resources unexpectedly contain XObject")
    if b"/ExtGState 72 0 R" not in root:
        raise AssertionError("pinned page resources do not use the audited ExtGState")
    if b" ".join(_object_header(pdf, compressed, 72).split()) != b"<< >>":
        raise AssertionError("pinned ExtGState resource is not empty")
    seen: set[int] = set()
    pending = [resource_object]
    while pending:
        number = pending.pop()
        if number in seen:
            continue
        seen.add(number)
        header = _object_header(pdf, compressed, number)
        forbidden = (
            b"/Type /XObject", b"/Subtype /Form", b"/Subtype /Image",
            b"/Subtype /PS", b"/SMask", b"/OC ", b"/OCProperties",
        )
        if any(marker in header for marker in forbidden):
            raise AssertionError(f"forbidden render resource reachable at object {number}")
        for reference in _indirect_references(header):
            _object_header(pdf, compressed, reference)
            if reference not in seen:
                pending.append(reference)
    return tuple(sorted(seen))


def _unicode_from_hex(value: bytes) -> str:
    raw = bytes.fromhex(value.decode("ascii"))
    if len(raw) % 2:
        raise AssertionError(f"odd UTF-16BE CMap value {value!r}")
    return raw.decode("utf-16-be")


def _parse_cmap(data: bytes) -> dict[int, str]:
    if len(re.findall(rb"/CMapType\b", data)) != 1 or data.count(b"/CMapType 2 def") != 1:
        raise AssertionError("ToUnicode CMap is not one type-2 mapping")
    forbidden = (b"usecmap", b"/WMode", b"beginnotdefchar", b"beginnotdefrange")
    if any(marker in data for marker in forbidden):
        raise AssertionError("ToUnicode CMap uses an unsupported inherited/vertical mapping")
    codespace_blocks = re.findall(
        rb"1\s+begincodespacerange\s*<00>\s*<FF>\s*endcodespacerange",
        data,
        re.DOTALL,
    )
    if (
        len(codespace_blocks) != 1
        or data.count(b"begincodespacerange") != 1
        or data.count(b"endcodespacerange") != 1
    ):
        raise AssertionError("ToUnicode CMap does not have the exact one-byte codespace")

    lines = [line.strip() for line in data.splitlines()]
    result: dict[int, str] = {}
    mode: str | None = None
    expected_entries = 0
    actual_entries = 0
    block_counts = Counter()

    def assign(source: int, target: str) -> None:
        if not 0 <= source <= 255 or source in result:
            raise AssertionError("duplicate or out-of-range ToUnicode source code")
        result[source] = target

    for line in lines:
        char_start = re.fullmatch(rb"([0-9]+)\s+beginbfchar", line)
        range_start = re.fullmatch(rb"([0-9]+)\s+beginbfrange", line)
        if char_start is not None:
            if mode is not None:
                raise AssertionError("nested ToUnicode mapping block")
            mode = "char"
            expected_entries = int(char_start.group(1))
            actual_entries = 0
            block_counts[mode] += 1
            continue
        if line == b"endbfchar":
            if mode != "char" or actual_entries != expected_entries:
                raise AssertionError("ToUnicode bfchar count mismatch")
            mode = None
            continue
        if range_start is not None:
            if mode is not None:
                raise AssertionError("nested ToUnicode mapping block")
            mode = "range"
            expected_entries = int(range_start.group(1))
            actual_entries = 0
            block_counts[mode] += 1
            continue
        if line == b"endbfrange":
            if mode != "range" or actual_entries != expected_entries:
                raise AssertionError("ToUnicode bfrange count mismatch")
            mode = None
            continue
        if mode == "char":
            mapping = re.fullmatch(
                rb"<([0-9A-Fa-f]{2})>\s+<([0-9A-Fa-f]+)>", line
            )
            if mapping is None:
                raise AssertionError("unparsed ToUnicode bfchar entry")
            assign(int(mapping.group(1), 16), _unicode_from_hex(mapping.group(2)))
            actual_entries += 1
        elif mode == "range":
            mapping = re.fullmatch(
                rb"<([0-9A-Fa-f]{2})>\s+<([0-9A-Fa-f]{2})>\s+"
                rb"<([0-9A-Fa-f]{4})>",
                line,
            )
            if mapping is None:
                raise AssertionError("unparsed ToUnicode bfrange entry")
            first, last, target = (int(value, 16) for value in mapping.groups())
            if first > last:
                raise AssertionError("descending CMap range")
            for offset, source in enumerate(range(first, last + 1)):
                assign(source, chr(target + offset))
            actual_entries += 1
        elif re.match(rb"<[0-9A-Fa-f]", line) and line != b"<00> <FF>":
            raise AssertionError("unscoped ToUnicode mapping token")
    if mode is not None or block_counts != Counter({"char": 1, "range": 1}) or not result:
        raise AssertionError("empty ToUnicode CMap")
    return result


def _numbers(value: bytes) -> tuple[float, ...]:
    return tuple(
        float(item)
        for item in re.findall(rb"[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)", value)
    )


def _standard_encoding() -> dict[int, str]:
    result = {code: chr(code) for code in range(ord("A"), ord("Z") + 1)}
    result.update({code: chr(code) for code in range(ord("a"), ord("z") + 1)})
    names = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
    result.update({48 + index: name for index, name in enumerate(names)})
    result.update({
        32: "space", 39: "quoteright", 40: "parenleft", 41: "parenright",
        44: "comma", 45: "hyphen", 46: "period", 47: "slash",
        58: "colon", 59: "semicolon", 61: "equal", 91: "bracketleft",
        93: "bracketright", 96: "quoteleft",
    })
    return result


def _parse_pdf_encoding(body: bytes) -> dict[int, str]:
    normalized = b" ".join(body.split())
    profile = re.fullmatch(
        rb"<< /Differences \[ (.*?) \] /Type /Encoding >>",
        normalized,
    )
    if profile is None:
        raise AssertionError("indirect PDF encoding is outside the pinned dictionary profile")
    result = _standard_encoding()
    encoded_tokens = re.findall(rb"/[A-Za-z0-9_.]+|[0-9]+", profile.group(1))
    if b" ".join(encoded_tokens) != profile.group(1):
        raise AssertionError("indirect PDF Differences contains an unparsed token")
    current: int | None = None
    for token in encoded_tokens:
        if token.startswith(b"/"):
            if current is None:
                raise AssertionError("PDF Differences name precedes a code")
            result[current] = token[1:].decode("ascii")
            current += 1
        else:
            current = int(token)
    return result


def _parse_program_encoding(program: bytes) -> dict[int, str]:
    before_eexec, separator, _ = program.partition(b"currentfile eexec")
    if not separator or program.count(b"currentfile eexec") != 1:
        raise AssertionError("embedded Type1 program has an ambiguous eexec boundary")
    font_type_definitions = re.findall(
        rb"/FontType\s+([-+]?[0-9]+)\s+def\b", before_eexec
    )
    if font_type_definitions != [b"1"]:
        raise AssertionError("embedded font is not a bounded Type1 program")
    paint_type_definitions = re.findall(
        rb"/PaintType\s+([-+]?[0-9]+)\s+def\b", before_eexec
    )
    if paint_type_definitions != [b"0"]:
        raise AssertionError("embedded Type1 font is not fill-painted")
    matrix_matches = re.findall(
        rb"/FontMatrix\s*\[([^]]+)\]\s*readonly def", before_eexec
    )
    if len(re.findall(rb"/FontMatrix\b", before_eexec)) != 1 or len(matrix_matches) != 1:
        raise AssertionError("embedded Type1 font has an ambiguous FontMatrix")
    matrix_match = matrix_matches[0]
    if _numbers(matrix_match) != (0.001, 0.0, 0.0, 0.001, 0.0, 0.0):
        raise AssertionError("embedded Type1 font matrix is not the pinned identity scale")
    encoding_keys = re.findall(rb"/Encoding\b", before_eexec)
    standard_definitions = re.findall(
        rb"/Encoding\s+StandardEncoding\s+def\b", before_eexec
    )
    explicit_definitions = re.findall(rb"/Encoding\s+256\s+array\b", before_eexec)
    if len(encoding_keys) != 1:
        raise AssertionError("embedded Type1 program must define Encoding exactly once")
    if len(standard_definitions) == 1 and not explicit_definitions:
        return _standard_encoding()
    if len(explicit_definitions) != 1 or standard_definitions:
        raise AssertionError("embedded Type1 Encoding has an unsupported definition")
    start = before_eexec.find(b"/Encoding 256 array")
    initialization = re.findall(
        rb"0\s+1\s+255\s+\{\s*1\s+index\s+exch\s+/\.notdef\s+put\s*\}\s+for",
        before_eexec[start:],
    )
    if len(initialization) != 1:
        raise AssertionError("embedded explicit Encoding lacks one .notdef initialization")
    encoding_pairs = re.findall(
        rb"dup\s+([0-9]+)\s+/([^\s]+)\s+put", before_eexec[start:]
    )
    encoding = {int(code): name.decode("ascii") for code, name in encoding_pairs}
    if not encoding:
        raise AssertionError("embedded Type1 encoding is empty")
    if len(encoding) != len(encoding_pairs):
        raise AssertionError("embedded Type1 Encoding assigns a code more than once")
    return encoding


def _decrypt_type1(ciphertext: bytes, key: int) -> bytes:
    state = key
    output = bytearray()
    for value in ciphertext:
        plain = value ^ (state >> 8)
        state = ((value + state) * 52845 + 22719) & 0xFFFF
        output.append(plain)
    if len(output) < 4:
        raise AssertionError("truncated Type1 encrypted section")
    return bytes(output[4:])


def _type1_charstrings(program: bytes, length1: int, length2: int) -> frozenset[str]:
    if length1 <= 0 or length2 <= 4 or length1 + length2 > len(program):
        raise AssertionError("invalid Type1 Length1/Length2 envelope")
    if b"currentfile eexec" not in program[:length1]:
        raise AssertionError("Type1 cleartext/eexec boundary is not inside Length1")
    decrypted = _decrypt_type1(program[length1 : length1 + length2], 55665)
    declared_matches = re.findall(
        rb"/CharStrings\s+([0-9]+)\s+dict\s+dup\s+begin", decrypted
    )
    if len(re.findall(rb"/CharStrings\b", decrypted)) != 1 or len(declared_matches) != 1:
        raise AssertionError("decrypted Type1 program lacks CharStrings dictionary")
    raw_names = re.findall(
        rb"/([A-Za-z0-9_.]+)\s+[0-9]+\s+(?:RD|-\|)", decrypted
    )
    names = {value.decode("ascii") for value in raw_names}
    if (
        len(raw_names) != int(declared_matches[0])
        or len(names) != len(raw_names)
        or ".notdef" not in names
    ):
        raise AssertionError("decrypted Type1 CharStrings inventory mismatch")
    return frozenset(names)


def glyph_name_unicode(name: str) -> str:
    """Canonical Unicode for the bounded theorem glyph-name vocabulary."""
    if len(name) == 1 and name.isascii() and name.isalnum():
        return name
    values = {
        "zero": "0", "one": "1", "two": "2", "three": "3",
        "four": "4", "five": "5", "six": "6", "seven": "7",
        "eight": "8", "nine": "9", "parenleft": "(",
        "parenright": ")", "plus": "+", "period": ".", "comma": ",",
        "colon": ":", "semicolon": ";", "equal": "=", "hyphen": "-",
        "bar": "|", "braceleft": "{", "braceright": "}",
        "minus": "−", "lessequal": "≤", "fi": "fi",
    }
    if name not in values:
        raise AssertionError(f"glyph name {name!r} is outside the theorem vocabulary")
    return values[name]


def _font_infos(
    pdf: bytes,
    compressed: dict[int, bytes],
    resource: int,
) -> dict[str, FontInfo]:
    resource_body = _object_header(pdf, compressed, resource)
    fonts_match = re.search(rb"/Font\s*<<(.*?)>>", resource_body, re.DOTALL)
    if fonts_match is None:
        raise AssertionError(f"resource object {resource} has no font dictionary")
    references = re.findall(rb"/(F[0-9]+)\s+([0-9]+)\s+0\s+R", fonts_match.group(1))
    if not references:
        raise AssertionError(f"resource object {resource} has no fonts")
    result: dict[str, FontInfo] = {}
    for raw_name, raw_number in references:
        name = raw_name.decode("ascii")
        font_body = _object_header(pdf, compressed, int(raw_number))
        normalized_font = b" ".join(font_body.split())
        font_profile = re.fullmatch(
            rb"<< /BaseFont /[A-Za-z0-9+_.-]+ "
            rb"(?:/Encoding 118 0 R )?"
            rb"/FirstChar [0-9]+ /FontDescriptor [0-9]+ 0 R "
            rb"/LastChar [0-9]+ /Subtype /Type1 /ToUnicode [0-9]+ 0 R "
            rb"/Type /Font /Widths [0-9]+ 0 R >>",
            normalized_font,
        )
        if font_profile is None:
            raise AssertionError(f"font {name} is outside the exact simple-Type1 profile")
        first_match = re.search(rb"/FirstChar\s+([0-9]+)\b", font_body)
        last_match = re.search(rb"/LastChar\s+([0-9]+)\b", font_body)
        width_match = re.search(rb"/Widths\s+([0-9]+)\s+0\s+R", font_body)
        unicode_match = re.search(rb"/ToUnicode\s+([0-9]+)\s+0\s+R", font_body)
        descriptor_match = re.search(rb"/FontDescriptor\s+([0-9]+)\s+0\s+R", font_body)
        if any(item is None for item in (first_match, last_match, width_match, unicode_match, descriptor_match)):
            raise AssertionError(f"font {name} lacks a pinned simple-font field")
        first = int(first_match.group(1))
        last = int(last_match.group(1))
        width_body = b" ".join(
            _object_header(pdf, compressed, int(width_match.group(1))).split()
        )
        number_token = rb"[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)"
        if re.fullmatch(
            rb"\[ " + number_token + rb"(?: " + number_token + rb")* \]",
            width_body,
        ) is None:
            raise AssertionError(f"font {name} widths are outside the pinned array profile")
        width_values = _numbers(width_body)
        if len(width_values) != last - first + 1:
            raise AssertionError(f"font {name} width array length mismatch")
        widths = {first + index: value for index, value in enumerate(width_values)}
        descriptor = _object_header(pdf, compressed, int(descriptor_match.group(1)))
        normalized_descriptor = b" ".join(descriptor.split())
        numeric = rb"[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)"
        descriptor_profile = re.fullmatch(
            rb"<< /Ascent " + numeric
            + rb" /CapHeight " + numeric
            + rb" /CharSet \([^)]*\) /Descent " + numeric
            + rb" /Flags [0-9]+ /FontBBox \[ " + numeric
            + rb" " + numeric + rb" " + numeric + rb" " + numeric
            + rb" \] /FontFile [0-9]+ 0 R /FontName /[A-Za-z0-9+_.-]+"
            + rb" /ItalicAngle " + numeric
            + rb" /StemV " + numeric
            + rb" /Type /FontDescriptor /XHeight " + numeric + rb" >>",
            normalized_descriptor,
        )
        if descriptor_profile is None:
            raise AssertionError(
                f"font descriptor for {name} is outside the exact pinned profile"
            )
        bbox_match = re.search(rb"/FontBBox\s*\[([^]]+)\]", descriptor)
        file_match = re.search(rb"/FontFile\s+([0-9]+)\s+0\s+R", descriptor)
        charset_match = re.search(rb"/CharSet\s*\(([^)]*)\)", descriptor)
        if bbox_match is None or file_match is None or charset_match is None:
            raise AssertionError(f"font descriptor for {name} lacks bbox/file/charset")
        bbox_values = _numbers(bbox_match.group(1))
        if len(bbox_values) != 4:
            raise AssertionError(f"font {name} bbox is malformed")
        bbox = tuple(bbox_values)
        file_number = int(file_match.group(1))
        file_header = _object_header(pdf, compressed, file_number)
        normalized_file_header = b" ".join(file_header.split())
        if re.fullmatch(
            rb"<< /Filter /FlateDecode /Length1 [0-9]+ /Length2 [0-9]+ "
            rb"/Length3 0 /Length [0-9]+ >>",
            normalized_file_header,
        ) is None:
            raise AssertionError(f"embedded font file for {name} has an ambiguous envelope")
        length1_match = re.search(rb"/Length1\s+([0-9]+)\b", file_header)
        length2_match = re.search(rb"/Length2\s+([0-9]+)\b", file_header)
        if length1_match is None or length2_match is None:
            raise AssertionError(f"embedded font file for {name} lacks Length1/Length2")
        program = _stream_data(pdf, file_number)
        program_bbox_match = re.search(rb"/FontBBox\s*[\[{]([^}\]]+)[}\]]", program[:2400])
        if program_bbox_match is None or _numbers(program_bbox_match.group(1)) != bbox:
            raise AssertionError(f"font {name} descriptor/program bbox mismatch")
        program_encoding = _parse_program_encoding(program)
        encoding_keys = re.findall(rb"/Encoding\b", font_body)
        if len(encoding_keys) > 1:
            raise AssertionError(f"font {name} has duplicate Encoding keys")
        encoding_match = re.search(
            rb"/Encoding\b\s+([0-9]+)\s+0\s+R(?=\s|/|>>)",
            font_body,
        )
        if encoding_keys and encoding_match is None:
            raise AssertionError(f"font {name} has an unsupported Encoding value")
        if encoding_match is not None:
            encoding_number = int(encoding_match.group(1))
            if encoding_number != 118:
                raise AssertionError(
                    f"font {name} references unexpected Encoding object {encoding_number}"
                )
            glyph_names = _parse_pdf_encoding(
                _object_header(pdf, compressed, encoding_number)
            )
        else:
            glyph_names = program_encoding
        charset = set(re.findall(rb"/([^/\s]+)", charset_match.group(1)))
        charset_names = frozenset(value.decode("ascii") for value in charset)
        charstrings = _type1_charstrings(
            program,
            int(length1_match.group(1)),
            int(length2_match.group(1)),
        )
        program_digest = hashlib.sha256(program).hexdigest()
        if EXPECTED_FONT_PROGRAM_SHA256.get(file_number) != program_digest:
            raise AssertionError(
                f"embedded font program {file_number} does not match its reviewed digest"
            )
        cmap = _parse_cmap(_stream_data(pdf, int(unicode_match.group(1))))
        result[name] = FontInfo(
            name, cmap, glyph_names, widths, bbox, charset_names, charstrings
        )
    return result


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
                result.append({ord("n"): 10, ord("r"): 13, ord("t"): 9, ord("b"): 8, ord("f"): 12}[escaped])
            elif escaped in b"()\\":
                result.append(escaped)
            elif ord("0") <= escaped <= ord("7"):
                digits = bytearray([escaped])
                while len(digits) < 3 and index < len(content) and ord("0") <= content[index] <= ord("7"):
                    digits.append(content[index])
                    index += 1
                result.append(int(digits.decode("ascii"), 8))
            elif escaped == 13:
                if index < len(content) and content[index] == 10:
                    index += 1
            elif escaped != 10:
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
        if value in b"<>{}":
            raise AssertionError("hex strings/dictionaries are forbidden in pinned page content")
        if value == ord("/"):
            end = index + 1
            while end < len(content) and content[end] not in whitespace + delimiters:
                end += 1
            if end == index + 1:
                raise AssertionError("empty PDF name")
            tokens.append(content[index:end].decode("ascii"))
            index = end
            continue
        end = index
        while end < len(content) and content[end] not in whitespace + delimiters:
            end += 1
        if end == index:
            raise AssertionError(f"unparsed PDF content byte at {index}")
        raw = content[index:end]
        try:
            token: object = float(raw) if b"." in raw else int(raw)
        except ValueError:
            token = raw.decode("ascii")
        tokens.append(token)
        index = end
    return tokens


def _finite_number(value: object) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise AssertionError(f"expected numeric PDF operand, got {value!r}")
    result = float(value)
    if not math.isfinite(result):
        raise AssertionError("nonfinite PDF numeric operand")
    return result


def _decode_page(
    page: int,
    content: bytes,
    fonts: dict[str, FontInfo],
    resource_closure: tuple[int, ...],
) -> ExtractedPage:
    operands: list[object] = []
    array_markers: list[int] = []
    counts: Counter[str] = Counter()
    glyphs: list[Glyph] = []
    in_text = False
    font: FontInfo | None = None
    font_size: float | None = None
    line_x = line_y = text_x = text_y = 0.0
    position_fresh = False
    fill_color = ("gray", 0.0, 0.0, 0.0)

    def require_operands(operator: str, count: int) -> tuple[object, ...]:
        if len(operands) != count:
            raise AssertionError(f"{operator} expected {count} operands, got {operands!r}")
        result = tuple(operands)
        operands.clear()
        return result

    def show(values: list[object], operator: str) -> None:
        nonlocal text_x, position_fresh
        if not in_text or font is None or font_size is None:
            raise AssertionError(f"{operator} outside initialized text state")
        if not position_fresh:
            raise AssertionError("every pinned text-showing operation must be paired with a fresh Td")
        saw_string = False
        for item in values:
            if isinstance(item, bytes):
                saw_string = True
                for code in item:
                    if code not in font.widths or code not in font.glyph_names:
                        raise AssertionError(f"font {font.name} cannot render code {code}")
                    if font.widths[code] <= 0.0:
                        raise AssertionError(
                            f"font {font.name} code {code} has nonpositive advance width"
                        )
                    glyph_name = font.glyph_names[code]
                    if (
                        glyph_name == ".notdef"
                        or glyph_name not in font.charset
                        or glyph_name not in font.charstrings
                    ):
                        raise AssertionError(
                            f"font {font.name} code {code} lacks one operative embedded glyph"
                        )
                    decoded = font.cmap.get(code, f"⟦{font.name}:{code:02X}⟧")
                    x0, y0, x1, y1 = font.bbox
                    bbox = (
                        text_x + font_size * x0 / 1000.0,
                        text_y + font_size * y0 / 1000.0,
                        text_x + font_size * x1 / 1000.0,
                        text_y + font_size * y1 / 1000.0,
                    )
                    glyphs.append(Glyph(decoded, code, glyph_name, font.name, font_size, text_x, text_y, bbox, fill_color))
                    text_x += font_size * font.widths[code] / 1000.0
            else:
                text_x -= font_size * _finite_number(item) / 1000.0
        if not saw_string:
            raise AssertionError(f"{operator} array contains no text")
        position_fresh = False

    for token in _tokens(content):
        if token == "[":
            if array_markers:
                raise AssertionError("nested arrays are forbidden in pinned page content")
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
        if isinstance(token, (bytes, int, float)) or (isinstance(token, str) and token.startswith("/")):
            operands.append(token)
            continue
        if array_markers:
            raise AssertionError("PDF operator occurs inside an unterminated array")
        if not isinstance(token, str):
            raise AssertionError(f"unclassified PDF token {token!r}")
        counts[token] += 1
        if token == "BT":
            require_operands(token, 0)
            if in_text:
                raise AssertionError("nested BT")
            in_text = True
            font = None
            font_size = None
            line_x = line_y = text_x = text_y = 0.0
            position_fresh = False
        elif token == "ET":
            require_operands(token, 0)
            if not in_text:
                raise AssertionError("ET outside text object")
            in_text = False
            position_fresh = False
        elif token == "Tf":
            raw_name, raw_size = require_operands(token, 2)
            if not in_text or not isinstance(raw_name, str) or not raw_name.startswith("/"):
                raise AssertionError("malformed Tf")
            name = raw_name[1:]
            if name not in fonts:
                raise AssertionError(f"font {name} is absent from page resources")
            size = _finite_number(raw_size)
            if size <= 0.0:
                raise AssertionError("text font size must be positive")
            font = fonts[name]
            font_size = size
        elif token == "Td":
            raw_x, raw_y = require_operands(token, 2)
            if not in_text:
                raise AssertionError("Td outside text object")
            line_x += _finite_number(raw_x)
            line_y += _finite_number(raw_y)
            text_x, text_y = line_x, line_y
            position_fresh = True
        elif token == "TJ":
            (array,) = require_operands(token, 1)
            if not isinstance(array, list):
                raise AssertionError("TJ operand is not an array")
            show(array, token)
        elif token == "Tj":
            (raw,) = require_operands(token, 1)
            if not isinstance(raw, bytes):
                raise AssertionError("Tj operand is not a string")
            show([raw], token)
        elif token in ("'", '"'):
            raise AssertionError(f"alternate text-showing operator {token!r} is forbidden")
        elif token == "Do":
            require_operands(token, 1)
            raise AssertionError("XObject invocation is forbidden on pinned theorem pages")
        elif token in ("g", "G"):
            (raw_gray,) = require_operands(token, 1)
            gray = _finite_number(raw_gray)
            if not 0.0 <= gray <= 1.0:
                raise AssertionError("gray component outside [0,1]")
            if token == "g":
                fill_color = ("gray", gray, gray, gray)
        elif token in ("rg", "RG"):
            values = require_operands(token, 3)
            red, green, blue = (_finite_number(value) for value in values)
            if not all(0.0 <= value <= 1.0 for value in (red, green, blue)):
                raise AssertionError("RGB component outside [0,1]")
            if token == "rg":
                fill_color = ("rgb", red, green, blue)
        else:
            # Covers every path paint/clip, q/Q/cm, text-state variant, gs,
            # shading, marked/optional content, inline image, and extension.
            raise AssertionError(f"operator {token!r} is outside the pinned render profile")
    if operands or array_markers or in_text:
        raise AssertionError("unterminated operands, array, or text object")
    if dict(counts) != EXPECTED_OPERATOR_COUNTS[page]:
        raise AssertionError(f"page {page} exhaustive operator inventory mismatch: {dict(counts)}")
    if counts["Td"] != counts["TJ"]:
        raise AssertionError("each pinned TJ must have exactly one positioning Td")
    return ExtractedPage(
        page,
        "".join(glyph.text for glyph in glyphs),
        tuple(glyphs),
        MEDIA_BOX,
        tuple(sorted(counts.items())),
        resource_closure,
    )


def extract_appendix_pages(pdf: bytes) -> tuple[ExtractedPage, ...]:
    compressed = _compressed_objects(pdf)
    _audit_document_root(pdf, compressed)
    _page_tree_order(pdf, compressed)
    pages: list[ExtractedPage] = []
    for page, page_object, content_object, resource_object in PAGE_BINDINGS:
        _audit_page_envelope(pdf, page_object, content_object, resource_object)
        closure = _audit_resource_graph(pdf, compressed, resource_object)
        fonts = _font_infos(pdf, compressed, resource_object)
        pages.append(_decode_page(page, _stream_data(pdf, content_object), fonts, closure))
    return tuple(pages)
