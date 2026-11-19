/* HTTP Toolkit 本地汉化注入层 —— 展示层改写 + 中英文即时切换，不改动程序本身。 */
(function () {
  if (window.__htkZhLoaded) return;
  window.__htkZhLoaded = true;

  var DICT = __DICT__;
  var LS_KEY = 'htk-zh-mode';
  var DEFAULT_MODE = 'zh';          // 首次打开默认中文，之后按你的选择记忆

  var SKIP_TAGS = { SCRIPT: 1, STYLE: 1, CODE: 1, PRE: 1, TEXTAREA: 1 };
  var SKIP_SELECTOR = '.monaco-editor,[contenteditable="true"],[data-htk-ignored]';

  function norm(s) { return s.replace(/\s+/g, ' ').trim(); }
  function esc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

  // 1) 整句精确匹配表
  var exact = Object.create(null);
  var keys = Object.keys(DICT);
  for (var i = 0; i < keys.length; i++) {
    var k = norm(keys[i]);
    if (k.length >= 2) exact[k] = DICT[keys[i]];
  }

  // 2) 拼接型文案：一条大正则，长短语优先
  var phrases = Object.keys(exact)
    .filter(function (en) { return en.length >= 4 && en.length <= 80; })
    .sort(function (a, b) { return b.length - a.length; });

  var PHRASE_RE = phrases.length
    ? new RegExp('(?<![A-Za-z])(' + phrases.map(esc).join('|') + ')(?![A-Za-z])', 'g')
    : null;

  function translate(text) {
    var hit = exact[norm(text)];
    if (hit) return hit;
    if (/[\u3400-\u9fff]/.test(text)) return text;      // 已经是中文
    if (!PHRASE_RE || text.length > 300) return text;
    return text.replace(PHRASE_RE, function (m) { return exact[m] || m; });
  }

  var mode = (function () {
    try { return localStorage.getItem(LS_KEY) || DEFAULT_MODE; } catch (e) { return DEFAULT_MODE; }
  })();

  function inSkip(el) {
    if (!el) return true;
    if (SKIP_TAGS[el.tagName]) return true;
    try {
      return !!(el.closest && el.closest(SKIP_SELECTOR));
    } catch (e) {
      return false;
    }
  }

  function parts(raw) {
    var lead = raw.match(/^\s*/)[0];
    var trail = raw.match(/\s*$/)[0];
    return [lead, raw.slice(lead.length, raw.length - trail.length), trail];
  }

  function doText(node) {
    var raw = node.nodeValue;
    if (raw == null) return;
    var p = parts(raw);

    if (mode !== 'zh') {
      if (node.__htkEn != null && node.__htkZh == raw && p[1] !== node.__htkEn) {
        node.nodeValue = p[0] + node.__htkEn + p[2];
        node.__htkZh = null;
      }
      return;
    }

    if (!p[1] || p[1].length < 2) return;
    if (node.__htkZh === raw) return;           // 已是本层改写的值
    var zh = translate(p[1]);
    if (zh && zh !== p[1]) {
      node.__htkEn = p[1];                      // 记住英文原文，便于切回
      node.__htkZh = p[0] + zh + p[2];
      node.nodeValue = node.__htkZh;
    }
  }

  function doAttrs(el) {
    var attrs = ['placeholder', 'title', 'aria-label', 'alt'];
    for (var i = 0; i < attrs.length; i++) {
      var attr = attrs[i];
      var v = el.getAttribute && el.getAttribute(attr);
      if (!v) continue;
      var en = el.__htkAttrEn || (el.__htkAttrEn = {});
      var zhStore = el.__htkAttrZh || (el.__htkAttrZh = {});

      if (mode !== 'zh') {
        if (en[attr] != null && zhStore[attr] === v) {
          el.setAttribute(attr, en[attr]);
          zhStore[attr] = null;
        }
        continue;
      }
      if (zhStore[attr] === v) continue;
      var zh = translate(v);
      if (zh && zh !== v) {
        en[attr] = v;
        zhStore[attr] = zh;
        el.setAttribute(attr, zh);
      }
    }
  }

  function walk(root, fn) {
    if (!root) return;
    if (root.nodeType === 3) {
      if (!inSkip(root.parentElement)) fn(root, null);
      return;
    }
    if (root.nodeType !== 1) return;
    if (!inSkip(root)) fn(null, root);

    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        return inSkip(n.parentElement) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
      }
    });
    var batch = [];
    var n;
    while ((n = walker.nextNode())) batch.push(n);
    for (var i = 0; i < batch.length; i++) fn(batch[i], null);

    if (root.querySelectorAll) {
      var els = root.querySelectorAll('[placeholder],[title],[aria-label],[alt]');
      for (var k = 0; k < els.length; k++) if (!inSkip(els[k])) fn(null, els[k]);
    }
  }

  function run() {
    walk(document.body, function (textNode, el) {
      if (textNode) doText(textNode);
      else doAttrs(el);
    });
    if (document.title) {
      if (document.titleStore === undefined) document.titleStore = document.title;
      var t = mode === 'zh' ? translate(document.title) : document.titleStore;
      if (t && t !== document.title) document.title = t;
    }
  }

  var pending = null;
  function schedule() {
    if (pending) return;
    pending = setTimeout(function () { pending = null; run(); }, 80);
  }

  // ---- 切换按钮 ----
  function makeButton() {
    if (document.getElementById('htk-lang-toggle')) return;
    var btn = document.createElement('div');
    btn.id = 'htk-lang-toggle';
    btn.setAttribute('data-htk-ignored', '1');
    btn.style.cssText = [
      'position:fixed', 'right:14px', 'bottom:12px', 'z-index:2147483647',
      'padding:5px 12px', 'border-radius:14px', 'cursor:pointer',
      'font:600 12px/1.4 "DM Sans",system-ui,sans-serif', 'color:#fff',
      'background:rgba(24,24,28,.72)', 'border:1px solid rgba(255,255,255,.18)',
      'box-shadow:0 2px 10px rgba(0,0,0,.28)', 'user-select:none',
      'backdrop-filter:blur(4px)', 'opacity:.75', 'transition:opacity .15s'
    ].join(';');
    btn.onmouseenter = function () { btn.style.opacity = '1'; };
    btn.onmouseleave = function () { btn.style.opacity = '.75'; };
    btn.onclick = function () { setMode(mode === 'zh' ? 'en' : 'zh'); };
    document.body.appendChild(btn);
    renderBtn();
  }

  function renderBtn() {
    var btn = document.getElementById('htk-lang-toggle');
    if (!btn) return;
    btn.textContent = mode === 'zh' ? '中文 / EN' : 'EN / 中文';
    btn.title = mode === 'zh' ? '当前：中文（Ctrl+Alt+L 切换）' : '当前：English（Ctrl+Alt+L 切换）';
  }

  function setMode(next) {
    if (next !== 'en' && next !== 'zh') return;
    mode = next;
    try { localStorage.setItem(LS_KEY, mode); } catch (e) {}
    run();
    renderBtn();
    console.log('[htk-zh] switched to ' + mode);
  }

  function start() {
    makeButton();
    run();
    new MutationObserver(schedule).observe(document.body, {
      childList: true, subtree: true, characterData: true, attributes: true,
      attributeFilter: ['placeholder', 'title', 'aria-label', 'alt']
    });
    window.addEventListener('keydown', function (e) {
      if (e.ctrlKey && e.altKey && (e.key === 'l' || e.key === 'L')) {
        e.preventDefault();
        setMode(mode === 'zh' ? 'en' : 'zh');
      }
    });
    window.__htkZh = {
      get mode() { return mode; },
      setMode: setMode,
      toggle: function () { setMode(mode === 'zh' ? 'en' : 'zh'); }
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
  setTimeout(function () {
    console.log('[htk-zh] mode=' + mode +
      ' btn=' + !!document.getElementById('htk-lang-toggle') +
      ' mode2=' + (window.__htkZh ? window.__htkZh.mode : 'n/a'));
  }, 3000);
})();
