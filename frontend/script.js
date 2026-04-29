// ─────────────────────────────────────────────────────────────────────────────
// Config
// ─────────────────────────────────────────────────────────────────────────────
const API_URL = 'https://ai-gift-finder-6-jf7d.onrender.com/api/recommend';

// ─── Full product catalog (mirrors products.json) ────────────────────────────
const CATALOG = [
  { id:'P001', name:"Fisher-Price Baby's First Blocks",   category:'Educational Toys',        price:'89 AED',  brand:'Fisher-Price',  age_fit:'6–36 months',  rating:4.7, tags:['learning','shapes','colorful'],           reason:"A beloved classic that builds fine motor skills and shape recognition. Babies love the satisfying click when shapes drop in!" },
  { id:'P002', name:'Ergobaby Omni 360 Baby Carrier',     category:'Baby Gear',               price:'649 AED', brand:'Ergobaby',      age_fit:'0–48 months',  rating:4.9, tags:['practical','ergonomic','newborn'],         reason:"Award-winning ergonomic carrier with lumbar support and four carry positions — a life-saver for busy parents." },
  { id:'P003', name:'Jellycat Bashful Bunny Soft Toy',    category:'Plush Toys',              price:'115 AED', brand:'Jellycat',      age_fit:'0–10 years',   rating:4.9, tags:['emotional','comfort','plush','gift'],      reason:"Irresistibly soft, endlessly huggable — the Bashful Bunny is a timeless first gift that becomes a lifelong companion." },
  { id:'P004', name:'Munchkin Miracle 360 Trainer Cup',   category:'Feeding',                 price:'59 AED',  brand:'Munchkin',      age_fit:'6–36 months',  rating:4.6, tags:['practical','feeding','weaning'],           reason:"The spill-proof 360° design makes the transition from bottle to cup completely mess-free — parents love it!" },
  { id:'P005', name:'Baby Einstein Take Along Tunes',     category:'Musical Toys',            price:'75 AED',  brand:'Baby Einstein', age_fit:'3–18 months',  rating:4.5, tags:['musical','sensory','developmental'],       reason:"Seven classical melodies and a colourful light show spark curiosity and auditory development in little ones." },
  { id:'P006', name:'HALO SleepSack Wearable Blanket',   category:'Sleep',                   price:'139 AED', brand:'HALO',          age_fit:'0–18 months',  rating:4.8, tags:['sleep','safe','newborn'],                  reason:"Pediatrician-recommended to replace loose blankets — keeps babies at the perfect sleep temperature all night." },
  { id:'P007', name:'Skip Hop Play Gym',                  category:'Play Mats',               price:'299 AED', brand:'Skip Hop',      age_fit:'0–12 months',  rating:4.7, tags:['tummy time','developmental','sensory'],     reason:"Grows with baby through multiple stages with detachable toys, a mirror, and crinkle sounds for endless exploration." },
  { id:'P008', name:'Chicco Baby Senses Gift Set',        category:'Gift Sets',               price:'185 AED', brand:'Chicco',        age_fit:'0–12 months',  rating:4.6, tags:['gift set','sensory','newborn','bundle'],   reason:"Beautifully boxed sensory set with rattle, soft book, teether and plush toy — perfect for any gifting occasion." },
  { id:'P009', name:'Philips Avent Natural Bottle Set',   category:'Feeding',                 price:'175 AED', brand:'Philips Avent', age_fit:'0–12 months',  rating:4.7, tags:['feeding','bottle','newborn'],             reason:"Anti-colic design with a natural-latch nipple makes feeding smoother for both baby and parent." },
  { id:'P010', name:'Infantino Squeeze & Teethe Hedgehog',category:'Teething Toys',          price:'45 AED',  brand:'Infantino',     age_fit:'3–18 months',  rating:4.4, tags:['teething','sensory','BPA-free'],           reason:"Multi-textured BPA-free surface soothes sore gums while encouraging sensory exploration and grip strength." },
  { id:'P013', name:'Manhattan Toy Winkel Rattle',        category:'Sensory Toys',            price:'95 AED',  brand:'Manhattan Toy', age_fit:'3–12 months',  rating:4.8, tags:['rattle','teether','sensory','iconic'],     reason:"The iconic looped rattle has soothed babies for decades — great for hand-eye coordination and gentle teething relief." },
  { id:'P014', name:"Aden + Anais Muslin Swaddles (4pk)", category:"Swaddles & Blankets",    price:'199 AED', brand:'Aden + Anais',  age_fit:'0–12 months',  rating:4.8, tags:['swaddle','muslin','newborn','breathable'], reason:"Four versatile muslin squares that work as swaddles, nursing covers, or pram shades — every new parent needs these." },
  { id:'P015', name:'Lovevery Play Kits (6-Month Box)',   category:'Developmental Kits',      price:'349 AED', brand:'Lovevery',      age_fit:'5–7 months',   rating:4.9, tags:['developmental','educational','premium'],   reason:"Scientifically designed stage-based kit with high-contrast cards, soft blocks and an activity guide — pure developmental gold." },
];

// Category → reliable category-coded images (via picsum + seed)
const CATEGORY_IMAGES = {
  'educational toys':    'https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=600&q=80',
  'plush toys':          'https://images.unsplash.com/photo-1559715541-5daf8a0296d0?w=600&q=80',
  'feeding':             'https://images.unsplash.com/photo-1631210842756-0abf5ba26eac?w=600&q=80',
  'musical toys':        'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=600&q=80',
  'sleep':               'https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=600&q=80',
  'play mats':           'https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=600&q=80',
  'gift sets':           'https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=600&q=80',
  'baby gear':           'https://images.unsplash.com/photo-1555252333-9f8e92e65df9?w=600&q=80',
  'teething toys':       'https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=600&q=80',
  'sensory toys':        'https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=600&q=80',
  'strollers':           'https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=600&q=80',
  'swaddles & blankets': 'https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=600&q=80',
  'developmental kits':  'https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=600&q=80',
  'default':             'https://images.unsplash.com/photo-1513885535751-8b9238bd345a?w=600&q=80',
};

// Per-product image map for precise visuals
const PRODUCT_IMAGES = {
  "Fisher-Price Baby's First Blocks":    'https://picsum.photos/seed/blocks/600/400',
  'Ergobaby Omni 360 Baby Carrier':       'https://picsum.photos/seed/carrier/600/400',
  'Jellycat Bashful Bunny Soft Toy':      'https://picsum.photos/seed/bunny/600/400',
  'Munchkin Miracle 360 Trainer Cup':     'https://picsum.photos/seed/cup/600/400',
  'Baby Einstein Take Along Tunes':       'https://picsum.photos/seed/music/600/400',
  'HALO SleepSack Wearable Blanket':      'https://picsum.photos/seed/sleep/600/400',
  'Skip Hop Play Gym':                    'https://picsum.photos/seed/gym/600/400',
  'Chicco Baby Senses Gift Set':          'https://picsum.photos/seed/giftset/600/400',
  'Philips Avent Natural Bottle Set':     'https://picsum.photos/seed/bottle/600/400',
  'Infantino Squeeze & Teethe Hedgehog':  'https://picsum.photos/seed/hedgehog/600/400',
  'Manhattan Toy Winkel Rattle':          'https://picsum.photos/seed/rattle/600/400',
  "Aden + Anais Muslin Swaddles (4pk)":  'https://picsum.photos/seed/swaddle/600/400',
  'Lovevery Play Kits (6-Month Box)':     'https://picsum.photos/seed/lovevery/600/400',
};


function getImg(category, overrideUrl, productName) {
  if (overrideUrl && overrideUrl.startsWith('http') && !overrideUrl.includes('picsum')) return overrideUrl;
  if (productName && PRODUCT_IMAGES[productName]) return PRODUCT_IMAGES[productName];
  return CATEGORY_IMAGES[(category||'').toLowerCase()] || CATEGORY_IMAGES['default'];
}

// ─── Smart demo search ───────────────────────────────────────────────────────
function demoSearch(query) {
  const q = query.toLowerCase();

  // Budget extraction
  const budgetMatch = q.match(/(\d+)\s*(aed|dirham)/i);
  const budget = budgetMatch ? parseInt(budgetMatch[1]) : Infinity;

  // Parse price from "89 AED" → 89
  function parsePrice(p) { return parseInt((p||'0').replace(/[^\d]/g, '')) || 0; }

  // Intent / keyword scoring
  const INTENT_MAP = {
    educational:['educational','learning','teach','book','school','knowledge','smart'],
    practical:  ['practical','useful','functional','essential','feeding','sleep','gear','bottle','carrier'],
    emotional:  ['emotional','cuddle','soft','plush','love','cute','comfort','hug'],
    musical:    ['music','musical','sing','sound','melody'],
    sensory:    ['sensory','rattle','teether','touch','feel'],
    newborn:    ['newborn','new born','baby shower','0 month','0-3'],
    luxury:     ['luxury','premium','gift','special'],
    blanket:    ['blanket','swaddle','wrap'],
    sleep:      ['sleep','nap','night','bedtime'],
  };

  function score(product) {
    let s = 0;
    const haystack = [product.name, product.category, ...(product.tags||[]), product.reason].join(' ').toLowerCase();
    for (const [, words] of Object.entries(INTENT_MAP)) {
      for (const w of words) { if (q.includes(w) && haystack.includes(w)) s += 2; }
    }
    // general token match
    q.split(/\s+/).forEach(token => { if (token.length > 3 && haystack.includes(token)) s += 1; });
    if (parsePrice(product.price) <= budget) s += 1;
    s += (product.rating || 0) * 0.2;
    return s;
  }

  return CATALOG
    .filter(p => parsePrice(p.price) <= budget)
    .map(p => ({ ...p, confidence: Math.min(0.98, 0.55 + score(p) * 0.05), _score: score(p) }))
    .sort((a, b) => b._score - a._score)
    .slice(0, 5)
    .map(p => {
      const { _score, ...rest } = p;
      return { ...rest, in_stock: true, image_url: null, purchase_link: '#' };
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// DOM refs
// ─────────────────────────────────────────────────────────────────────────────
const queryInput     = document.getElementById('query-input');
const searchBtn      = document.getElementById('search-btn');
const btnText        = searchBtn.querySelector('.btn-text');
const btnLoader      = searchBtn.querySelector('.btn-loader');
const resultsSection = document.getElementById('results-section');
const resultsGrid    = document.getElementById('results-grid');
const resultsCount   = document.getElementById('results-count');
const resultsTitle   = document.getElementById('results-title');
const initialState   = document.getElementById('initial-state');
const emptyState     = document.getElementById('empty-state');
const themeToggle    = document.getElementById('theme-toggle');
const wishlistBtn    = document.getElementById('wishlist-btn');
const wishlistCount  = document.getElementById('wishlist-count');
const btnEn          = document.getElementById('btn-en');
const btnAr          = document.getElementById('btn-ar');
const voiceBtn       = document.getElementById('voice-btn');
const chips          = document.querySelectorAll('.chip');
const suggestionTags = document.querySelectorAll('.suggestion-tag');

// ─────────────────────────────────────────────────────────────────────────────
// State
// ─────────────────────────────────────────────────────────────────────────────
let currentLang       = 'EN';
let wishlist          = JSON.parse(localStorage.getItem('gf_wishlist') || '[]');
let isShowingWishlist = false;
let currentResults    = [];

// ─────────────────────────────────────────────────────────────────────────────
// Translations
// ─────────────────────────────────────────────────────────────────────────────
const T = {
  EN: {
    placeholder:  'e.g., educational toy for 1 year old under 300 AED',
    btnText:      'Find Gifts ✨',
    resultsTitle: 'Recommended for You',
    wishlistTitle:'My Wishlist ❤️',
    emptyTitle:   'No gifts found',
    emptySub:     'Try adjusting your search terms or budget.',
    confidence:   'Match',
    whyFit:       'Why it fits:',
    age:          'Ages',
    itemsFound:   'gifts found',
    buyNow:       'Shop Now →',
    addedWish:    '❤️ Added to wishlist',
    removedWish:  'Removed from wishlist',
    listening:    '🎤 Listening…',
    speechErr:    'Speech recognition failed. Try typing.',
    serverErr:    '⚠️ Backend offline — showing smart demo results.',
  },
  AR: {
    placeholder:  'مثلاً: لعبة تعليمية لعمر سنة أقل من 300 درهم',
    btnText:      'ابحث عن هدايا ✨',
    resultsTitle: 'مقترح لك',
    wishlistTitle:'قائمة أمنياتي ❤️',
    emptyTitle:   'لم يتم العثور على هدايا',
    emptySub:     'حاول تعديل شروط البحث أو الميزانية.',
    confidence:   'تطابق',
    whyFit:       'لماذا يناسبك:',
    age:          'العمر',
    itemsFound:   'هدايا',
    buyNow:       '← تسوق الآن',
    addedWish:    '❤️ تمت الإضافة للمفضلة',
    removedWish:  'تمت الإزالة من المفضلة',
    listening:    '🎤 جاري الاستماع…',
    speechErr:    'فشل التعرف على الصوت.',
    serverErr:    '⚠️ الخادم غير متصل — عرض نتائج تجريبية.',
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// Theme
// ─────────────────────────────────────────────────────────────────────────────
function applyTheme(dark) {
  if (dark) {
    document.documentElement.setAttribute('data-theme', 'dark');
    themeToggle.textContent = '☀️';
    localStorage.setItem('gf_theme', 'dark');
  } else {
    document.documentElement.removeAttribute('data-theme');
    themeToggle.textContent = '🌙';
    localStorage.setItem('gf_theme', 'light');
  }
}
applyTheme(localStorage.getItem('gf_theme') === 'dark');
themeToggle.addEventListener('click', () => applyTheme(!document.documentElement.hasAttribute('data-theme')));

// ─────────────────────────────────────────────────────────────────────────────
// Language
// ─────────────────────────────────────────────────────────────────────────────
function setLanguage(lang) {
  currentLang = lang;
  document.documentElement.lang = lang.toLowerCase();
  document.body.dir = lang === 'AR' ? 'rtl' : 'ltr';
  btnEn.classList.toggle('active', lang === 'EN');
  btnAr.classList.toggle('active', lang === 'AR');
  queryInput.placeholder = T[lang].placeholder;
  btnText.textContent    = T[lang].btnText;
  if (isShowingWishlist) {
    resultsTitle.textContent = T[lang].wishlistTitle;
    renderCards(wishlist);
  } else if (currentResults.length > 0) {
    resultsTitle.textContent = T[lang].resultsTitle;
    renderCards(currentResults);
  }
}
btnEn.addEventListener('click', () => setLanguage('EN'));
btnAr.addEventListener('click', () => setLanguage('AR'));

// ─────────────────────────────────────────────────────────────────────────────
// Voice Search
// ─────────────────────────────────────────────────────────────────────────────
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SR) {
  const rec = new SR();
  rec.continuous = false;
  rec.interimResults = false;
  voiceBtn.addEventListener('click', () => {
    if (voiceBtn.classList.contains('pulsing')) { rec.stop(); return; }
    rec.lang = currentLang === 'AR' ? 'ar-SA' : 'en-US';
    rec.start();
    voiceBtn.classList.add('pulsing');
    showToast(T[currentLang].listening, 'info');
  });
  rec.onresult = e => { queryInput.value = e.results[0][0].transcript; voiceBtn.classList.remove('pulsing'); handleSearch(); };
  rec.onerror  = () => { voiceBtn.classList.remove('pulsing'); showToast(T[currentLang].speechErr, 'error'); };
  rec.onend    = () => voiceBtn.classList.remove('pulsing');
} else {
  voiceBtn.style.display = 'none';
}

// ─────────────────────────────────────────────────────────────────────────────
// Chips & Suggestions
// ─────────────────────────────────────────────────────────────────────────────
chips.forEach(chip => {
  chip.addEventListener('click', () => {
    chip.parentElement.querySelectorAll('.chip').forEach(c => { if (c !== chip) c.classList.remove('active'); });
    chip.classList.toggle('active');
    const active = [...document.querySelectorAll('.chip.active')];
    if (active.length) {
      queryInput.value = `Looking for something ${active.map(c => c.dataset.value).join(' ')}`;
      searchBtn.style.transform = 'scale(1.05)';
      setTimeout(() => searchBtn.style.transform = '', 250);
    }
  });
});

suggestionTags.forEach(tag => {
  tag.addEventListener('click', () => { queryInput.value = tag.textContent.trim(); handleSearch(); });
});

// ─────────────────────────────────────────────────────────────────────────────
// Search
// ─────────────────────────────────────────────────────────────────────────────
searchBtn.addEventListener('click', handleSearch);
queryInput.addEventListener('keypress', e => { if (e.key === 'Enter') handleSearch(); });

async function handleSearch() {
  const query = queryInput.value.trim();
  if (!query) return;

  setLoading(true);
  isShowingWishlist = false;
  initialState.classList.add('hidden');
  resultsSection.classList.add('hidden');
  emptyState.classList.add('hidden');

  let products = [];
  let fromDemo = false;

  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 8000);   // 8 s timeout
    const res = await fetch(API_URL, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ query }),
      signal:  ctrl.signal,
    });
    clearTimeout(timer);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    products = data.products || [];
  } catch {
    // Backend unavailable → use smart demo search
    products  = demoSearch(query);
    fromDemo  = true;
  }

  currentResults = products;

  if (products.length === 0) {
    emptyState.classList.remove('hidden');
  } else {
    resultsTitle.textContent = T[currentLang].resultsTitle;
    resultsSection.classList.remove('hidden');
    renderCards(products);
  }

  if (fromDemo) showToast(T[currentLang].serverErr, 'info');
  setLoading(false);
}

// ─────────────────────────────────────────────────────────────────────────────
// Rendering
// ─────────────────────────────────────────────────────────────────────────────
function renderCards(products) {
  resultsGrid.innerHTML = '';
  resultsCount.textContent = `${products.length} ${T[currentLang].itemsFound}`;

  if (!products.length) {
    resultsSection.classList.add('hidden');
    emptyState.classList.remove('hidden');
    return;
  }
  resultsSection.classList.remove('hidden');
  emptyState.classList.add('hidden');

  products.forEach((p, i) => resultsGrid.appendChild(buildCard(p, i)));
}

function buildCard(product, index) {
  const card = document.createElement('div');
  card.className = 'card';
  card.style.animationDelay = `${index * 0.07}s`;

  const isFav       = wishlist.some(w => w.name === product.name);
  const imgSrc      = getImg(product.category, product.image_url, product.name);
  const buyLink     = product.purchase_link && product.purchase_link !== '#' ? product.purchase_link : '#';
  const confidence  = Math.round((product.confidence || 0) * 100);
  const stars       = product.rating ? renderStars(product.rating) : '';
  const stockBadge  = product.in_stock === false
    ? '<span class="stock-badge out">Out of Stock</span>'
    : '<span class="stock-badge in">In Stock</span>';

  card.innerHTML = `
    <div class="card-img-container">
      <img src="${imgSrc}" alt="${esc(product.name)}" loading="lazy"
           onerror="this.src='${CATEGORY_IMAGES['default']}'">
      <div class="card-img-overlay"></div>
      <div class="card-badge-top">
        <span class="card-category-pill">${esc(product.category || 'Gift')}</span>
      </div>
      <button class="wishlist-toggle${isFav ? ' active' : ''}" aria-label="Toggle wishlist">
        ${isFav ? '♥' : '♡'}
      </button>
    </div>
    <div class="card-body">
      <div class="card-header-row">
        <h3 class="card-name">${esc(product.name)}</h3>
        <span class="confidence-pill">${confidence}%</span>
      </div>
      <div class="card-price-row">
        <span class="price">${esc(product.price)}</span>
        ${stars ? `<span class="rating">${stars} ${Number(product.rating).toFixed(1)}</span>` : ''}
        ${stockBadge}
      </div>
      <div class="reason">
        <span class="reason-label">${T[currentLang].whyFit}</span>
        ${esc(product.reason)}
      </div>
      <div class="card-footer-row">
        <div class="card-meta">
          ${product.brand ? `<span class="brand">${esc(product.brand)}</span>` : ''}
          <span class="age-fit">👶 ${T[currentLang].age}: ${esc(product.age_fit)}</span>
        </div>
        <a href="${buyLink}" target="_blank" rel="noopener" class="buy-btn">
          ${T[currentLang].buyNow}
        </a>
      </div>
    </div>
  `;

  card.querySelector('.wishlist-toggle').addEventListener('click', e => {
    e.stopPropagation();
    toggleWishlistItem(product, e.currentTarget);
  });
  return card;
}

function renderStars(rating) {
  const full  = Math.floor(rating);
  const half  = rating - full >= 0.5;
  const empty = 5 - full - (half ? 1 : 0);
  return '★'.repeat(full) + (half ? '½' : '') + '☆'.repeat(empty);
}

function esc(s) {
  return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ─────────────────────────────────────────────────────────────────────────────
// Wishlist
// ─────────────────────────────────────────────────────────────────────────────
function saveWishlist() { localStorage.setItem('gf_wishlist', JSON.stringify(wishlist)); }

function updateBadge() {
  wishlistCount.textContent = wishlist.length;
  wishlistCount.classList.toggle('hidden', wishlist.length === 0);
}

function toggleWishlistItem(product, btn) {
  const idx = wishlist.findIndex(w => w.name === product.name);
  if (idx > -1) {
    wishlist.splice(idx, 1);
    btn.innerHTML = '♡';
    btn.classList.remove('active');
    showToast(T[currentLang].removedWish, 'info');
  } else {
    wishlist.push(product);
    btn.innerHTML = '♥';
    btn.classList.add('active');
    showToast(T[currentLang].addedWish, 'info');
  }
  saveWishlist();
  updateBadge();
  if (isShowingWishlist) renderCards(wishlist);
}

wishlistBtn.addEventListener('click', () => {
  isShowingWishlist = !isShowingWishlist;
  if (isShowingWishlist) {
    initialState.classList.add('hidden');
    emptyState.classList.add('hidden');
    resultsSection.classList.remove('hidden');
    resultsTitle.textContent = T[currentLang].wishlistTitle;
    renderCards(wishlist);
  } else {
    resultsTitle.textContent = T[currentLang].resultsTitle;
    if (currentResults.length) {
      renderCards(currentResults);
    } else {
      resultsSection.classList.add('hidden');
      initialState.classList.remove('hidden');
    }
  }
});

updateBadge();

// ─────────────────────────────────────────────────────────────────────────────
// Loading
// ─────────────────────────────────────────────────────────────────────────────
function setLoading(on) {
  searchBtn.disabled = on;
  btnText.classList.toggle('hidden', on);
  btnLoader.classList.toggle('hidden', !on);
}

// ─────────────────────────────────────────────────────────────────────────────
// Toasts
// ─────────────────────────────────────────────────────────────────────────────
function showToast(msg, type = 'info') {
  const container = document.getElementById('toast-container');
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.textContent = msg;
  container.appendChild(t);
  setTimeout(() => {
    t.style.cssText += 'opacity:0;transform:translateX(20px);transition:all 0.4s ease;';
    setTimeout(() => t.remove(), 450);
  }, 3800);
}
