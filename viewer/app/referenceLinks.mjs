const REFERENCE_PATTERN = /(?:sha256:)?[a-f0-9]{7,64}/gi;

/**
 * @typedef {{ kind: "transaction" | "judgment", id: string, text: string }} ViewerReference
 */

function normalized(value) {
  return value.toLowerCase().replace(/^sha256:/, "");
}

/**
 * Build a reference resolver from artifacts that the selected state can open.
 * A prefix must contain at least seven hexadecimal characters and identify one
 * artifact uniquely. SHA-256-prefixed text is restricted to SHA-256 IDs.
 *
 * @param {Array<{ transactionId: string }>} transactions
 * @param {Array<{ judgmentId: string }>} judgments
 */
export function createViewerReferenceResolver(transactions, judgments) {
  const targets = [
    ...transactions.map((item) => ({
      kind: /** @type {const} */ ("transaction"),
      id: item.transactionId,
      normalizedId: normalized(item.transactionId),
      sha256: item.transactionId.toLowerCase().startsWith("sha256:"),
    })),
    ...judgments.map((item) => ({
      kind: /** @type {const} */ ("judgment"),
      id: item.judgmentId,
      normalizedId: normalized(item.judgmentId),
      sha256: item.judgmentId.toLowerCase().startsWith("sha256:"),
    })),
  ];

  /** @param {string} value @returns {ViewerReference | null} */
  function resolve(value) {
    const lower = value.toLowerCase();
    const candidate = normalized(lower);
    if (!/^[a-f0-9]{7,64}$/.test(candidate)) return null;
    const requiresSha256 = lower.startsWith("sha256:");
    const matches = targets.filter((target) =>
      (!requiresSha256 || target.sha256) && target.normalizedId.startsWith(candidate),
    );
    if (matches.length !== 1) return null;
    return { kind: matches[0].kind, id: matches[0].id, text: value };
  }

  /** @param {string} value @returns {Array<string | ViewerReference>} */
  function split(value) {
    const parts = [];
    let position = 0;
    for (const match of value.matchAll(REFERENCE_PATTERN)) {
      const start = match.index;
      const end = start + match[0].length;
      const before = start > 0 ? value[start - 1] : "";
      const after = end < value.length ? value[end] : "";
      if (/[a-f0-9]/i.test(before) || /[a-f0-9]/i.test(after)) continue;
      if (start > position) parts.push(value.slice(position, start));
      const reference = resolve(match[0]);
      parts.push(reference ?? match[0]);
      position = end;
    }
    if (position < value.length) parts.push(value.slice(position));
    return parts.length ? parts : [value];
  }

  return { resolve, split };
}
