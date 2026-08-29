document.addEventListener('DOMContentLoaded', function() {
  // ===== Page navigation (top nav) =====
  const pageLinks = document.querySelectorAll('.nav-links a[href^="#"]');
  const pageSections = document.querySelectorAll('.page');

  function showPage(targetId) {
    pageLinks.forEach(l => l.classList.remove('active'));
    pageSections.forEach(s => s.classList.remove('active'));
    const link = document.querySelector(`.nav-links a[href="#${targetId}"]`);
    const section = document.getElementById(targetId);
    if (link) link.classList.add('active');
    if (section) {
      section.classList.add('active');
      section.style.opacity = '1';
      section.style.transform = 'translateY(0)';
    }
  }

  pageLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const targetId = this.getAttribute('href').substring(1);
      showPage(targetId);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });

  // init first page if none active
  if (!document.querySelector('.page.active') && pageSections.length) {
    showPage(pageSections[0].id);
  } else {
    const active = document.querySelector('.page.active');
    if (active) {
      active.style.opacity = '1';
      active.style.transform = 'translateY(0)';
    }
  }

  // ===== Category tabs (level 1) =====
  const categoryTabs = document.querySelectorAll('.category-tab');
  const categoryContents = document.querySelectorAll('.category-content');

  categoryTabs.forEach(btn => {
    btn.addEventListener('click', function() {
      const target = this.dataset.category;
      categoryTabs.forEach(b => b.classList.remove('active'));
      categoryContents.forEach(c => c.classList.remove('active'));
      this.classList.add('active');
      const content = document.getElementById('category-' + target);
      if (content) content.classList.add('active');
    });
  });

  // ===== Subtabs (level 2) - scoped per category =====
  document.querySelectorAll('.subtab').forEach(btn => {
    btn.addEventListener('click', function() {
      const targetId = this.dataset.subtab;
      const category = this.closest('.category-content');
      if (!category) return;
      // only affect subtabs inside same category
      category.querySelectorAll('.subtab').forEach(b => b.classList.remove('active'));
      category.querySelectorAll('.subtab-content').forEach(c => c.classList.remove('active'));
      this.classList.add('active');
      const panel = document.getElementById('subtab-' + targetId);
      if (panel) panel.classList.add('active');
    });
  });

  // ===== Tooling tabs (level 3) =====
  document.querySelectorAll('.tooling-tab').forEach(btn => {
    btn.addEventListener('click', function() {
      const target = this.dataset.tooling;
      const parent = this.closest('.subtab-content');
      if (!parent) return;
      parent.querySelectorAll('.tooling-tab').forEach(b => b.classList.remove('active'));
      parent.querySelectorAll('.tooling-panel').forEach(p => p.classList.remove('active'));
      this.classList.add('active');
      const panel = document.getElementById('tooling-' + target);
      if (panel) panel.classList.add('active');
    });
  });

  // Ensure each category has at least one active subtab/content
  categoryContents.forEach(cat => {
    if (!cat.querySelector('.subtab.active')) {
      const first = cat.querySelector('.subtab');
      if (first) first.classList.add('active');
    }
    if (!cat.querySelector('.subtab-content.active')) {
      const firstC = cat.querySelector('.subtab-content');
      if (firstC) firstC.classList.add('active');
    }
  });

  // ===== PDF link - force new tab (ensure not handled as SPA page) =====
  const pdfLink = document.querySelector('a.btn-pdf');
  if (pdfLink) {
    pdfLink.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      window.open(this.href, '_blank', 'noopener');
    });
  }

  // ===== Contact form -> mailto (option 1, static) =====
  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const name = document.getElementById('contact-name').value.trim();
      const email = document.getElementById('contact-email').value.trim();
      const message = document.getElementById('contact-message').value.trim();
      const status = document.getElementById('contact-status');
      const to = 'suykerbuykh@gmail.com';
      const subject = encodeURIComponent(`CV contact from ${name}`);
      const body = encodeURIComponent(`Name: ${name}\nEmail: ${email}\n\nMessage:\n${message}`);
      const mailto = `mailto:${to}?subject=${subject}&body=${body}`;
      window.location.href = mailto;
      if (status) {
        status.textContent = 'Opening your email app… If nothing happens, please email directly to suykerbuykh@gmail.com';
        status.style.display = 'block';
      }
    });
  }
});
