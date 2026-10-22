document.addEventListener('DOMContentLoaded', () => {
    // --- NAVBAR SCROLL EFFECT ---
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.style.background = 'rgba(15, 23, 42, 0.95)';
                navbar.style.boxShadow = '0 4px 20px rgba(0,0,0,0.1)';
            } else {
                navbar.style.background = 'rgba(15, 23, 42, 0.7)';
                navbar.style.boxShadow = 'none';
            }
        });
    }

    // --- INDEX PAGE: TRACKING FORM ---
    const trackingForm = document.getElementById('tracking-form');
    if (trackingForm) {
        trackingForm.addEventListener('submit', (e) => {
            const trackingNumber = document.getElementById('tracking-number').value.trim().toUpperCase();
            if (trackingNumber) {
                document.getElementById('tracking-number').value = trackingNumber;
            }
        });
    }

    // --- MOBILE MENU TOGGLE ---
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuToggle && navLinks) {
        mobileMenuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            const icon = mobileMenuToggle.querySelector('i');
            if (navLinks.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-xmark');
            } else {
                icon.classList.remove('fa-xmark');
                icon.classList.add('fa-bars');
            }
        });
    }
});

// --- GOOGLE TRANSLATE INTEGRATION ---
const googleTranslateScript = document.createElement('script');
googleTranslateScript.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
document.head.appendChild(googleTranslateScript);

const translateDiv = document.createElement('div');
translateDiv.id = 'google_translate_element';
translateDiv.style.display = 'none';
document.body.appendChild(translateDiv);

window.googleTranslateElementInit = function() {
    new google.translate.TranslateElement({
        pageLanguage: 'en',
        autoDisplay: false
    }, 'google_translate_element');
};

window.changeLang = function(langName) {
    const langMap = {
        'English': 'en', 'Russian': 'ru', 'German': 'de', 'Spanish': 'es',
        'French': 'fr', 'Chinese': 'zh-CN', 'Arabic': 'ar', 'Hindi': 'hi',
        'Portuguese': 'pt', 'Japanese': 'ja', 'Korean': 'ko', 'Italian': 'it',
        'Dutch': 'nl', 'Turkish': 'tr', 'Vietnamese': 'vi', 'Polish': 'pl',
        'Indonesian': 'id', 'Thai': 'th', 'Swedish': 'sv', 'Greek': 'el'
    };
    
    const langCode = langMap[langName];
    if (!langCode) return;
    
    const currentLangSpan = document.querySelector('.current-lang');
    if (currentLangSpan) {
        currentLangSpan.textContent = langName;
    }
    
    const select = document.querySelector('.goog-te-combo');
    if (select) {
        select.value = langCode;
        select.dispatchEvent(new Event('change'));
    }
};
