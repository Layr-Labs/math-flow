function findUnescaped(text, delimiter, start) {
  let cursor = start;
  while (cursor < text.length) {
    const found = text.indexOf(delimiter, cursor);
    if (found < 0) return -1;

    let backslashes = 0;
    for (let index = found - 1; index >= 0 && text[index] === "\\"; index -= 1) {
      backslashes += 1;
    }
    if (backslashes % 2 === 0) return found;
    cursor = found + delimiter.length;
  }
  return -1;
}

function isEscapedAt(text, index) {
  let backslashes = 0;
  for (let cursor = index - 1; cursor >= 0 && text[cursor] === "\\"; cursor -= 1) {
    backslashes += 1;
  }
  return backslashes % 2 === 1;
}

function skipCodeSpan(value, cursor) {
  if (value[cursor] !== "`") return cursor;
  let runLength = 1;
  while (value[cursor + runLength] === "`") runLength += 1;
  const delimiter = "`".repeat(runLength);
  const closeAt = value.indexOf(delimiter, cursor + runLength);
  return closeAt < 0 ? value.length : closeAt + runLength;
}

function splitDelimitedMath(value, delimiters) {
  const segments = [];
  let textStart = 0;
  let cursor = 0;

  while (cursor < value.length) {
    if (value[cursor] === "`") {
      cursor = skipCodeSpan(value, cursor);
      continue;
    }
    const delimiter = delimiters.find(({ open }) => value.startsWith(open, cursor) && !isEscapedAt(value, cursor));
    if (!delimiter) {
      cursor += 1;
      continue;
    }

    const closeAt = findUnescaped(value, delimiter.close, cursor + delimiter.open.length);
    if (closeAt < 0) {
      cursor += delimiter.open.length;
      continue;
    }

    if (cursor > textStart) segments.push({ type: "text", value: value.slice(textStart, cursor) });
    segments.push({
      type: "math",
      value: value.slice(cursor + delimiter.open.length, closeAt),
    });
    cursor = closeAt + delimiter.close.length;
    textStart = cursor;
  }

  if (textStart < value.length) segments.push({ type: "text", value: value.slice(textStart) });
  if (!segments.length) segments.push({ type: "text", value });
  return segments;
}

export function splitDisplayMath(value) {
  return splitDelimitedMath(value, [
    { open: "\\[", close: "\\]" },
    { open: "$$", close: "$$" },
  ]);
}

export function splitInlineMath(value) {
  return splitDelimitedMath(value, [
    { open: "\\(", close: "\\)" },
    { open: "$", close: "$" },
  ]);
}
