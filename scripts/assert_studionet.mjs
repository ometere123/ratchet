#!/usr/bin/env node
// Refuse every deployment unless the exact stable StudioNet RPC confirms 61999.
const endpoint = 'https://studio.genlayer.com/api';
const expected = 61999;
let response;
try {
  const r = await fetch(endpoint, {
    method: 'POST',
    headers: {'content-type':'application/json'},
    body: JSON.stringify({jsonrpc:'2.0',id:17,method:'eth_chainId',params:[]}),
    signal: AbortSignal.timeout(15000),
  });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  response = await r.json();
} catch (e) {
  console.error('REFUSING DEPLOYMENT: cannot confirm stable RPC chain ID:', e.message);
  process.exit(1);
}
if (response.error || typeof response.result !== 'string') {
  console.error('REFUSING DEPLOYMENT: eth_chainId absent/unavailable:', JSON.stringify(response));
  process.exit(1);
}
const actual = Number.parseInt(response.result, 16);
if (actual !== expected) {
  console.error(`REFUSING DEPLOYMENT: wrong chain ID ${actual}; expected ${expected} (${endpoint}).`);
  process.exit(1);
}
console.log(`Confirmed exact stable StudioNet: chain ${actual}, RPC ${endpoint}`);
