document.addEventListener('DOMContentLoaded', function() {
  // Page navigation
  const pageLinks = document.querySelectorAll('.nav-links a');
  const pageSections = document.querySelectorAll('.page');

  pageLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      
      // Remove active class from all links and pages
      pageLinks.forEach(l => l.classList.remove('active'));
      pageSections.forEach(section => section.classList.remove('active'));
      
      // Add active class to clicked link
      this.classList.add('active');
      
      // Show corresponding page
      const targetId = this.getAttribute('href').substring(1);
      const targetSection = document.getElementById(targetId);
      if (targetSection) {
        targetSection.classList.add('active');
      }
    });
  });

  // Initialize first page
  if (pageSections.length > 0) {
    pageSections[0].classList.add('active');
    if (pageLinks.length > 0) {
      pageLinks[0].classList.add('active');
    }
  }

  // Subtab navigation for Experience page
  const subtabButtons = document.querySelectorAll('.subtab');
  const subtabContents = document.querySelectorAll('.subtab-content');

  subtabButtons.forEach(button => {
    button.addEventListener('click', function() {
      // Remove active class from all subtab buttons and contents
      subtabButtons.forEach(btn => btn.classList.remove('active'));
      subtabContents.forEach(content => content.classList.remove('active'));
      
      // Add active class to clicked button
      this.classList.add('active');
      
      // Show corresponding subtab content
      const targetSubtab = this.getAttribute('data-subtab');
      const targetContent = document.getElementById('subtab-' + targetSubtab);
      if (targetContent) {
        targetContent.classList.add('active');
      }
    });
  });

  // Initialize first subtab
  if (subtabButtons.length > 0) {
    subtabButtons[0].classList.add('active');
    const firstTarget = subtabButtons[0].getAttribute('data-subtab');
    const firstContent = document.getElementById('subtab-' + firstTarget);
    if (firstContent) {
      firstContent.classList.add('active');
    }
  }

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });

  // Add subtle animation on scroll
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);

  // Observe all sections
  document.querySelectorAll('.page').forEach(section => {
    section.style.opacity = '0';
    section.style.transform = 'translateY(20px)';
    section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(section);
  });
});