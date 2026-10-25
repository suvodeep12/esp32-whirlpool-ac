// Usage: bun run tools/check-peer-magicool.ts <local irtxrx checkout at pinned SHA>
// Checkout: b23013a75c0e9eec9150ebd08b2d388f7d1d3337. No npm install required.
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import assert from 'node:assert/strict';

assert(process.argv[2], 'Supply the path to the inspected peer checkout');
const peer = await import(pathToFileURL(resolve(process.argv[2], 'src/protocols/whirlpool_magicool.ts')).href);
const reverse = (n: number) => Number.parseInt(n.toString(2).padStart(8, '0').split('').reverse().join(''), 2);
const fixtures = new URL('../firmware/ir-receiver/captures/', import.meta.url);
const captures = JSON.parse(readFileSync(new URL('repeat-analysis.json', fixtures), 'utf8'));
const timings = [...readFileSync(new URL('repeat.txt', fixtures), 'utf8').matchAll(/rawData\[\d+\] = \{([^}]+)\}/g)]
  .map(m => m[1].split(',').map(x => Number(x.trim())));
assert.equal(timings.length, captures.length);
const results = captures.map((capture: any, i: number) => {
  if (!capture.checksum_valid) return { capture: capture.capture, incomplete: true,
    decoderAccepted: peer.decodeWhirlpoolMagicool(timings[i]) !== null };
  const lsb = Uint8Array.from(capture.msb_bytes.split(' ').map((b: string) => reverse(Number.parseInt(b, 16))));
  const built = peer.buildWhirlpoolMagicoolRaw({temp: capture.temperature_candidate,
    power: true, mode: 3, fan: 0, swing: 7, light: true, remoteState: 0});
  assert.deepEqual(built, lsb);
  const ideal = [3370, 1365];
  for (const byte of lsb) for (let bit = 0; bit < 8; bit++) ideal.push(580, byte & (1 << bit) ? 1003 : 250);
  ideal.push(600);
  assert.equal(peer.decodeWhirlpoolMagicool(ideal)?.temp, capture.temperature_candidate);
  return {capture: capture.capture, temp: capture.temperature_candidate, bytesMatch: true,
    idealDecoderAccepted: true, measuredDecoderAccepted: peer.decodeWhirlpoolMagicool(timings[i]) !== null};
});
console.log(JSON.stringify(results, null, 2));
