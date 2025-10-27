// Small DOM-driven animations: counters, intersection observer, hero parallax
(function(){
  function inViewInit() {
    const io = new IntersectionObserver((entries)=>{
      entries.forEach(entry=>{
        if(entry.isIntersecting){
          entry.target.classList.add('in-view');
        }
      });
    }, {threshold: 0.12});

    document.querySelectorAll('.fade-up, .reveal-stagger').forEach(el=>io.observe(el));
  }

  function animateCounters(){
    document.querySelectorAll('.stat-counter').forEach(el=>{
      const target = parseInt(el.dataset.to || el.textContent.replace(/\D/g,''),10) || 0;
      const duration = 1500;
      let start = null;
      const from = 0;
      function step(ts){
        if(!start) start = ts;
        const progress = Math.min((ts-start)/duration,1);
        const value = Math.floor(from + (target - from) * easeOutCubic(progress));
        el.textContent = value.toLocaleString();
        if(progress < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    });
  }

  function easeOutCubic(t){ return 1 - Math.pow(1-t,3); }

  function heroParallax(){
    const hero = document.querySelector('.hero-image-cover');
    const container = hero && hero.closest('section');
    if(!hero || !container) return;
    container.addEventListener('mousemove', function(e){
      const r = container.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      hero.style.transform = `translate3d(${x*10}px, ${-y*8}px, 0) scale(1.02)`;
    });
    container.addEventListener('mouseleave', function(){ hero.style.transform = ''; });
  }

  // when DOM ready
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', ()=>{ inViewInit(); animateCounters(); heroParallax(); });
  } else {
    inViewInit(); animateCounters(); heroParallax();
  }
})();
