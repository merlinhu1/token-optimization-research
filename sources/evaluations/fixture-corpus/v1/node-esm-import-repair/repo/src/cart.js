import { normalizeSKU } from './normalize.js';

export function addLine(cart, sku, qty) {
  const key = normalizeSKU(sku);
  return { ...cart, [key]: (cart[key] ?? 0) + qty };
}
