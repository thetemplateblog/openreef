// OpenReef site: mobile nav, docs sidebar toggle, on-this-page TOC with scroll spy, copy buttons.
(function () {
  const navBtn = document.querySelector('[data-nav-toggle]');
  const nav = document.querySelector('[data-nav]');
  if (navBtn && nav) navBtn.addEventListener('click', () => {
    const open = nav.classList.toggle('is-open');
    navBtn.setAttribute('aria-expanded', open);
  });

  const side = document.querySelector('[data-docs-side]');
  const sideBtn = document.querySelector('[data-side-toggle]');
  if (side && sideBtn) sideBtn.addEventListener('click', () => {
    const open = side.classList.toggle('is-open');
    sideBtn.setAttribute('aria-expanded', open);
  });

  // TOC
  const tocList = document.querySelector('[data-toc-list]');
  const article = document.querySelector('.docs-main .prose');
  if (tocList && article) {
    const heads = article.querySelectorAll('h2, h3');
    if (heads.length < 2) { document.querySelector('[data-toc]').style.display = 'none'; }
    const links = [];
    heads.forEach(h => {
      if (!h.id) h.id = h.textContent.trim().toLowerCase().replace(/[^\w]+/g, '-');
      const a = document.createElement('a');
      a.href = '#' + h.id; a.textContent = h.textContent; if (h.tagName === 'H3') a.className = 'lvl3';
      tocList.appendChild(a); links.push([h, a]);
    });
    const spy = () => {
      let current = links[0];
      for (const l of links) if (l[0].getBoundingClientRect().top < 120) current = l;
      links.forEach(([, a]) => a.classList.toggle('is-active', current && a === current[1]));
    };
    document.addEventListener('scroll', spy, { passive: true }); spy();
  }

  // copy buttons on code blocks
  document.querySelectorAll('pre').forEach(pre => {
    const b = document.createElement('button');
    b.textContent = 'Copy'; b.className = 'copy-btn';
    b.style.cssText = 'position:absolute;top:8px;right:8px;font:500 11px Inter,sans-serif;background:#2d3b39;color:#d7e0de;border:0;border-radius:6px;padding:4px 8px;cursor:pointer';
    pre.style.position = 'relative';
    b.addEventListener('click', () => { navigator.clipboard.writeText(pre.innerText.replace(/^Copy\n?/, '')); b.textContent = 'Copied'; setTimeout(() => b.textContent = 'Copy', 1200); });
    pre.appendChild(b);
  });
})();
