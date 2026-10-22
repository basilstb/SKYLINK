document.addEventListener('DOMContentLoaded', () => {
    // --- NAVBAR SCROLL EFFECT ---
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 40) {
                navbar.style.background = 'rgba(11, 15, 25, 0.94)';
                navbar.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.35)';
                navbar.style.borderBottom = '1px solid rgba(99, 102, 241, 0.3)';
            } else {
                navbar.style.background = 'rgba(11, 15, 25, 0.85)';
                navbar.style.boxShadow = 'none';
                navbar.style.borderBottom = '1px solid rgba(99, 102, 241, 0.22)';
            }
        });
    }

    // --- INDEX PAGE: TRACKING FORM ---
    const trackingForm = document.getElementById('tracking-form');
    if (trackingForm) {
        trackingForm.addEventListener('submit', (e) => {
            const trackingInput = document.getElementById('tracking-number');
            if (trackingInput && trackingInput.value) {
                trackingInput.value = trackingInput.value.trim().toUpperCase();
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

    // Initialize Calculator on load
    if (document.getElementById('calc-origin')) {
        calculateRate();
    }
});

// --- QUICK-TEST TRACKING CHIP FILLER ---
window.fillTracking = function(code) {
    const input = document.getElementById('tracking-number');
    if (input) {
        input.value = code;
        input.focus();
        input.style.boxShadow = '0 0 0 3px rgba(6, 182, 212, 0.5)';
        setTimeout(() => {
            const form = document.getElementById('tracking-form');
            if (form) form.submit();
        }, 300);
    }
};

// --- INTERACTIVE FREIGHT & FX RATE CALCULATOR ---
let currentCurrency = 'USD';
const exchangeRates = {
    'USD': { rate: 1.0, symbol: '$' },
    'EUR': { rate: 0.92, symbol: '€' },
    'GBP': { rate: 0.79, symbol: '£' },
    'JPY': { rate: 154.5, symbol: '¥' }
};

window.setCurrency = function(currency) {
    currentCurrency = currency;
    document.querySelectorAll('.currency-btn').forEach(btn => {
        if (btn.getAttribute('data-currency') === currency) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    calculateRate();
};

window.calculateRate = function() {
    const origin = document.getElementById('calc-origin')?.value || 'USA';
    const dest = document.getElementById('calc-dest')?.value || 'SGP';
    const weightVal = parseFloat(document.getElementById('calc-weight')?.value) || 1;
    const tier = document.getElementById('calc-tier')?.value || 'express';

    // Base per kg rates by tier
    let tierMultiplier = 12.0;
    let baseHandling = 40.0;
    if (tier === 'standard') {
        tierMultiplier = 5.5;
        baseHandling = 60.0;
    } else if (tier === 'ground') {
        tierMultiplier = 3.8;
        baseHandling = 25.0;
    }

    // Distance surcharge factor if cross-continent
    let distanceFactor = (origin === dest) ? 1.0 : 1.35;
    
    // Calculate total base in USD
    const freightUSD = (weightVal * tierMultiplier * distanceFactor) + baseHandling;
    const clearanceUSD = Math.max(25.0, freightUSD * 0.18);
    const totalUSD = freightUSD + clearanceUSD;

    // Convert to selected currency
    const fx = exchangeRates[currentCurrency] || exchangeRates['USD'];
    const totalConverted = totalUSD * fx.rate;
    const freightConverted = freightUSD * fx.rate;
    const clearanceConverted = clearanceUSD * fx.rate;

    const displayAmount = document.getElementById('calc-display-amount');
    const metaDetails = document.getElementById('calc-meta-details');

    if (displayAmount) {
        if (currentCurrency === 'JPY') {
            displayAmount.textContent = `${fx.symbol}${Math.round(totalConverted).toLocaleString()}`;
        } else {
            displayAmount.textContent = `${fx.symbol}${totalConverted.toFixed(2)}`;
        }
    }

    if (metaDetails) {
        if (currentCurrency === 'JPY') {
            metaDetails.innerHTML = `Base Freight: ${fx.symbol}${Math.round(freightConverted).toLocaleString()} &bull; Customs Clearance: ${fx.symbol}${Math.round(clearanceConverted).toLocaleString()} &bull; Telemetry: ${fx.symbol}0 (Included)`;
        } else {
            metaDetails.innerHTML = `Base Freight: ${fx.symbol}${freightConverted.toFixed(2)} &bull; Customs Clearance: ${fx.symbol}${clearanceConverted.toFixed(2)} &bull; Telemetry: ${fx.symbol}0 (Included)`;
        }
    }
};

// --- FAQ ACCORDION INTERACTION ---
window.toggleFaq = function(header) {
    const item = header.closest('.faq-item');
    if (!item) return;
    
    const wasActive = item.classList.contains('active');
    // Close other open FAQ items for clean accordion effect
    document.querySelectorAll('.faq-item').forEach(el => el.classList.remove('active'));
    
    if (!wasActive) {
        item.classList.add('active');
    }
};

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
