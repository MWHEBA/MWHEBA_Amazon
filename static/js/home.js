/**
 * ملف JavaScript للصفحة الرئيسية
 */

document.addEventListener('DOMContentLoaded', function() {
    // تأثيرات التمرير
    const fadeElements = document.querySelectorAll('.fade-in');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });
    
    fadeElements.forEach(element => {
        observer.observe(element);
    });
    
    // تحريك الإحصائيات - عداد رقمي
    const statsValues = document.querySelectorAll('.stats-value');
    
    statsValues.forEach(stat => {
        const finalValue = stat.textContent;
        let startValue = 0;
        let endValue = parseInt(finalValue.replace(/\D/g, ''));
        let duration = Math.floor(2000 / endValue);
        let counter = setInterval(function() {
            startValue += 1;
            stat.textContent = finalValue.replace(/\d+/, startValue);
            if (startValue >= endValue) {
                clearInterval(counter);
                stat.textContent = finalValue;
            }
        }, duration);
    });
    
    // تأثير التمرير السلس للروابط الداخلية
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            // إزالة الفئة النشطة من جميع الروابط
            document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
                link.classList.remove('active');
            });
            
            // إضافة الفئة النشطة للرابط المضغوط
            this.classList.add('active');
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // تحديث الرابط النشط عند التمرير
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    function updateActiveLink() {
        const scrollPosition = window.scrollY;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            const sectionBottom = sectionTop + section.offsetHeight;
            const sectionId = '#' + section.getAttribute('id');
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === sectionId) {
                        link.classList.add('active');
                    }
                });
            }
        });
        
        // إذا كنا في أعلى الصفحة، نجعل رابط الرئيسية نشطًا
        if (scrollPosition < 100) {
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === '/') {
                    link.classList.add('active');
                }
            });
        }
    }
    
    window.addEventListener('scroll', updateActiveLink);
    
    // تحديث الرابط النشط عند تحميل الصفحة
    updateActiveLink();
    
    // تأثير تكبير الصور عند النقر
    const screenshotItems = document.querySelectorAll('.screenshot-item img');
    
    screenshotItems.forEach(item => {
        item.addEventListener('click', function() {
            // إنشاء طبقة العرض المكبر
            const overlay = document.createElement('div');
            overlay.className = 'image-overlay';
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.9)';
            overlay.style.display = 'flex';
            overlay.style.alignItems = 'center';
            overlay.style.justifyContent = 'center';
            overlay.style.zIndex = '9999';
            
            // إنشاء الصورة المكبرة
            const enlargedImg = document.createElement('img');
            enlargedImg.src = this.src;
            enlargedImg.style.maxWidth = '90%';
            enlargedImg.style.maxHeight = '90%';
            enlargedImg.style.boxShadow = '0 0 20px rgba(255, 255, 255, 0.5)';
            enlargedImg.style.border = '2px solid white';
            
            // إنشاء زر الإغلاق
            const closeBtn = document.createElement('button');
            closeBtn.textContent = '×';
            closeBtn.style.position = 'absolute';
            closeBtn.style.top = '20px';
            closeBtn.style.right = '20px';
            closeBtn.style.backgroundColor = 'transparent';
            closeBtn.style.border = 'none';
            closeBtn.style.color = 'white';
            closeBtn.style.fontSize = '40px';
            closeBtn.style.cursor = 'pointer';
            
            // إضافة العناصر إلى الطبقة
            overlay.appendChild(enlargedImg);
            overlay.appendChild(closeBtn);
            document.body.appendChild(overlay);
            
            // إغلاق الطبقة عند النقر على زر الإغلاق أو على الطبقة نفسها
            closeBtn.addEventListener('click', function() {
                document.body.removeChild(overlay);
            });
            
            overlay.addEventListener('click', function(e) {
                if (e.target === overlay) {
                    document.body.removeChild(overlay);
                }
            });
        });
    });
    
    // إضافة تأثير متحرك للأزرار عند التمرير فوقها
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // تفعيل الأكورديون للأسئلة الشائعة
    const accordionButtons = document.querySelectorAll('.accordion-button');
    
    accordionButtons.forEach(button => {
        button.addEventListener('click', function() {
            // إزالة الفئة النشطة من جميع الأزرار
            accordionButtons.forEach(btn => {
                if (btn !== this) {
                    btn.classList.add('collapsed');
                    const content = btn.nextElementSibling;
                    content.style.maxHeight = null;
                }
            });
            
            // تبديل الحالة للزر الحالي
            this.classList.toggle('collapsed');
            const content = this.nextElementSibling;
            
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
            } else {
                content.style.maxHeight = content.scrollHeight + "px";
            }
        });
    });
}); 