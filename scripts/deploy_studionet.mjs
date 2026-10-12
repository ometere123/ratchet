#!/usr/bin/env node
/** Cross-platform guarded deployment; always invokes a repository-local CLI. */
import {spawnSync} from 'node:child_process';
import {readFileSync, existsSync} from 'node:fs';
import {resolve} from 'node:path';
import readline from 'node:readline/promises';
import {stdin as input, stdout as output} from 'node:process';
const root = resolve(import.meta.dirname, '..');
const cli = resolve(root, 'node_modules', '.bin', process.platform === 'win32' ? 'genlayer.cmd':'genlayer');
const rpc = 'https://studio.genlayer.com/api';
function run(args) {
  const proc = spawnSync(cli,args,{cwd:root,encoding:'utf8',stdio:'inherit',shell:process.platform==='win32'});
  if(proc.status!==0) throw new Error(`Local GenLayer CLI command failed: ${args.join(' ')}`);
}
async function assertChain() {
  const response=await fetch(rpc,{method:'POST',headers:{'content-type':'application/json'},
    body:JSON.stringify({jsonrpc:'2.0',id:22,method:'eth_chainId',params:[]}),
    signal:AbortSignal.timeout(15000)});
  if(!response.ok) throw new Error(`RPC HTTP ${response.status}`);
  const obj=await response.json();
  if(obj.error || typeof obj.result!=='string' || Number.parseInt(obj.result,16)!==61999)
    throw new Error('REFUSING: stable RPC did not prove chain ID 61999');
  console.log(`Verified RPC chain 61999 at ${rpc}`);
}
try {
  if(!existsSync(cli)) throw new Error('No repo-local CLI; run npm install first.');
  const ver=spawnSync(cli,['--version'],{cwd:root,encoding:'utf8',shell:process.platform==='win32'});
  const value=(ver.stdout||'')+' '+(ver.stderr||'');
  if(ver.status!==0||!/(^|\D)0\.39\.1(\D|$)/.test(value))
    throw new Error(`REFUSING: local CLI must be 0.39.1, got ${value.trim()}`);
  const manifest=JSON.parse(readFileSync(resolve(root,'package.json'),'utf8'));
  if(manifest.devDependencies?.genlayer!=='0.39.1') throw new Error('Pin tampered');
  await assertChain();
  run(['network','set','studionet']);
  run(['network','info']);
  const rl=readline.createInterface({input,output});
  const answer=await rl.question('Confirm network=studionet/61999 and deploy? Type DEPLOY-61999: ');
  rl.close();
  if(answer.trim()!=='DEPLOY-61999') throw new Error('Deployment canceled');
  run(['deploy','--contract','contracts/ratchet.py','--rpc',rpc]);
} catch(e) {
  console.error(e.message);
  process.exitCode=1;
}
