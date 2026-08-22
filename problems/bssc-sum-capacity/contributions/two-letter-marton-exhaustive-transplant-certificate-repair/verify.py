#!/usr/bin/env python3
"""Exhaustively certify two fixed rational BSSC transplant families.

The checker uses only the Python standard library.  It verifies the vendored
source certificate, constructs outward entropy intervals for exact rational
masses, and evaluates all 2 * 4^9 deterministic maps.  Entropy-cell intervals
are quantized outward at 10^-18 bit resolution, so the final global upper
bound is rigorous despite the compact integer scan.
"""

from __future__ import annotations

import hashlib
import json
import time
from array import array
from dataclasses import dataclass
from decimal import (
    Context,
    Decimal,
    ROUND_CEILING,
    ROUND_FLOOR,
    ROUND_HALF_EVEN,
    getcontext,
)
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source_certificate.json"
SOURCE_SHA256 = (
    "45502b2e7a694ae2d1beaee3e19249d63d9efe39b6405daa42ada0e1cbb846d6"
)
SOURCE_BYTES = 17683
DEPENDENCY = "88a1004f309460f3ec1cacdae88d30f88559f9bc"
CLAIM_KEY = (
    "bssc-sum-capacity/two-letter-marton-exhaustive-transplant-certificate-repair"
)
CORRECTED_TRANSACTION = "1075dd02e8f83427a17b3f9f1391dfbb9e6d0a82"
CORRECTED_JUDGMENT = (
    "sha256:4f75d510a3f080724aafefb35accddd481e6a02b32c24e10414c341c9b62eddf"
)
DECLARED_REFERENCES = (DEPENDENCY, CORRECTED_TRANSACTION)
THRESHOLD_LOWER = Decimal(
    "0.7232857688439092313268831563011740144159620214477211104074274596056014"
)
THRESHOLD_UPPER = Decimal(
    "0.7232857688439092313268831563011740144159620214477211104074274596056016"
)
EXPECTED_MAP = (1, 0, 3, 0, 0, 2, 3, 2, 3)
EXPECTED_MAP_ID = 243761
EXPECTED_UPPER_ARGMAX_MAP = (2, 0, 3, 0, 0, 1, 3, 1, 3)
EXPECTED_SCAN_RESULTS = (
    (6, 1_090_205_773_997_791_666, 226_354, EXPECTED_UPPER_ARGMAX_MAP),
    (7, 1_090_380_802_264_441_243, 226_354, EXPECTED_UPPER_ARGMAX_MAP),
)
EXPECTED_CANDIDATE_INTERVAL = (
    1_090_380_802_264_441_073,
    1_090_380_802_264_441_243,
)
EXPECTED_ENDPOINT_INTERVALS = (
    (546_525_784_279_605_164, 546_525_784_279_605_249),
    (543_855_017_984_835_909, 543_855_017_984_835_994),
)
EXPECTED_GLOBAL_INTERVAL = EXPECTED_CANDIDATE_INTERVAL
EXPECTED_THRESHOLD_FLOOR = 1_446_571_537_687_818_462
EXPECTED_ENTROPY_CELLS = 24_610
EXPECTED_ENTROPY_TABLES = 42
EXPECTED_PROJECTION_PATTERNS = 13

SOURCE_DENOMINATOR = 1_000_000_000_000
CHANNEL_DENOMINATOR = 4
MASS_DENOMINATOR = SOURCE_DENOMINATOR * CHANNEL_DENOMINATOR
MAPS_PER_LAW = 4**9
SCALE = 10**18
FULL_ACTIVE = tuple(range(9))

# Transition numerators over the common denominator four.  Rows and columns
# use the super-symbol order 00, 01, 10, 11.
KERNEL_Y = (
    (1, 1, 1, 1),
    (0, 2, 0, 2),
    (0, 0, 2, 2),
    (0, 0, 0, 4),
)
KERNEL_Z = (
    (4, 0, 0, 0),
    (2, 2, 0, 0),
    (2, 0, 2, 0),
    (1, 1, 1, 1),
)
KERNELS = {"Y": KERNEL_Y, "Z": KERNEL_Z}

getcontext().prec = 80
D = Decimal
NEAR = Context(prec=50, rounding=ROUND_HALF_EVEN)
DOWN = Context(prec=50, rounding=ROUND_FLOOR)
UP = Context(prec=50, rounding=ROUND_CEILING)
LN2_NEAR = NEAR.ln(D(2))
LN2_LOWER = LN2_NEAR.next_minus(context=NEAR)
LN2_UPPER = LN2_NEAR.next_plus(context=NEAR)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def scaled_floor(value: Decimal) -> int:
    scaled = DOWN.multiply(value, D(SCALE))
    return int(scaled.to_integral_value(rounding=ROUND_FLOOR))


def scaled_ceiling(value: Decimal) -> int:
    scaled = UP.multiply(value, D(SCALE))
    return int(scaled.to_integral_value(rounding=ROUND_CEILING))


ENTROPY_CACHE: dict[int, tuple[int, int]] = {
    0: (0, 0),
    MASS_DENOMINATOR: (0, 0),
}


def entropy_cell(numerator: int) -> tuple[int, int]:
    """Outward scaled interval for -p log_2 p, p=numerator/MASS_DENOMINATOR."""

    cached = ENTROPY_CACHE.get(numerator)
    if cached is not None:
        return cached
    need(0 < numerator < MASS_DENOMINATOR, "cell probability range")

    p_lower = DOWN.divide(D(numerator), D(MASS_DENOMINATOR))
    p_upper = UP.divide(D(numerator), D(MASS_DENOMINATOR))
    need(p_lower == p_upper, "terminating exact cell probability")
    p = p_lower

    log_near = NEAR.ln(p)
    log_lower = log_near.next_minus(context=NEAR)
    log_upper = log_near.next_plus(context=NEAR)
    negative_log_lower = -log_upper
    negative_log_upper = -log_lower

    h_lower = DOWN.divide(
        DOWN.multiply(p, negative_log_lower),
        LN2_UPPER,
    )
    h_upper = UP.divide(
        UP.multiply(p, negative_log_upper),
        LN2_LOWER,
    )
    result = (scaled_floor(h_lower), scaled_ceiling(h_upper))
    need(0 <= result[0] <= result[1], "outward entropy cell")
    ENTROPY_CACHE[numerator] = result
    return result


@dataclass(frozen=True)
class EntropyTable:
    active: tuple[int, ...]
    lower: array
    upper: array


TABLE_CACHE: dict[tuple[tuple[int, ...], str], EntropyTable] = {}
PROJECTION_CACHE: dict[tuple[int, ...], array | None] = {FULL_ACTIVE: None}


def entropy_table(weights: tuple[int, ...], receiver: str) -> EntropyTable:
    """Entropy of one condition slice for every assignment of active labels."""

    key = (weights, receiver)
    cached = TABLE_CACHE.get(key)
    if cached is not None:
        return cached
    need(len(weights) == 9, "nine source labels")
    need(all(value >= 0 for value in weights), "nonnegative exact weights")
    kernel = KERNELS[receiver]
    active = tuple(index for index, value in enumerate(weights) if value)
    count = 1 << (2 * len(active))
    lower = array("q")
    upper = array("q")
    append_lower = lower.append
    append_upper = upper.append

    for code in range(count):
        output = [0, 0, 0, 0]
        for local_index, source_label in enumerate(active):
            mapped_input = (code >> (2 * local_index)) & 3
            mass = weights[source_label]
            row = kernel[mapped_input]
            output[0] += mass * row[0]
            output[1] += mass * row[1]
            output[2] += mass * row[2]
            output[3] += mass * row[3]
        need(
            sum(output) == CHANNEL_DENOMINATOR * sum(weights),
            "channel mass preservation",
        )
        cell_bounds = [entropy_cell(value) for value in output]
        append_lower(sum(item[0] for item in cell_bounds))
        append_upper(sum(item[1] for item in cell_bounds))

    table = EntropyTable(active, lower, upper)
    TABLE_CACHE[key] = table
    return table


def projection(active: tuple[int, ...]) -> array | None:
    """Map each nine-digit map ID to the local active-digit table index."""

    if active in PROJECTION_CACHE:
        return PROJECTION_CACHE[active]
    result = array("I")
    append = result.append
    for map_id in range(MAPS_PER_LAW):
        local = 0
        for local_index, source_label in enumerate(active):
            digit = (map_id >> (2 * source_label)) & 3
            local |= digit << (2 * local_index)
        append(local)
    PROJECTION_CACHE[active] = result
    return result


def local_index(map_id: int, active: tuple[int, ...]) -> int:
    if active == FULL_ACTIVE:
        return map_id
    result = 0
    for local_position, source_label in enumerate(active):
        digit = (map_id >> (2 * source_label)) & 3
        result |= digit << (2 * local_position)
    return result


def table_interval(table: EntropyTable, map_id: int) -> tuple[int, int]:
    index = local_index(map_id, table.active)
    return table.lower[index], table.upper[index]


def sum_interval(
    tables: tuple[EntropyTable, ...],
    map_id: int,
) -> tuple[int, int]:
    lower = 0
    upper = 0
    for table in tables:
        item_lower, item_upper = table_interval(table, map_id)
        lower += item_lower
        upper += item_upper
    return lower, upper


@dataclass(frozen=True)
class RecordTables:
    row: int
    x_y: EntropyTable
    x_z: EntropyTable
    wx_y: tuple[EntropyTable, ...]
    wx_z: tuple[EntropyTable, ...]
    wux_y: tuple[EntropyTable, ...]
    wvx_z: tuple[EntropyTable, ...]
    constant_lower: int
    constant_upper: int

    @property
    def positive(self) -> tuple[EntropyTable, ...]:
        return (self.x_y, self.x_z, *self.wx_y, *self.wx_z)

    @property
    def negative(self) -> tuple[EntropyTable, ...]:
        return (*self.wux_y, *self.wvx_z)


def build_record_tables(record: dict) -> RecordTables:
    need(record["shape"] == [2, 4, 4, 9], "source record shape")
    need(record["axis_order"] == ["W", "U", "V", "X1X2"], "axis order")
    need(
        record["input_pair_order"]
        == ["00", "01", "02", "10", "11", "12", "20", "21", "22"],
        "source-label order",
    )
    denominator = int(record["probability_denominator"])
    need(denominator == SOURCE_DENOMINATOR, "source denominator")
    flat = [int(value) for value in record["probability_numerators"]]
    need(len(flat) == 2 * 4 * 4 * 9, "complete source law")
    need(all(value >= 0 for value in flat), "source nonnegativity")
    need(sum(flat) == denominator, "exact source simplex")

    def at(w: int, u: int, v: int, source_label: int) -> int:
        return flat[((w * 4 + u) * 4 + v) * 9 + source_label]

    x = tuple(
        sum(at(w, u, v, source_label)
            for w in range(2) for u in range(4) for v in range(4))
        for source_label in range(9)
    )
    wx = tuple(
        tuple(
            sum(at(w, u, v, source_label)
                for u in range(4) for v in range(4))
            for source_label in range(9)
        )
        for w in range(2)
    )
    wux = tuple(
        tuple(
            sum(at(w, u, v, source_label) for v in range(4))
            for source_label in range(9)
        )
        for w in range(2)
        for u in range(4)
    )
    wvx = tuple(
        tuple(
            sum(at(w, u, v, source_label) for u in range(4))
            for source_label in range(9)
        )
        for w in range(2)
        for v in range(4)
    )
    wuv = tuple(
        sum(at(w, u, v, source_label) for source_label in range(9))
        for w in range(2)
        for u in range(4)
        for v in range(4)
    )

    constant_cells = [
        entropy_cell(CHANNEL_DENOMINATOR * value) for value in wuv
    ]
    constant_lower = sum(item[0] for item in constant_cells)
    constant_upper = sum(item[1] for item in constant_cells)

    return RecordTables(
        row=int(record["row_index"]),
        x_y=entropy_table(x, "Y"),
        x_z=entropy_table(x, "Z"),
        wx_y=tuple(entropy_table(weights, "Y") for weights in wx),
        wx_z=tuple(entropy_table(weights, "Z") for weights in wx),
        wux_y=tuple(
            entropy_table(weights, "Y") for weights in wux if any(weights)
        ),
        wvx_z=tuple(
            entropy_table(weights, "Z") for weights in wvx if any(weights)
        ),
        constant_lower=constant_lower,
        constant_upper=constant_upper,
    )


def objective_interval(tables: RecordTables, map_id: int) -> tuple[int, int]:
    """Interval for twice L_{1/2}, scaled by SCALE."""

    positive_lower, positive_upper = sum_interval(tables.positive, map_id)
    negative_lower, negative_upper = sum_interval(tables.negative, map_id)
    lower = (
        2 * tables.constant_lower
        + positive_lower
        - 2 * negative_upper
    )
    upper = (
        2 * tables.constant_upper
        + positive_upper
        - 2 * negative_lower
    )
    need(lower <= upper, "objective interval orientation")
    return lower, upper


def endpoint_intervals(
    tables: RecordTables,
    map_id: int,
) -> tuple[tuple[int, int], tuple[int, int]]:
    """Intervals for the common-Y and common-Z Marton endpoints."""

    negative_lower, negative_upper = sum_interval(tables.negative, map_id)
    y_positive_lower, y_positive_upper = sum_interval(
        (tables.x_y, *tables.wx_z),
        map_id,
    )
    z_positive_lower, z_positive_upper = sum_interval(
        (tables.x_z, *tables.wx_y),
        map_id,
    )
    endpoint_y = (
        tables.constant_lower + y_positive_lower - negative_upper,
        tables.constant_upper + y_positive_upper - negative_lower,
    )
    endpoint_z = (
        tables.constant_lower + z_positive_lower - negative_upper,
        tables.constant_upper + z_positive_upper - negative_lower,
    )
    return endpoint_y, endpoint_z


def attached(
    tables: tuple[EntropyTable, ...],
    use_upper: bool,
) -> list[tuple[array, array | None]]:
    result = []
    for table in tables:
        values = table.upper if use_upper else table.lower
        result.append((values, projection(table.active)))
    return result


def exhaustive_upper(tables: RecordTables) -> tuple[int, int]:
    """Return the largest outward upper bound and one attaining map ID."""

    positive = attached(tables.positive, use_upper=True)
    negative = attached(tables.negative, use_upper=False)
    constant = 2 * tables.constant_upper
    maximum = -(1 << 62)
    argmax = -1
    for map_id in range(MAPS_PER_LAW):
        value = constant
        for values, indices in positive:
            value += values[map_id if indices is None else indices[map_id]]
        for values, indices in negative:
            value -= 2 * values[
                map_id if indices is None else indices[map_id]
            ]
        if value > maximum:
            maximum = value
            argmax = map_id
    need(argmax >= 0, "exhaustive map coverage")
    return maximum, argmax


def decode_map(map_id: int) -> tuple[int, ...]:
    return tuple((map_id >> (2 * source_label)) & 3 for source_label in range(9))


def encode_map(mapping: tuple[int, ...]) -> int:
    need(len(mapping) == 9 and all(0 <= digit < 4 for digit in mapping),
         "map digits")
    return sum(digit << (2 * index) for index, digit in enumerate(mapping))


def scaled_decimal(value: int, denominator_factor: int = 1) -> Decimal:
    return D(value) / D(denominator_factor * SCALE)


def check_metadata() -> None:
    claims = load_json(ROOT / "claims.json")
    need(claims.get("schemaVersion") == 1, "claims schema")
    payload = claims.get("claims")
    need(isinstance(payload, list) and len(payload) == 1, "single claim")
    claim = payload[0]
    need(claim.get("claimKey") == CLAIM_KEY, "claim key")
    need(
        claim.get("dependencyTransactionIds") == list(DECLARED_REFERENCES),
        "ordered threshold and corrective references",
    )
    statement = claim.get("statement", "")
    for phrase in (
        "2 * 4^9 = 524,288",
        "243761",
        "Outward",
        "[0.5451904011322205365, 0.5451904011322206215]",
        "strictly below 2 L_RTD",
        "fixed-law deterministic-map family only",
        "No value within that enclosure is asserted to greater precision",
        "corrective/provenance reference rather than a mathematical premise",
        CORRECTED_TRANSACTION,
    ):
        need(phrase in statement, f"claim scope token: {phrase}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for phrase in (
        CORRECTED_TRANSACTION,
        CORRECTED_JUDGMENT,
        "does not assert or rely on the earlier purported independent",
    ):
        need(phrase in readme, f"corrective provenance token: {phrase}")

    verification = load_json(ROOT / "verification.json")
    need(verification.get("schemaVersion") == 1, "verification schema")
    need(verification.get("entrypoint") == "verify.py", "entrypoint")
    need(verification.get("arguments") == [], "no arguments")


def check_source() -> list[dict]:
    need(SOURCE.stat().st_size == SOURCE_BYTES, "source byte length")
    need(sha256(SOURCE) == SOURCE_SHA256, "pinned source SHA-256")
    source = load_json(SOURCE)
    need(source.get("schema_version") == 2, "source schema")
    records = source.get("winning_schemes")
    need(isinstance(records, list) and len(records) == 2, "two source laws")
    need([int(record["row_index"]) for record in records] == [6, 7],
         "source rows 6 and 7")
    return records


def main() -> None:
    started = time.monotonic()
    check_metadata()
    records = check_source()
    need(encode_map(EXPECTED_MAP) == EXPECTED_MAP_ID, "base-four map ID")

    tables = [build_record_tables(record) for record in records]
    need([item.row for item in tables] == [6, 7], "record-table order")
    scan_results = [exhaustive_upper(item) for item in tables]
    evaluations = len(tables) * MAPS_PER_LAW
    need(evaluations == 524_288, "exhaustive evaluation count")

    row7 = tables[1]
    candidate = objective_interval(row7, EXPECTED_MAP_ID)
    endpoints = endpoint_intervals(row7, EXPECTED_MAP_ID)
    observed_scan_results = tuple(
        (item.row, upper, argmax, decode_map(argmax))
        for item, (upper, argmax) in zip(tables, scan_results)
    )
    need(observed_scan_results == EXPECTED_SCAN_RESULTS,
         "exact row maxima and upper-argmax maps")
    need(candidate == EXPECTED_CANDIDATE_INTERVAL,
         "exact row-7 witness interval")
    need(endpoints == EXPECTED_ENDPOINT_INTERVALS,
         "exact row-7 witness endpoint intervals")

    global_upper = max(result[0] for result in scan_results)
    maximum_interval = (candidate[0], global_upper)
    need(maximum_interval[0] <= maximum_interval[1],
         "global maximum enclosure")
    need(maximum_interval == EXPECTED_GLOBAL_INTERVAL,
         "exact two-law global interval")
    need(len(ENTROPY_CACHE) == EXPECTED_ENTROPY_CELLS,
         "exact entropy-cell coverage")
    need(len(TABLE_CACHE) == EXPECTED_ENTROPY_TABLES,
         "exact entropy-table coverage")
    need(len(PROJECTION_CACHE) == EXPECTED_PROJECTION_PATTERNS,
         "exact projection-pattern coverage")
    threshold_floor = int(
        (D(2 * SCALE) * THRESHOLD_LOWER).to_integral_value(
            rounding=ROUND_FLOOR
        )
    )
    need(threshold_floor == EXPECTED_THRESHOLD_FLOOR,
         "exact twice-RTD comparison floor")
    need(global_upper < threshold_floor, "strictly below directed RTD lower")
    need(THRESHOLD_LOWER < THRESHOLD_UPPER, "threshold interval orientation")

    print("PASS: repaired exhaustive directed two-law BSSC transplant certificate")
    print("source sha256:", SOURCE_SHA256)
    print("maps per law:", MAPS_PER_LAW)
    print("total law-map evaluations:", evaluations)
    print("locked scaled scan results:", observed_scan_results)
    print("locked scaled witness interval:", candidate)
    print("locked scaled endpoint intervals:", endpoints)
    print("locked scaled RTD comparison floor:", threshold_floor)
    for item, (upper, argmax) in zip(tables, scan_results):
        print(
            "row",
            item.row,
            "maximum upper bits:",
            scaled_decimal(upper, 2),
            "upper-argmax map id:",
            argmax,
            "map:",
            decode_map(argmax),
        )
    print(
        "row 7 candidate Lhalf interval bits:",
        scaled_decimal(candidate[0], 2),
        scaled_decimal(candidate[1], 2),
    )
    print(
        "row 7 candidate endpoint intervals bits:",
        (scaled_decimal(endpoints[0][0]), scaled_decimal(endpoints[0][1])),
        (scaled_decimal(endpoints[1][0]), scaled_decimal(endpoints[1][1])),
    )
    print(
        "two-law global maximum interval bits:",
        scaled_decimal(maximum_interval[0], 2),
        scaled_decimal(maximum_interval[1], 2),
    )
    print("directed RTD lower bits:", THRESHOLD_LOWER)
    print("distinct entropy cells:", len(ENTROPY_CACHE))
    print("entropy tables:", len(TABLE_CACHE))
    print("projection patterns:", len(PROJECTION_CACHE))
    print("elapsed seconds:", format(time.monotonic() - started, ".3f"))


if __name__ == "__main__":
    main()
