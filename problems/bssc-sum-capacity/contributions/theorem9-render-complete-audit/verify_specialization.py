#!/usr/bin/env python3
"""Exact source-to-specialization audit for the private-message GK bound.

The script has two deliberately independent inputs:

1. ``GK-outer.pdf`` is the exact committed official primary-source PDF.
2. ``theorem9_spec.json`` is a structured term-by-term transcription.
3. ``make_path_rows`` constructs the local L=3 rows from generic path formulas.

The verifier extracts Appendix B directly from the pinned PDF with its embedded
ToUnicode maps and compares the factorization, (19a)-(19p), and both side
conditions against the structured specification.  After setting R0=0, minima
are expanded into scalar rows and the two interval side conditions are split
into four nonnegative slacks.  The independent constructions are normalized
only with I(U,W;A)=I(W;A)+I(U;A|W) and its V analogue, then compared exactly.
No optimizer, third-party package, or network request is used.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


_EXTRACTOR_PATH = Path(__file__).resolve().with_name("pdf_source_extract.py")
_EXTRACTOR_SPEC = importlib.util.spec_from_file_location(
    "theorem9_bounded_pdf_source_extract", _EXTRACTOR_PATH
)
if _EXTRACTOR_SPEC is None or _EXTRACTOR_SPEC.loader is None:
    raise AssertionError(f"cannot load bounded PDF extractor at {_EXTRACTOR_PATH}")
_EXTRACTOR = importlib.util.module_from_spec(_EXTRACTOR_SPEC)
sys.modules[_EXTRACTOR_SPEC.name] = _EXTRACTOR
_EXTRACTOR_SPEC.loader.exec_module(_EXTRACTOR)
extract_appendix_pages = _EXTRACTOR.extract_appendix_pages
glyph_name_unicode = _EXTRACTOR.glyph_name_unicode


GROUPS = ("a", "b", "c")
KINDS = ("W", "U|W", "V|W", "UW", "VW", "X|UW", "X|VW")
OUTPUTS = ("Y", "G", "K", "Z")
MIRROR_KIND = {
    "W": "W",
    "U|W": "V|W",
    "V|W": "U|W",
    "UW": "VW",
    "VW": "UW",
    "X|UW": "X|VW",
    "X|VW": "X|UW",
}

# These sets are an independent audit of the distinct output-bearing terms in
# (19a)-(19p) and the two side conditions.  They are intentionally not read
# from theorem9_spec.json.
EXPECTED_TERM_AUDIT = {
    "Y": {"a:W", "a:U|W", "a:X|VW"},
    "Z": {"c:W", "c:V|W", "c:X|UW"},
    "G": {
        "a:W", "b:W", "a:UW", "b:UW", "a:VW", "b:VW",
        "a:U|W", "b:U|W", "b:V|W", "a:X|UW", "a:X|VW",
        "b:X|VW",
    },
    "K": {
        "b:W", "c:W", "b:UW", "c:UW", "b:VW", "c:VW",
        "b:U|W", "b:V|W", "c:V|W", "b:X|UW", "c:X|UW",
        "c:X|VW",
    },
}
EXPECTED_THEOREM_GEOMETRY_SHA256 = (
    "43e10353f3dade58020fde708193bdf3d1114df7cd84fbc54359aec0aa2bcef0"
)


Atom = tuple[str, str, str]  # group, kind, output
RawTerm = tuple[int, str, str, str]
Linear = dict[Atom, int]


@dataclass(frozen=True)
class Row:
    label: str
    r1: int
    r2: int
    terms: tuple[RawTerm, ...]


def term(coefficient: int, group: str, kind: str, output: str) -> RawTerm:
    return coefficient, group, kind, output


def add_coefficient(result: Linear, atom: Atom, coefficient: int) -> None:
    result[atom] = result.get(atom, 0) + coefficient
    if result[atom] == 0:
        del result[atom]


def normalize_terms(terms: Iterable[RawTerm]) -> Linear:
    """Normalize solely by expanding UW and VW with the chain rule."""
    result: Linear = {}
    for coefficient, group, kind, output in terms:
        if (
            not isinstance(coefficient, int)
            or coefficient == 0
            or group not in GROUPS
            or kind not in KINDS
            or output not in OUTPUTS
        ):
            raise AssertionError((coefficient, group, kind, output))
        if kind == "UW":
            add_coefficient(result, (group, "W", output), coefficient)
            add_coefficient(result, (group, "U|W", output), coefficient)
        elif kind == "VW":
            add_coefficient(result, (group, "W", output), coefficient)
            add_coefficient(result, (group, "V|W", output), coefficient)
        else:
            add_coefficient(result, (group, kind, output), coefficient)
    return result


def as_raw_terms(value: object) -> tuple[RawTerm, ...]:
    if not isinstance(value, list):
        raise AssertionError("term list must be an array")
    result: list[RawTerm] = []
    for item in value:
        if not isinstance(item, list) or len(item) != 4:
            raise AssertionError(f"invalid encoded term: {item!r}")
        coefficient, group, kind, output = item
        if not all(isinstance(x, str) for x in (group, kind, output)):
            raise AssertionError(f"invalid encoded term: {item!r}")
        result.append(term(coefficient, group, kind, output))
    normalize_terms(result)
    return tuple(result)


def canonical_atom(group: str, kind: str, output: str) -> str:
    """Render one structured information term as the PDF extractor renders it."""
    auxiliary = {
        "W": f"W{group}",
        "U|W": f"U{group}",
        "V|W": f"V{group}",
        "UW": f"U{group},W{group}",
        "VW": f"V{group},W{group}",
        "X|UW": "X",
        "X|VW": "X",
    }[kind]
    conditioning = {
        "W": "",
        "U|W": f"|W{group}",
        "V|W": f"|W{group}",
        "UW": "",
        "VW": "",
        "X|UW": f"|U{group},W{group}",
        "X|VW": f"|V{group},W{group}",
    }[kind]
    return f"I({auxiliary};{output}{conditioning})"


def canonical_sum(terms: tuple[RawTerm, ...]) -> str:
    if not terms:
        return "0"
    pieces: list[str] = []
    for index, (coefficient, group, kind, output) in enumerate(terms):
        if coefficient not in (-1, 1):
            raise AssertionError("source surface form requires unit coefficients")
        atom = canonical_atom(group, kind, output)
        if index == 0:
            pieces.append(atom if coefficient == 1 else "−" + atom)
        else:
            pieces.append(("+" if coefficient == 1 else "−") + atom)
    return "".join(pieces)


def source_equation_pieces(spec: dict[str, object]) -> dict[str, str]:
    """Generate the source-facing equation text from the structured term spec."""
    constraints = spec.get("constraints")
    if not isinstance(constraints, list):
        raise AssertionError("missing structured constraints")
    result: dict[str, str] = {}
    for constraint in constraints:
        if not isinstance(constraint, dict):
            raise AssertionError("constraint must be an object")
        labels = constraint.get("sourceLabels")
        rates = constraint.get("rateCoefficients")
        branches = constraint.get("branches")
        if (
            not isinstance(labels, list)
            or not all(isinstance(label, str) for label in labels)
            or not isinstance(rates, list)
            or len(rates) != 2
            or not isinstance(branches, list)
        ):
            raise AssertionError("invalid source-surface constraint")
        lhs = "R0" + ("+R1" if rates[0] else "") + ("+R2" if rates[1] else "")
        base = canonical_sum(as_raw_terms(constraint.get("base")))
        branch_sums: list[str] = []
        for branch in branches:
            if not isinstance(branch, dict):
                raise AssertionError("invalid source-surface branch")
            branch_sums.append(canonical_sum(as_raw_terms(branch.get("terms"))))
        has_minimum = len(branch_sums) > 1
        minimum = "min{" + ",".join(branch_sums) + "}" if has_minimum else ""
        position = constraint.get("minimumPosition")
        if len(labels) == 2:
            if position != "suffix" or not has_minimum:
                raise AssertionError("split source equation must end in a minimum")
            result[labels[0]] = f"{lhs}≤{base}"
            result[labels[1]] = "+" + minimum
        elif len(labels) == 1:
            if has_minimum and position == "suffix":
                rhs = base + "+" + minimum
            elif has_minimum and position == "prefix":
                rhs = minimum + "+" + base
            elif not has_minimum and position is None:
                rhs = base
            else:
                raise AssertionError("invalid minimum placement")
            result[labels[0]] = f"{lhs}≤{rhs}"
        else:
            raise AssertionError("source constraint must have one or two labels")
    expected_labels = [f"19{chr(ord('a') + index)}" for index in range(16)]
    if list(result) != expected_labels:
        raise AssertionError((list(result), expected_labels))
    return result


def source_factorization(spec: dict[str, object]) -> str:
    value = spec.get("factorization")
    if not isinstance(value, dict):
        raise AssertionError("missing structured factorization")
    variables = value.get("variables")
    factors = value.get("factors")
    if (
        not isinstance(variables, list)
        or not variables
        or not all(isinstance(item, str) and item for item in variables)
        or not isinstance(factors, list)
        or not factors
        or not all(isinstance(item, str) and item for item in factors)
    ):
        raise AssertionError("invalid structured factorization")
    expected_variables = [
        "Ua", "Va", "Wa", "Ub", "Vb", "Wb", "Uc", "Vc", "Wc",
        "X", "Y", "Z", "G", "K",
    ]
    expected_factors = [
        "pX", "pUa,Va,Wa|X", "pUb,Vb,Wb|X", "pUc,Vc,Wc|X",
        "TY,Z|X", "TG,K|X,Y,Z",
    ]
    if variables != expected_variables or factors != expected_factors:
        raise AssertionError("factorization does not encode the three independent auxiliary groups")
    return "p" + ",".join(variables) + "=" + "".join(factors)


def source_side_conditions(spec: dict[str, object]) -> tuple[str, str]:
    values = spec.get("sideConditions")
    if not isinstance(values, list) or len(values) != 2:
        raise AssertionError("expected two structured side conditions")
    result: list[str] = []
    for value in values:
        if not isinstance(value, dict):
            raise AssertionError("side condition must be an object")
        left = canonical_sum(as_raw_terms(value.get("left")))
        right = canonical_sum(as_raw_terms(value.get("right")))
        result.append(f"0≤{left}≤{right}")
    return result[0], result[1]


def _split_glyphs_at_character(glyphs: tuple[object, ...], index: int) -> tuple[list[object], list[object]]:
    before: list[object] = []
    after: list[object] = []
    cursor = 0
    for glyph in glyphs:
        end = cursor + len(glyph.text)
        if cursor < index < end:
            raise AssertionError("theorem boundary falls inside one visible glyph")
        (before if end <= index else after).append(glyph)
        cursor = end
    if cursor < index:
        raise AssertionError("theorem boundary lies beyond rendered page text")
    return before, after


def _boxes_overlap(left: tuple[float, ...], right: tuple[float, ...]) -> bool:
    return (
        max(left[0], right[0]) < min(left[2], right[2])
        and max(left[1], right[1]) < min(left[3], right[3])
    )


def verify_rendered_theorem(pages: tuple[object, ...], marker_index: int) -> None:
    """Prove the exact decoded theorem glyphs are the complete visible content."""
    before, theorem_page_14 = _split_glyphs_at_character(pages[0].glyphs, marker_index)
    theorem_glyphs = theorem_page_14 + list(pages[1].glyphs)
    theorem_pairs = [(14, glyph) for glyph in theorem_page_14] + [
        (15, glyph) for glyph in pages[1].glyphs
    ]
    if not theorem_page_14 or not pages[1].glyphs:
        raise AssertionError("Theorem 9 must occupy the page-14 suffix and all of page 15")

    for page in pages:
        if page.media_box != (0.0, 0.0, 612.0, 792.0):
            raise AssertionError("theorem source page does not have the pinned MediaBox/CropBox")
        print(
            f"PASS source page {page.number} exhaustive operators: "
            + ", ".join(f"{name}={count}" for name, count in page.operator_counts)
        )
        print(
            f"PASS source page {page.number} recursive resource audit: "
            f"{len(page.resource_closure)} objects, no Form/Image/XObject"
        )

    for glyph in theorem_glyphs:
        if glyph.text != glyph_name_unicode(glyph.glyph_name):
            raise AssertionError(
                f"ToUnicode/operative Type1 glyph mismatch for {glyph.font} "
                f"code {glyph.code}: {glyph.glyph_name!r} -> {glyph.text!r}"
            )
        if glyph.fill_color != ("gray", 0.0, 0.0, 0.0):
            raise AssertionError("Theorem 9 contains a non-black visible glyph")
        if glyph.font_size <= 0.0:
            raise AssertionError("Theorem 9 contains a nonpositive font size")
        x0, y0, x1, y1 = glyph.bbox
        if not (0.0 < x0 < x1 < 612.0 and 0.0 < y0 < y1 < 792.0):
            raise AssertionError(
                f"visible theorem glyph is clipped or outside the page: {glyph!r}"
            )

    # Within each unchanged baseline, stream order must be strict left-to-right
    # order.  This catches displaced runs followed by a compensating backtrack
    # even when every individual glyph remains inside the page.
    for page_number in (14, 15):
        page_glyphs = [glyph for page, glyph in theorem_pairs if page == page_number]
        for previous, current in zip(page_glyphs, page_glyphs[1:]):
            if abs(previous.y - current.y) < 1e-9 and current.x <= previous.x:
                raise AssertionError(
                    f"page {page_number} theorem reading order backtracks on one baseline"
                )

    geometry_lines: list[str] = []
    for page_number, glyph in theorem_pairs:
        escaped = glyph.text.encode("unicode_escape").decode("ascii")
        bbox_text = ",".join(f"{value:.6f}" for value in glyph.bbox)
        geometry_lines.append(
            f"{page_number}|{glyph.font}|{glyph.code:02x}|{glyph.glyph_name}|"
            f"{escaped}|{glyph.font_size:.6f}|{glyph.x:.6f}|{glyph.y:.6f}|{bbox_text}"
        )
    geometry_payload = ("\n".join(geometry_lines) + "\n").encode("ascii")
    geometry_digest = hashlib.sha256(geometry_payload).hexdigest()
    if geometry_digest != EXPECTED_THEOREM_GEOMETRY_SHA256:
        raise AssertionError(
            "reviewed theorem glyph order/layout digest mismatch: "
            f"{geometry_digest}"
        )

    # Page 14 content before APPENDIX B is the only other painting content on
    # either theorem page.  Its conservative embedded-font rectangles are
    # strictly above and disjoint from all theorem rectangles.  Since the
    # exhaustive operator profile contains no other painting, clipping, image,
    # Form, transparency, or optional-content operation, no different visible
    # content can cover, replace, or shadow the decoded theorem.
    if max(glyph.y for glyph in theorem_page_14) >= min(glyph.y for glyph in before):
        raise AssertionError("pre-Appendix and theorem baselines are not vertically separated")
    for earlier in before:
        for theorem_glyph in theorem_page_14:
            if _boxes_overlap(earlier.bbox, theorem_glyph.bbox):
                raise AssertionError("pre-Appendix visible content overlaps Theorem 9")

    bounds = (
        min(glyph.bbox[0] for glyph in theorem_glyphs),
        min(glyph.bbox[1] for glyph in theorem_glyphs),
        max(glyph.bbox[2] for glyph in theorem_glyphs),
        max(glyph.bbox[3] for glyph in theorem_glyphs),
    )
    print("PASS source catalog/page-tree order/envelopes: pages 14-15, single streams, no annotations")
    print(
        f"PASS operative Type1/ToUnicode binding and visible geometry: "
        f"{len(theorem_glyphs)} glyphs, bounds={bounds}, sha256:{geometry_digest}"
    )
    print("PASS complete-paint audit: opaque black theorem, unclipped, no alternate overlay")


def verify_source_semantics(pdf: bytes, spec: dict[str, object]) -> None:
    """Bind the complete source-facing theorem statement to the structured spec."""
    pages = extract_appendix_pages(pdf)
    if [page.number for page in pages] != [14, 15]:
        raise AssertionError("Appendix B extraction did not return PDF pages 14-15")
    appendix_marker = "APPENDIXB"
    if pages[0].text.count(appendix_marker) != 1:
        raise AssertionError("Appendix B marker is not unique on source page 14")
    marker_index = pages[0].text.index(appendix_marker)
    verify_rendered_theorem(pages, marker_index)
    theorem = pages[0].text[marker_index:] + pages[1].text
    if "⟦" in theorem or "⟧" in theorem:
        raise AssertionError("Theorem 9 source slice contains an unmapped PDF glyph")

    header = (
        "APPENDIXBGK-BOUNDTOTHEFULLCAPACITYREGION"
        "Theorem9(GK-Bound(FullVersion)).Givenabroadcastchannelcharacterizedby"
        "TY,Z|Xandanyachievableratetriple(R0,R1,R2),onecanfindsomeinputdistribution"
        "p(x)suchthatforanyauxiliarychannelTG,K|X,Y,Z,thefollowingconstraints"
        "regardingsum-ratearesatisfied:"
    )
    if not theorem.startswith(header):
        raise AssertionError("Theorem 9 title, channel premise, or quantifier header mismatch")

    cursor = len(header)
    expected_pieces = source_equation_pieces(spec)
    for label, expected in expected_pieces.items():
        marker = f"({label})"
        marker_at = theorem.find(marker, cursor)
        if marker_at < 0:
            raise AssertionError(f"source equation label {label} not found")
        actual = theorem[cursor:marker_at].removesuffix(",")
        if actual != expected:
            raise AssertionError(
                f"source equation {label} mismatch\nexpected={expected}\nactual={actual}"
            )
        print(f"PASS source PDF semantic equation ({label})")
        cursor = marker_at + len(marker)

    first_side, second_side = source_side_conditions(spec)
    expected_tail = (
        "forsomechoiceofdistributionoverthevariables"
        + source_factorization(spec)
        + "satisfying"
        + first_side
        + ","
        + second_side
        + "."
    )
    actual_tail = theorem[cursor:].strip()
    if actual_tail != expected_tail:
        raise AssertionError(
            f"source factorization/side-condition mismatch\n"
            f"expected={expected_tail}\nactual={actual_tail}"
        )
    print("PASS source PDF semantic factorization")
    print("PASS source PDF semantic side conditions (2)")


def mirror_terms(terms: tuple[RawTerm, ...]) -> tuple[RawTerm, ...]:
    group_mirror = {"a": "c", "b": "b", "c": "a"}
    output_mirror = {"Y": "Z", "G": "K", "K": "G", "Z": "Y"}
    return tuple(
        term(
            coefficient,
            group_mirror[group],
            MIRROR_KIND[kind],
            output_mirror[output],
        )
        for coefficient, group, kind, output in terms
    )


def make_path_rows() -> list[Row]:
    """Construct the L=3 private-message rows from generic path formulas."""
    rows: list[Row] = []
    length = 3

    def group(index: int) -> str:
        return GROUPS[index - 1]

    def output(index: int) -> str:
        return OUTPUTS[index]

    for middle in range(1, length + 1):
        u_walk = tuple(
            entry
            for index in range(1, middle)
            for entry in (
                term(1, group(index), "UW", output(index - 1)),
                term(-1, group(index), "UW", output(index)),
            )
        )
        uc_walk = tuple(
            entry
            for index in range(1, middle)
            for entry in (
                term(1, group(index), "U|W", output(index - 1)),
                term(-1, group(index), "U|W", output(index)),
            )
        )
        vc_walk = tuple(
            entry
            for index in range(middle + 1, length + 1)
            for entry in (
                term(1, group(index), "V|W", output(index)),
                term(-1, group(index), "V|W", output(index - 1)),
            )
        )
        v_walk = tuple(
            entry
            for index in range(middle + 1, length + 1)
            for entry in (
                term(1, group(index), "VW", output(index)),
                term(-1, group(index), "VW", output(index - 1)),
            )
        )
        rows.append(
            Row(
                f"SL({middle},U)",
                1,
                1,
                u_walk
                + (
                    term(1, group(middle), "UW", output(middle - 1)),
                    term(1, group(middle), "X|UW", output(middle)),
                )
                + vc_walk,
            )
        )
        rows.append(
            Row(
                f"SR({middle},U)",
                1,
                1,
                v_walk
                + (
                    term(1, group(middle), "VW", output(middle)),
                    term(1, group(middle), "X|VW", output(middle - 1)),
                )
                + uc_walk,
            )
        )
        if middle == length:
            rows.append(
                Row(
                    f"SL({middle},C)",
                    1,
                    1,
                    uc_walk
                    + (
                        term(1, group(middle), "U|W", output(middle - 1)),
                        term(1, group(middle), "X|UW", output(middle)),
                        term(1, group(middle), "W", output(middle)),
                    )
                    + vc_walk,
                )
            )
        if middle == 1:
            rows.append(
                Row(
                    f"SR({middle},C)",
                    1,
                    1,
                    vc_walk
                    + (
                        term(1, group(middle), "V|W", output(middle)),
                        term(1, group(middle), "X|VW", output(middle - 1)),
                        term(1, group(middle), "W", output(middle - 1)),
                    )
                    + uc_walk,
                )
            )

    r1_rows: list[Row] = []
    for stop in range(length):
        terms = tuple(
            entry
            for index in range(1, stop + 1)
            for entry in (
                term(1, group(index), "UW", output(index - 1)),
                term(-1, group(index), "UW", output(index)),
            )
        ) + (term(1, group(stop + 1), "UW", output(stop)),)
        r1_rows.append(Row(f"R1T({stop})", 1, 0, terms))
    for stop in range(length):
        terms = tuple(
            entry
            for index in range(1, stop + 1)
            for entry in (
                term(1, group(index), "U|W", output(index - 1)),
                term(-1, group(index), "U|W", output(index)),
            )
        ) + (term(1, group(stop + 1), "U|W", output(stop)),) + tuple(
            entry
            for index in range(stop + 1, length)
            for entry in (
                term(1, group(index), "W", output(index)),
                term(-1, group(index + 1), "W", output(index)),
            )
        ) + (term(1, group(length), "W", output(length)),)
        r1_rows.append(Row(f"R1A({stop})", 1, 0, terms))
    rows.extend(r1_rows)
    rows.extend(
        Row("R2" + row.label[2:], 0, 1, mirror_terms(row.terms))
        for row in r1_rows
    )

    nonnegative_y: list[Row] = []
    for stop in range(length):
        terms = (term(1, "a", "W", "Y"),) + tuple(
            entry
            for index in range(1, stop + 1)
            for entry in (
                term(1, group(index + 1), "W", output(index)),
                term(-1, group(index), "W", output(index)),
            )
        )
        nonnegative_y.append(Row(f"N_Y({stop})", 0, 0, terms))
    rows.extend(nonnegative_y)
    rows.extend(
        Row(f"N_Z({stop})", 0, 0, mirror_terms(row.terms))
        for stop, row in enumerate(nonnegative_y)
    )

    rows.extend(
        [
            Row(
                "F_Z_left",
                0,
                0,
                (term(1, "c", "X|UW", "Z"), term(-1, "c", "X|UW", "K")),
            ),
            Row(
                "F_Z_right_minus_left",
                0,
                0,
                (
                    term(1, "c", "V|W", "Z"),
                    term(-1, "c", "V|W", "K"),
                    term(-1, "c", "X|UW", "Z"),
                    term(1, "c", "X|UW", "K"),
                ),
            ),
            Row(
                "F_Y_left",
                0,
                0,
                (term(1, "a", "X|VW", "Y"), term(-1, "a", "X|VW", "G")),
            ),
            Row(
                "F_Y_right_minus_left",
                0,
                0,
                (
                    term(1, "a", "U|W", "Y"),
                    term(-1, "a", "U|W", "G"),
                    term(-1, "a", "X|VW", "Y"),
                    term(1, "a", "X|VW", "G"),
                ),
            ),
        ]
    )
    return rows


def load_source_rows(spec: dict[str, object]) -> tuple[dict[str, Row], dict[str, str]]:
    rows: dict[str, Row] = {}
    origins: dict[str, str] = {}
    labels_seen: list[str] = []
    raw_terms: list[RawTerm] = []

    constraints = spec.get("constraints")
    if not isinstance(constraints, list) or len(constraints) != 12:
        raise AssertionError("expected the 12 substantive Theorem 9 constraints")
    for constraint in constraints:
        if not isinstance(constraint, dict):
            raise AssertionError("constraint must be an object")
        source_labels = constraint.get("sourceLabels")
        rates = constraint.get("rateCoefficients")
        branches = constraint.get("branches")
        if (
            not isinstance(source_labels, list)
            or not all(isinstance(item, str) for item in source_labels)
            or not isinstance(rates, list)
            or rates not in ([0, 0], [1, 0], [0, 1], [1, 1])
            or not isinstance(branches, list)
            or not branches
        ):
            raise AssertionError(f"invalid constraint envelope: {constraint!r}")
        labels_seen.extend(source_labels)
        base = as_raw_terms(constraint.get("base"))
        raw_terms.extend(base)
        for branch_index, branch in enumerate(branches):
            if not isinstance(branch, dict) or set(branch) != {"row", "terms"}:
                raise AssertionError(f"invalid minimum branch: {branch!r}")
            label = branch["row"]
            if not isinstance(label, str) or label in rows:
                raise AssertionError(f"duplicate or invalid row label: {label!r}")
            branch_terms = as_raw_terms(branch["terms"])
            raw_terms.extend(branch_terms)
            rows[label] = Row(label, rates[0], rates[1], base + branch_terms)
            source_text = ",".join(source_labels)
            origins[label] = f"({source_text}) branch {branch_index}"

    expected_labels = [f"19{chr(ord('a') + index)}" for index in range(16)]
    if labels_seen != expected_labels:
        raise AssertionError((labels_seen, expected_labels))

    side_conditions = spec.get("sideConditions")
    if not isinstance(side_conditions, list) or len(side_conditions) != 2:
        raise AssertionError("expected exactly two side conditions")
    for side in side_conditions:
        if not isinstance(side, dict):
            raise AssertionError("side condition must be an object")
        name = side.get("name")
        left = as_raw_terms(side.get("left"))
        right = as_raw_terms(side.get("right"))
        raw_terms.extend(left)
        raw_terms.extend(right)
        side_rows = side.get("rows")
        if not isinstance(name, str) or not isinstance(side_rows, list):
            raise AssertionError("invalid side condition envelope")
        for side_row in side_rows:
            if not isinstance(side_row, dict) or set(side_row) != {"row", "operation"}:
                raise AssertionError(f"invalid side row: {side_row!r}")
            label = side_row["row"]
            operation = side_row["operation"]
            if not isinstance(label, str) or label in rows:
                raise AssertionError(f"duplicate or invalid row label: {label!r}")
            if operation == "left":
                terms = left
            elif operation == "right-minus-left":
                terms = right + tuple(
                    term(-coefficient, group, kind, output)
                    for coefficient, group, kind, output in left
                )
            else:
                raise AssertionError(f"invalid side operation: {operation!r}")
            rows[label] = Row(label, 0, 0, terms)
            origins[label] = f"{name}: {operation}"

    audit = {output: set() for output in OUTPUTS}
    for _coefficient, group, kind, output in raw_terms:
        audit[output].add(f"{group}:{kind}")
    if audit != EXPECTED_TERM_AUDIT:
        raise AssertionError((audit, EXPECTED_TERM_AUDIT))
    return rows, origins


def verify_pdf(path: Path, source: dict[str, object]) -> bytes:
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != source.get("pdfSha256"):
        raise AssertionError(
            f"source PDF digest mismatch: expected {source.get('pdfSha256')}, got {digest}"
        )
    if len(data) != source.get("pdfBytes"):
        raise AssertionError(
            f"source PDF size mismatch: expected {source.get('pdfBytes')}, got {len(data)}"
        )
    if source.get("pdfCreationDate") != "2026-01-14T01:01:59-08:00":
        raise AssertionError("source metadata creation date is not the reviewed value")
    creation = b"/CreationDate (D:20260114090159Z)"
    modified = b"/ModDate (D:20260114090159Z)"
    if data.count(creation) != 1 or data.count(modified) != 1:
        raise AssertionError("pinned PDF creation/modification metadata mismatch")
    print(f"PASS source PDF: {len(data)} bytes, sha256:{digest}")
    return data


def main() -> None:
    root = Path(__file__).resolve().parent
    spec = json.loads((root / "theorem9_spec.json").read_text(encoding="utf-8"))
    if spec.get("schemaVersion") != 1:
        raise AssertionError("unsupported theorem specification version")
    source = spec.get("source")
    if not isinstance(source, dict):
        raise AssertionError("missing source metadata")
    bundled_pdf = source.get("bundledPdf")
    if bundled_pdf != "GK-outer.pdf":
        raise AssertionError("unexpected bundled primary-source filename")
    pdf = verify_pdf(root / bundled_pdf, source)
    verify_source_semantics(pdf, spec)

    source_rows, origins = load_source_rows(spec)
    path_rows_list = make_path_rows()
    if len(path_rows_list) != 30:
        raise AssertionError(f"path construction produced {len(path_rows_list)} rows")
    path_rows = {row.label: row for row in path_rows_list}
    if len(path_rows) != 30:
        raise AssertionError("path construction contains duplicate labels")
    if set(source_rows) != set(path_rows):
        raise AssertionError(
            f"row-label mismatch: source-only={sorted(set(source_rows)-set(path_rows))}, "
            f"path-only={sorted(set(path_rows)-set(source_rows))}"
        )

    for label, source_row in source_rows.items():
        path_row = path_rows[label]
        source_value = (source_row.r1, source_row.r2, normalize_terms(source_row.terms))
        path_value = (path_row.r1, path_row.r2, normalize_terms(path_row.terms))
        if source_value != path_value:
            raise AssertionError(
                f"{label} mismatch\nsource={source_value!r}\npath={path_value!r}"
            )
        print(f"PASS {origins[label]} -> {label}")

    counts = {output: len(EXPECTED_TERM_AUDIT[output]) for output in OUTPUTS}
    print(f"PASS exhaustive single-output term audit: {counts}")
    print(
        "PASS: committed primary source, factorization, (19a)-(19p), both side "
        "conditions, and all 30 private-message rows agree exactly"
    )


if __name__ == "__main__":
    main()
