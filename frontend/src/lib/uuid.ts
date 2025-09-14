export function safeUuid(): string {
  // 1) native if available
  // @ts-expect-error some environments gate crypto
  if (typeof crypto !== "undefined" && crypto && typeof crypto.randomUUID === "function") {
    // @ts-expect-error
    return crypto.randomUUID();
  }

  // 2) RFC4122 v4 via getRandomValues (if available)
  // @ts-expect-error
  const g = (typeof crypto !== "undefined" && crypto && typeof crypto.getRandomValues === "function")
    // @ts-expect-error
    ? crypto.getRandomValues.bind(crypto)
    : null;

  if (g) {
    const bytes = new Uint8Array(16);
    g(bytes);
    // Per RFC 4122: set version and variant bits
    bytes[6] = (bytes[6] & 0x0f) | 0x40;  // version 4
    bytes[8] = (bytes[8] & 0x3f) | 0x80;  // variant 10
    const hex = Array.from(bytes, b => b.toString(16).padStart(2, "0")).join("");
    return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
  }

  // 3) last-resort fallback (not RFC-strong, but unique enough for session id)
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}
