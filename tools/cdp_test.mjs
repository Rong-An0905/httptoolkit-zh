// 通过 CDP 验证汉化 / 中英切换，并导出截图与未翻译文案
import fs from 'node:fs';

import path from 'node:path';
import { fileURLToPath } from 'node:url';
const OUT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..') + path.sep;

async function getTarget() {
  for (let i = 0; i < 20; i++) {
    try {
      const r = await fetch('http://127.0.0.1:9222/json/list');
      const list = await r.json();
      const page = list.find(t => t.type === 'page' && t.url.includes('127.0.0.1:8899'));
      if (page) return page;
    } catch (e) { /* retry */ }
    await new Promise(r => setTimeout(r, 1000));
  }
  throw new Error('no CDP target');
}

function cdp(ws) {
  let id = 0;
  const waiting = new Map();
  ws.addEventListener('message', ev => {
    const msg = JSON.parse(ev.data);
    if (msg.id && waiting.has(msg.id)) {
      waiting.get(msg.id)(msg);
      waiting.delete(msg.id);
    }
  });
  return (method, params = {}) => new Promise(res => {
    const mid = ++id;
    waiting.set(mid, res);
    ws.send(JSON.stringify({ id: mid, method, params }));
  });
}

const COLLECT = `(() => {
  const out = [];
  const skip = 'SCRIPT,STYLE,CODE,PRE,TEXTAREA,.monaco-editor,[contenteditable="true"]';
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
    acceptNode(n) {
      if (!n.parentElement || n.parentElement.closest(skip)) return NodeFilter.FILTER_REJECT;
      return NodeFilter.FILTER_ACCEPT;
    }
  });
  let n;
  while ((n = w.nextNode())) {
    const t = n.nodeValue.trim();
    if (t.length > 1 && /[A-Za-z]/.test(t) && !/[\\u3400-\\u9fff]/.test(t)) out.push(t);
  }
  return out;
})()`;

(async () => {
  const target = await getTarget();
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r));
  const send = cdp(ws);

  const evalJS = async (expr) => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    return r.result?.result?.value;
  };

  await send('Page.enable');
  console.log('mode =', await evalJS('window.__htkZh && window.__htkZh.mode'));
  console.log('title =', await evalJS('document.title'));
  console.log('btn =', await evalJS('!!document.getElementById("htk-lang-toggle")'));

  const zhShot = await send('Page.captureScreenshot', { format: 'jpeg', quality: 70 });
  fs.writeFileSync(OUT + 'cdp-zh.jpg', Buffer.from(zhShot.result.data, 'base64'));

  const untranslated = await evalJS(COLLECT) || [];
  fs.writeFileSync(OUT + 'untranslated.json', JSON.stringify(untranslated, null, 1), 'utf8');
  console.log('untranslated count =', untranslated.length);
  console.log('samples =', JSON.stringify(untranslated.slice(0, 15)));

  // 切换到英文
  await evalJS('window.__htkZh.setMode("en")');
  await new Promise(r => setTimeout(r, 1200));
  console.log('mode now =', await evalJS('window.__htkZh.mode'));
  console.log('title now =', await evalJS('document.title'));
  console.log('body sample =', JSON.stringify(await evalJS('document.body.innerText.slice(0,120)')));
  const enShot = await send('Page.captureScreenshot', { format: 'jpeg', quality: 70 });
  fs.writeFileSync(OUT + 'cdp-en.jpg', Buffer.from(enShot.result.data, 'base64'));

  // 切回中文
  await evalJS('window.__htkZh.setMode("zh")');
  await new Promise(r => setTimeout(r, 800));
  console.log('mode back =', await evalJS('window.__htkZh.mode'));
  console.log('body sample zh =', JSON.stringify(await evalJS('document.body.innerText.slice(0,120)')));

  ws.close();
})();
