/**
 * نُظم - JavaScript للتفاعلات العصرية
 * Modern Interactive Features for Nuzum Landing Page
 */

class NuzumLanding {
  constructor() {
    this.init();
    this.setupEventListeners();
    this.setupIntersectionObserver();
    this.setupScrollEffects();
    this.setupAnimatedCounters();
    this.setupParallaxEffects();
  }

  /**
   * تهيئة النظام الأساسي
   */
  init() {
    this.navbar = document.querySelector('.modern-navbar');
    this.heroSection = document.querySelector('.hero-section');
    this.reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    // تحقق من دعم المتصفح للتأثيرات المتقدمة
    this.supportsIntersectionObserver = 'IntersectionObserver' in window;
    this.supportsPassiveEvents = this.detectPassiveEvents();
    
    // إعداد المتغيرات العامة
    this.scrollY = 0;
    this.ticking = false;
    
    console.log('🚀 نُظم Landing Page initialized');
  }

  /**
   * إعداد مستمعي الأحداث
   */
  setupEventListeners() {
    // تأثيرات التمرير للشريط العلوي
    const scrollOptions = this.supportsPassiveEvents ? { passive: true } : false;
    window.addEventListener('scroll', this.handleScroll.bind(this), scrollOptions);
    
    // تأثيرات تغيير حجم النافذة
    window.addEventListener('resize', this.debounce(this.handleResize.bind(this), 250));
    
    // معالجة النقر على روابط التنقل السلس
    this.setupSmoothScrolling();
    
    // معالجة قائمة الهاتف المحمول
    this.setupMobileMenu();
    
    // تأثيرات الأزرار التفاعلية
    this.setupButtonEffects();
  }

  /**
   * إعداد مراقب التقاطع للحركات
   */
  setupIntersectionObserver() {
    if (!this.supportsIntersectionObserver || this.reducedMotion) return;

    const observerOptions = {
      root: null,
      rootMargin: '-10% 0px -20% 0px',
      threshold: [0, 0.1, 0.5, 1]
    };

    this.observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.animateElement(entry.target);
        }
      });
    }, observerOptions);

    // إضافة العناصر القابلة للحركة
    this.observeAnimatableElements();
  }

  /**
   * إضافة العناصر للمراقبة
   */
  observeAnimatableElements() {
    const animatableElements = document.querySelectorAll([
      '.fade-in',
      '.slide-in-right',
      '.slide-in-left',
      '.scale-in',
      '.glass-card',
      '.feature-card',
      '.stat-item'
    ].join(', '));

    animatableElements.forEach(el => {
      if (this.observer) {
        this.observer.observe(el);
      }
    });
  }

  /**
   * تحريك العنصر عند ظهوره
   */
  animateElement(element) {
    if (this.reducedMotion) {
      element.classList.add('visible');
      return;
    }

    // إضافة تأخير عشوائي لتأثير أكثر طبيعية
    const delay = Math.random() * 200;
    
    setTimeout(() => {
      element.classList.add('visible');
      
      // تشغيل أصوات التفاعل (إختيارية)
      this.triggerHapticFeedback();
    }, delay);
  }

  /**
   * إعداد تأثيرات التمرير
   */
  setupScrollEffects() {
    if (this.reducedMotion) return;
    
    // إعداد المتغيرات للتأثيرات
    this.lastScrollY = 0;
    this.scrollDirection = 'down';
    
    // إعداد تأثيرات النبرة (parallax) البسيطة
    this.parallaxElements = document.querySelectorAll('[data-parallax]');
  }

  /**
   * معالجة التمرير مع تحسين الأداء
   */
  handleScroll() {
    this.scrollY = window.pageYOffset;

    if (!this.ticking) {
      requestAnimationFrame(() => {
        this.updateOnScroll();
        this.ticking = false;
      });
      this.ticking = true;
    }
  }

  /**
   * تحديث العناصر أثناء التمرير
   */
  updateOnScroll() {
    this.updateNavbar();
    this.updateParallax();
    this.updateScrollProgress();
  }

  /**
   * تحديث شريط التنقل أثناء التمرير
   */
  updateNavbar() {
    if (!this.navbar) return;

    const scrollThreshold = 100;
    
    if (this.scrollY > scrollThreshold) {
      this.navbar.classList.add('scrolled');
    } else {
      this.navbar.classList.remove('scrolled');
    }

    // تحديث الرابط النشط
    this.updateActiveNavItem();
  }

  /**
   * تحديث العنصر النشط في التنقل
   */
  updateActiveNavItem() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');
    
    let current = '';
    
    sections.forEach(section => {
      const sectionTop = section.offsetTop - 200;
      const sectionHeight = section.offsetHeight;
      
      if (this.scrollY >= sectionTop && this.scrollY < sectionTop + sectionHeight) {
        current = section.getAttribute('id');
      }
    });

    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href').includes(current)) {
        link.classList.add('active');
      }
    });
  }

  /**
   * إعداد التمرير السلس
   */
  setupSmoothScrolling() {
    const navLinks = document.querySelectorAll('a[href^="#"]');
    
    navLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        const targetId = link.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        
        if (targetElement) {
          e.preventDefault();
          this.smoothScrollTo(targetElement);
        }
      });
    });
  }

  /**
   * التمرير السلس إلى عنصر معين
   */
  smoothScrollTo(element) {
    const targetPosition = element.offsetTop - 80; // مساحة للشريط العلوي
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    const duration = 1000;
    let start = null;

    const animate = (timestamp) => {
      if (!start) start = timestamp;
      const progress = timestamp - start;
      const ease = this.easeInOutCubic(progress / duration);
      
      window.scrollTo(0, startPosition + distance * ease);
      
      if (progress < duration) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }

  /**
   * دالة التسهيل للحركة السلسة
   */
  easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
  }

  /**
   * إعداد قائمة الهاتف المحمول
   */
  setupMobileMenu() {
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (mobileToggle) {
      mobileToggle.addEventListener('click', () => {
        this.toggleMobileMenu();
      });
    }

    // إغلاق القائمة عند النقر خارجها
    document.addEventListener('click', (e) => {
      if (mobileMenu && !mobileMenu.contains(e.target) && !mobileToggle?.contains(e.target)) {
        this.closeMobileMenu();
      }
    });
  }

  /**
   * تبديل قائمة الهاتف المحمول
   */
  toggleMobileMenu() {
    const mobileMenu = document.querySelector('.mobile-menu');
    if (mobileMenu) {
      mobileMenu.classList.toggle('active');
      document.body.classList.toggle('mobile-menu-open');
    }
  }

  /**
   * إغلاق قائمة الهاتف المحمول
   */
  closeMobileMenu() {
    const mobileMenu = document.querySelector('.mobile-menu');
    if (mobileMenu) {
      mobileMenu.classList.remove('active');
      document.body.classList.remove('mobile-menu-open');
    }
  }

  /**
   * إعداد العدادات المتحركة
   */
  setupAnimatedCounters() {
    const counters = document.querySelectorAll('.stat-number[data-count]');
    
    counters.forEach(counter => {
      if (this.observer) {
        this.observer.observe(counter);
      }
    });
  }

  /**
   * تحريك العداد
   */
  animateCounter(element) {
    if (this.reducedMotion) {
      element.textContent = element.dataset.count;
      return;
    }

    const target = parseInt(element.dataset.count);
    const duration = 2000;
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
      current += increment;
      
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      
      element.textContent = Math.floor(current).toLocaleString('ar-SA');
    }, 16);
  }

  /**
   * إعداد تأثيرات المنظر (Parallax)
   */
  setupParallaxEffects() {
    if (this.reducedMotion) return;

    this.parallaxElements = document.querySelectorAll('.parallax-element');
  }

  /**
   * تحديث تأثيرات المنظر
   */
  updateParallax() {
    if (this.reducedMotion || !this.parallaxElements) return;

    this.parallaxElements.forEach((element, index) => {
      const speed = element.dataset.speed || 0.5;
      const yPos = -(this.scrollY * speed);
      
      element.style.transform = `translate3d(0, ${yPos}px, 0)`;
    });
  }

  /**
   * إعداد تأثيرات الأزرار
   */
  setupButtonEffects() {
    const buttons = document.querySelectorAll('.btn-hero, .btn-nav, .glass-card');
    
    buttons.forEach(button => {
      button.addEventListener('mouseenter', (e) => {
        this.createRippleEffect(e);
      });
      
      button.addEventListener('click', (e) => {
        this.createClickEffect(e);
      });
    });
  }

  /**
   * إنشاء تأثير الموجة
   */
  createRippleEffect(e) {
    if (this.reducedMotion) return;

    const button = e.currentTarget;
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;
    
    const ripple = document.createElement('span');
    ripple.className = 'ripple-effect';
    ripple.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      left: ${x}px;
      top: ${y}px;
      background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
      border-radius: 50%;
      transform: scale(0);
      animation: ripple 0.6s ease-out;
      pointer-events: none;
      z-index: 1;
    `;
    
    button.style.position = 'relative';
    button.style.overflow = 'hidden';
    button.appendChild(ripple);
    
    setTimeout(() => {
      ripple.remove();
    }, 600);
  }

  /**
   * تأثير النقر
   */
  createClickEffect(e) {
    if (this.reducedMotion) return;

    const button = e.currentTarget;
    button.style.transform = 'scale(0.95)';
    
    setTimeout(() => {
      button.style.transform = '';
    }, 150);
  }

  /**
   * إعداد مؤشر التقدم في التمرير
   */
  updateScrollProgress() {
    const progressBar = document.querySelector('.scroll-progress');
    if (!progressBar) return;

    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = (this.scrollY / docHeight) * 100;
    
    progressBar.style.width = `${Math.min(progress, 100)}%`;
  }

  /**
   * معالجة تغيير حجم النافذة
   */
  handleResize() {
    // إعادة حساب المواضع والأحجام
    this.updateOnScroll();
    
    // تحديث متغيرات CSS المخصصة
    this.updateCSSVariables();
  }

  /**
   * تحديث متغيرات CSS
   */
  updateCSSVariables() {
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
  }

  /**
   * تشغيل ردود الفعل اللمسية
   */
  triggerHapticFeedback() {
    if ('vibrate' in navigator) {
      navigator.vibrate(10);
    }
  }

  /**
   * كشف دعم الأحداث السلبية
   */
  detectPassiveEvents() {
    let supportsPassive = false;
    try {
      const opts = Object.defineProperty({}, 'passive', {
        get: function() {
          supportsPassive = true;
        }
      });
      window.addEventListener('testPassive', null, opts);
      window.removeEventListener('testPassive', null, opts);
    } catch (e) {}
    return supportsPassive;
  }

  /**
   * دالة التأخير لتحسين الأداء
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  /**
   * دالة التحديد للحد من التنفيذ
   */
  throttle(func, limit) {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }
}

/**
 * إضافة أنماط CSS للتأثيرات الديناميكية
 */
const addDynamicStyles = () => {
  const styles = `
    @keyframes ripple {
      to {
        transform: scale(2);
        opacity: 0;
      }
    }
    
    .scroll-progress {
      position: fixed;
      top: 0;
      left: 0;
      height: 3px;
      background: linear-gradient(90deg, #1e3a5c, #10b981);
      z-index: 9999;
      transition: width 0.3s ease;
    }
    
    .mobile-menu-open {
      overflow: hidden;
    }
    
    .loading-spinner {
      display: inline-block;
      width: 20px;
      height: 20px;
      border: 3px solid rgba(255,255,255,.3);
      border-radius: 50%;
      border-top-color: #fff;
      animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  `;
  
  const styleSheet = document.createElement('style');
  styleSheet.textContent = styles;
  document.head.appendChild(styleSheet);
};

/**
 * تهيئة النظام عند تحميل الصفحة
 */
document.addEventListener('DOMContentLoaded', () => {
  // إضافة الأنماط الديناميكية
  addDynamicStyles();
  
  // إضافة شريط التقدم
  const progressBar = document.createElement('div');
  progressBar.className = 'scroll-progress';
  document.body.appendChild(progressBar);
  
  // تهيئة النظام الرئيسي
  const nuzumLanding = new NuzumLanding();
  
  // إتاحة النظام عالمياً للتصحيح
  window.NuzumLanding = nuzumLanding;
});

/**
 * معالجة تحميل الخطوط
 */
if ('fonts' in document) {
  document.fonts.ready.then(() => {
    document.documentElement.classList.add('fonts-loaded');
  });
}

/**
 * تحسين تحميل الصور
 */
const lazyLoadImages = () => {
  const images = document.querySelectorAll('img[data-src]');
  
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.classList.remove('lazy');
          imageObserver.unobserve(img);
        }
      });
    });
    
    images.forEach(img => imageObserver.observe(img));
  } else {
    // Fallback للمتصفحات القديمة
    images.forEach(img => {
      img.src = img.dataset.src;
      img.classList.remove('lazy');
    });
  }
};

// تشغيل تحميل الصور الكسول
document.addEventListener('DOMContentLoaded', lazyLoadImages);

/**
 * معالجة تحسين الأداء
 */
const optimizePerformance = () => {
  // تعطيل التمرير السلس للمتصفحات القديمة
  if (!CSS.supports('scroll-behavior', 'smooth')) {
    document.documentElement.style.scrollBehavior = 'auto';
  }
  
  // تحسين استهلاك الذاكرة
  window.addEventListener('beforeunload', () => {
    // تنظيف المستمعين والمراقبين
    if (window.NuzumLanding && window.NuzumLanding.observer) {
      window.NuzumLanding.observer.disconnect();
    }
  });
};

optimizePerformance();