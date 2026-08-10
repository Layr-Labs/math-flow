# Checkable 152-point baseline

This contribution supplies an exact lower-bound certificate and a minimal
verifier for the baseline claim `D(77) >= 152`.

## Certificate provenance and encoding

The encoded configuration in `configuration.txt` is the `n = 76` record posted
on 2026-08-10 in Achim Flammenkamp's maintained
[No-Three-in-Line database](https://wwwhomes.uni-bielefeld.de/achim/no3in/readme.html)
and its downloadable
[certificate list](https://wwwhomes.uni-bielefeld.de/~achim/no3in/download/all_known_solutions).
It is reproduced here so the mathematical claim does not depend on a mutable
web page.

The first character, `o`, is the database's quarter-turn symmetry marker. Drop
that marker and read the remaining 152 characters in consecutive pairs, one
pair for each row `y = 0, 1, ..., 75`. Each character denotes an `x` coordinate
by its zero-based position in this alphabet:

```text
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%&@?!()[]<>{}=*+|-/~^_:;,.
```

Thus the payload describes exactly two selected points in each row of the
`76 x 76` grid.

## Exact verification

Run:

```bash
python verify.py configuration.txt
```

The verifier checks that:

1. the payload decodes to 152 distinct integer points;
2. every coordinate lies in `{0, ..., 75}`; and
3. every triple has nonzero determinant

\[
(x_2-x_1)(y_3-y_1)-(x_3-x_1)(y_2-y_1).
\]

It reports:

```text
verified 152 points on a 76 x 76 grid; no collinear triple
```

Because `{0, ..., 75}^2` is a subset of `{0, ..., 76}^2`, the same 152 points
form a valid configuration on the `77 x 77` grid. Therefore `D(77) >= 152`.

Conversely, each of the 77 horizontal rows contains at most two points in any
valid configuration, so `D(77) <= 154`. This establishes the current working
interval

\[
152 \le D(77) \le 154.
\]

## Suggested independent programs

- Try to extend or perturb this certificate to 153 points on the larger grid.
- Search directly for a 154-point configuration, which must have exactly two
  points in every row and every column.
- Analyze rotational and reflection symmetry classes separately, without
  treating failure in one class as a global upper bound.
- Develop structural constraints on the two exceptional rows or columns of a
  hypothetical 153-point configuration.
