<contribution>
ordinal: 1
transaction_id: b28dd977ae39eb77989de8e60b63f7eacd8982d2
contribution_id: fredricksen-sweet-536-certificate
author: Robert Raynor
<artifact path="problems/schur-number-6/contributions/fredricksen-sweet-536-certificate/README.md">
# Exact certificate for the published lower bound S(6) >= 536

## Claim

The committed `coloring.csv` is a complete six-coloring of
`{1, 2, ..., 536}` with no monochromatic solution to `x + y = z`, including
the case `x = y`. It therefore independently replays the published baseline
lower bound

```text
S(6) >= 536.
```

This certificate does not improve the bound. The problem's published interval
remains `536 <= S(6) <= 1836`.

## Witness encoding and exact check

`coloring.csv` is the canonical expanded encoding: it has the exact header
`integer,color`, followed by one row for every integer in increasing order,
with colors numbered 1 through 6. `published-symmetric.json` preserves the
compact form printed by the source paper. Each ordinary representative `r`
encodes both `r` and `537-r` in the same color. The exceptional pair is
recorded explicitly as `[179, 4]` and `[358, 1]`, exactly as printed.

Run from this directory with Python 3 and only the standard library:

```bash
python3 -I -B verify.py published-symmetric.json coloring.csv
```

Expected output:

```text
verified 6-coloring of 1..536: class sizes 129,86,110,77,64,70; all 71824 in-range x<=y Schur triples are nonmonochromatic
```

The checker:

1. validates the compact witness schema, `n = 536`, six nonempty color
   classes, and symmetry modulus 537;
2. rejects noncanonical, duplicate, out-of-range, or overlapping paired
   representatives and special assignments;
3. expands the compact source witness and requires exact coverage of `1..536`;
4. validates the CSV header, row count, canonical integer order, and color
   range, and requires exact agreement with the source witness; and
5. enumerates every integer triple with `1 <= x <= y` and
   `z = x + y <= 536`, rejecting a monochromatic triple. Thus `x = y` is
   included rather than silently omitted.

`verification.json` requests a replay by the repository's pinned, networkless
Python-standard-library verifier. A passing hosted attestation is evidence only
that the pinned checker accepted the pinned artifact bytes; mathematical
judgment remains separate.

## Primary-source provenance and attribution

The construction is due to Harold Fredricksen and Melvin M. Sweet:

- Harold Fredricksen and Melvin M. Sweet, “Symmetric Sum-Free Partitions and
  Lower Bounds for Schur Numbers,” *The Electronic Journal of Combinatorics*
  7 (2000), Research Paper 32, DOI
  [10.37236/1510](https://doi.org/10.37236/1510).
- [Official journal article page](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v7i1r32).
- [Official primary PDF](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v7i1r32/pdf),
  retrieved 2026-08-12, SHA-256
  `ae8541c564efd65785a0e1d2c778108d58fec4c060707d7c277dd7f3eecad259`.

Page 2 defines a symmetric partition and permits `(n+1)/3` and
`2(n+1)/3` to occupy different sets when 3 divides `n+1`. Page 6 prints the
536 construction, says that only the smaller ordinary member of each symmetric
pair is listed, and places the exceptional values 179 and 358 in sets 4 and 1,
respectively. `published-symmetric.json` is a transcription of that page,
separating those exceptions from the paired representatives. `coloring.csv`
is the deterministic full expansion.

The official PDF was independently checked both by layout-preserving text
extraction and by visual inspection of the rendered page. The construction,
the bound, and their mathematical authorship remain Fredricksen and Sweet's;
this contribution claims no originality or priority for the construction.

## Limitations

- The certificate proves only the already published lower bound `S(6) >= 536`.
- It supplies no coloring of 537 or higher and no upper-bound information.
- The PDF is not vendored. Its official URLs and exact content digest are
  recorded, while all witness bytes needed for offline replay are committed.
- The verifier establishes the encoded finite predicate; it does not explain
  how Fredricksen and Sweet found the coloring.

## Artifact authorship

The witness and mathematical construction are by Harold Fredricksen and Melvin
M. Sweet. Transcription, canonical expansion design, checker, and documentation
were produced by an OpenAI Codex research agent operating the Math Flow solver
workflow at Robert Raynor's request. Any transcription or implementation errors
in these artifacts are the agent's.

</artifact>
<artifact path="problems/schur-number-6/contributions/fredricksen-sweet-536-certificate/coloring.csv">
integer,color
1,1
2,2
3,3
4,4
5,1
6,5
7,6
8,1
9,5
10,3
11,1
12,2
13,4
14,1
15,6
16,3
17,5
18,6
19,2
20,4
21,5
22,3
23,3
24,1
25,2
26,2
27,1
28,4
29,3
30,1
31,4
32,5
33,1
34,2
35,3
36,1
37,6
38,4
39,5
40,1
41,2
42,3
43,1
44,5
45,6
46,1
47,6
48,3
49,1
50,4
51,5
52,1
53,6
54,5
55,5
56,3
57,2
58,2
59,6
60,3
61,4
62,3
63,2
64,4
65,1
66,5
67,3
68,3
69,3
70,5
71,1
72,2
73,4
74,3
75,3
76,6
77,1
78,6
79,2
80,3
81,1
82,5
83,4
84,1
85,2
86,2
87,3
88,3
89,5
90,1
91,4
92,5
93,1
94,3
95,2
96,2
97,6
98,4
99,1
100,3
101,3
102,2
103,1
104,5
105,6
106,3
107,3
108,4
109,1
110,4
111,5
112,1
113,3
114,3
115,1
116,6
117,4
118,2
119,3
120,4
121,3
122,6
123,2
124,2
125,1
126,3
127,5
128,1
129,5
130,5
131,1
132,4
133,3
134,1
135,4
136,6
137,1
138,6
139,3
140,2
141,2
142,4
143,4
144,1
145,2
146,2
147,1
148,6
149,5
150,1
151,3
152,3
153,1
154,4
155,2
156,2
157,6
158,3
159,3
160,1
161,4
162,2
163,1
164,3
165,3
166,1
167,5
168,4
169,1
170,6
171,3
172,1
173,2
174,6
175,5
176,6
177,4
178,3
179,4
180,6
181,1
182,6
183,2
184,3
185,1
186,6
187,4
188,1
189,5
190,5
191,1
192,3
193,2
194,1
195,4
196,6
197,3
198,3
199,6
200,2
201,1
202,5
203,3
204,1
205,3
206,2
207,1
208,6
209,4
210,3
211,2
212,4
213,1
214,4
215,2
216,2
217,3
218,6
219,4
220,1
221,4
222,2
223,1
224,4
225,5
226,1
227,5
228,6
229,1
230,6
231,4
232,1
233,2
234,6
235,1
236,4
237,3
238,1
239,2
240,6
241,3
242,1
243,3
244,2
245,1
246,4
247,5
248,1
249,3
250,3
251,1
252,5
253,2
254,1
255,3
256,3
257,6
258,4
259,6
260,2
261,2
262,5
263,5
264,1
265,4
266,2
267,1
268,6
269,6
270,1
271,2
272,4
273,1
274,5
275,5
276,2
277,2
278,6
279,4
280,6
281,3
282,3
283,1
284,2
285,5
286,1
287,3
288,3
289,1
290,5
291,4
292,1
293,2
294,3
295,1
296,3
297,6
298,2
299,1
300,3
301,4
302,1
303,6
304,2
305,1
306,4
307,6
308,1
309,6
310,5
311,1
312,5
313,4
314,1
315,2
316,4
317,1
318,4
319,6
320,3
321,2
322,2
323,4
324,1
325,4
326,2
327,3
328,4
329,6
330,1
331,2
332,3
333,1
334,3
335,5
336,1
337,2
338,6
339,3
340,3
341,6
342,4
343,1
344,2
345,3
346,1
347,5
348,5
349,1
350,4
351,6
352,1
353,3
354,2
355,6
356,1
357,6
358,1
359,3
360,4
361,6
362,5
363,6
364,2
365,1
366,3
367,6
368,1
369,4
370,5
371,1
372,3
373,3
374,1
375,2
376,4
377,1
378,3
379,3
380,6
381,2
382,2
383,4
384,1
385,3
386,3
387,1
388,5
389,6
390,1
391,2
392,2
393,1
394,4
395,4
396,2
397,2
398,3
399,6
400,1
401,6
402,4
403,1
404,3
405,4
406,1
407,5
408,5
409,1
410,5
411,3
412,1
413,2
414,2
415,6
416,3
417,4
418,3
419,2
420,4
421,6
422,1
423,3
424,3
425,1
426,5
427,4
428,1
429,4
430,3
431,3
432,6
433,5
434,1
435,2
436,3
437,3
438,1
439,4
440,6
441,2
442,2
443,3
444,1
445,5
446,4
447,1
448,5
449,3
450,3
451,2
452,2
453,1
454,4
455,5
456,1
457,3
458,2
459,6
460,1
461,6
462,3
463,3
464,4
465,2
466,1
467,5
468,3
469,3
470,3
471,5
472,1
473,4
474,2
475,3
476,4
477,3
478,6
479,2
480,2
481,3
482,5
483,5
484,6
485,1
486,5
487,4
488,1
489,3
490,6
491,1
492,6
493,5
494,1
495,3
496,2
497,1
498,5
499,4
500,6
501,1
502,3
503,2
504,1
505,5
506,4
507,1
508,3
509,4
510,1
511,2
512,2
513,1
514,3
515,3
516,5
517,4
518,2
519,6
520,5
521,3
522,6
523,1
524,4
525,2
526,1
527,3
528,5
529,1
530,6
531,5
532,1
533,4
534,3
535,2
536,1

</artifact>
<artifact path="problems/schur-number-6/contributions/fredricksen-sweet-536-certificate/published-symmetric.json">
{
  "schemaVersion": 1,
  "n": 536,
  "colorCount": 6,
  "encoding": "symmetric-representatives-v1",
  "symmetryModulus": 537,
  "pairedClasses": [
    [1, 5, 8, 11, 14, 24, 27, 30, 33, 36, 40, 43, 46, 49, 52, 65, 71, 77, 81, 84, 90, 93, 99, 103, 109, 112, 115, 125, 128, 131, 134, 137, 144, 147, 150, 153, 160, 163, 166, 169, 172, 181, 185, 188, 191, 194, 201, 204, 207, 213, 220, 223, 226, 229, 232, 235, 238, 242, 245, 248, 251, 254, 264, 267],
    [2, 12, 19, 25, 26, 34, 41, 57, 58, 63, 72, 79, 85, 86, 95, 96, 102, 118, 123, 124, 140, 141, 145, 146, 155, 156, 162, 173, 183, 193, 200, 206, 211, 215, 216, 222, 233, 239, 244, 253, 260, 261, 266],
    [3, 10, 16, 22, 23, 29, 35, 42, 48, 56, 60, 62, 67, 68, 69, 74, 75, 80, 87, 88, 94, 100, 101, 106, 107, 113, 114, 119, 121, 126, 133, 139, 151, 152, 158, 159, 164, 165, 171, 178, 184, 192, 197, 198, 203, 205, 210, 217, 237, 241, 243, 249, 250, 255, 256],
    [4, 13, 20, 28, 31, 38, 50, 61, 64, 73, 83, 91, 98, 108, 110, 117, 120, 132, 135, 142, 143, 154, 161, 168, 177, 187, 195, 209, 212, 214, 219, 221, 224, 231, 236, 246, 258, 265],
    [6, 9, 17, 21, 32, 39, 44, 51, 54, 55, 66, 70, 82, 89, 92, 104, 111, 127, 129, 130, 149, 167, 175, 189, 190, 202, 225, 227, 247, 252, 262, 263],
    [7, 15, 18, 37, 45, 47, 53, 59, 76, 78, 97, 105, 116, 122, 136, 138, 148, 157, 170, 174, 176, 180, 182, 186, 196, 199, 208, 218, 228, 230, 234, 240, 257, 259, 268]
  ],
  "specialAssignments": [[179, 4], [358, 1]]
}

</artifact>
<artifact path="problems/schur-number-6/contributions/fredricksen-sweet-536-certificate/verification.json">
{
  "schemaVersion": 1,
  "verifier": {
    "id": "python-stdlib-3-13-v1",
    "specDigest": "sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884"
  },
  "entrypoint": "verify.py",
  "arguments": ["published-symmetric.json", "coloring.csv"]
}

</artifact>
<artifact path="problems/schur-number-6/contributions/fredricksen-sweet-536-certificate/verify.py">
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


EXPECTED_KEYS = {
    "schemaVersion",
    "n",
    "colorCount",
    "encoding",
    "symmetryModulus",
    "pairedClasses",
    "specialAssignments",
}


def exact_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    return value


def assign(colors: dict[int, int], value: int, color: int, source: str) -> None:
    if value in colors:
        raise ValueError(f"integer {value} assigned more than once ({source})")
    colors[value] = color


def expand_symmetric(path: Path) -> tuple[int, int, dict[int, int]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != EXPECTED_KEYS:
        raise ValueError("symmetric witness has unexpected or missing fields")
    if exact_int(data["schemaVersion"], "schemaVersion") != 1:
        raise ValueError("unsupported schemaVersion")
    n = exact_int(data["n"], "n")
    color_count = exact_int(data["colorCount"], "colorCount")
    modulus = exact_int(data["symmetryModulus"], "symmetryModulus")
    if (n, color_count, modulus) != (536, 6, 537):
        raise ValueError("expected n=536, six colors, and symmetry modulus 537")
    if data["encoding"] != "symmetric-representatives-v1":
        raise ValueError("unsupported symmetric encoding")

    classes = data["pairedClasses"]
    if not isinstance(classes, list) or len(classes) != color_count:
        raise ValueError("pairedClasses must contain exactly six class lists")

    colors: dict[int, int] = {}
    for color, representatives in enumerate(classes, start=1):
        if not isinstance(representatives, list) or not representatives:
            raise ValueError(f"paired class {color} must be a nonempty list")
        if representatives != sorted(representatives):
            raise ValueError(f"paired class {color} is not in canonical order")
        for index, raw in enumerate(representatives):
            value = exact_int(raw, f"pairedClasses[{color - 1}][{index}]")
            complement = modulus - value
            if not (1 <= value < complement <= n):
                raise ValueError(f"{value} is not the smaller member of a valid pair")
            assign(colors, value, color, "paired representative")
            assign(colors, complement, color, "paired complement")

    specials = data["specialAssignments"]
    if not isinstance(specials, list) or specials != sorted(specials):
        raise ValueError("specialAssignments must be a canonically sorted list")
    for index, pair in enumerate(specials):
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError(f"specialAssignments[{index}] must be [integer, color]")
        value = exact_int(pair[0], f"specialAssignments[{index}][0]")
        color = exact_int(pair[1], f"specialAssignments[{index}][1]")
        if not (1 <= value <= n and 1 <= color <= color_count):
            raise ValueError("special assignment is outside the valid range")
        assign(colors, value, color, "special assignment")

    expected_domain = set(range(1, n + 1))
    if set(colors) != expected_domain:
        missing = sorted(expected_domain - set(colors))
        extra = sorted(set(colors) - expected_domain)
        raise ValueError(
            f"expanded witness is not a partition; missing={missing}, extra={extra}"
        )
    return n, color_count, colors


def read_canonical_csv(path: Path, n: int, color_count: int) -> dict[int, int]:
    with path.open(newline="", encoding="ascii") as stream:
        rows = list(csv.reader(stream))
    if not rows or rows[0] != ["integer", "color"]:
        raise ValueError("CSV header must be exactly integer,color")
    if len(rows) != n + 1:
        raise ValueError(f"CSV must have exactly {n} data rows")

    colors: dict[int, int] = {}
    for expected_integer, row in enumerate(rows[1:], start=1):
        if len(row) != 2 or not all(
            field.isascii() and field.isdecimal() for field in row
        ):
            raise ValueError(f"malformed CSV row {expected_integer + 1}")
        value, color = map(int, row)
        if row != [str(value), str(color)]:
            raise ValueError(f"noncanonical decimal at CSV row {expected_integer + 1}")
        if value != expected_integer:
            raise ValueError("CSV integers must appear exactly once in increasing order")
        if not (1 <= color <= color_count):
            raise ValueError(f"color outside 1..{color_count} at integer {value}")
        colors[value] = color
    return colors


def verify_sum_free(n: int, colors: dict[int, int]) -> int:
    checked = 0
    for x in range(1, n + 1):
        for y in range(x, n - x + 1):
            z = x + y
            checked += 1
            if colors[x] == colors[y] == colors[z]:
                raise ValueError(
                    f"monochromatic Schur triple: {x}+{y}={z}, color {colors[x]}"
                )
    return checked


def verify(
    symmetric_path: Path, csv_path: Path
) -> tuple[int, int, list[int], int]:
    n, color_count, expanded = expand_symmetric(symmetric_path)
    canonical = read_canonical_csv(csv_path, n, color_count)
    if canonical != expanded:
        mismatch = next(
            value for value in range(1, n + 1) if canonical[value] != expanded[value]
        )
        raise ValueError(f"CSV disagrees with symmetric source at integer {mismatch}")
    class_sizes = [
        sum(color == expected for color in canonical.values())
        for expected in range(1, color_count + 1)
    ]
    if any(size == 0 for size in class_sizes) or sum(class_sizes) != n:
        raise ValueError("CSV does not encode six nonempty color classes")
    checked = verify_sum_free(n, canonical)
    return n, color_count, class_sizes, checked


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Fredricksen-Sweet Schur-6 witness"
    )
    parser.add_argument("symmetric_witness", type=Path)
    parser.add_argument("canonical_coloring", type=Path)
    args = parser.parse_args()
    n, color_count, class_sizes, checked = verify(
        args.symmetric_witness, args.canonical_coloring
    )
    sizes = ",".join(map(str, class_sizes))
    print(
        f"verified {color_count}-coloring of 1..{n}: class sizes {sizes}; "
        f"all {checked} in-range x<=y Schur triples are nonmonochromatic"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

</artifact>
</contribution>