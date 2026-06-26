import test from 'node:test';
import assert from 'node:assert/strict';
import { addLine } from '../src/cart.js';

test('normalizes SKU when adding cart line', () => {
  assert.deepEqual(addLine({}, ' abc-123 ', 2), { 'ABC-123': 2 });
});
