<div align="center">

# SEAR
### Smart Enterprise Analysis & Reporting

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-4CAF50?logo=apache)](https://www.apache.org/licenses/LICENSE-2.0)
[![Open Source](https://img.shields.io/badge/Open_Source-Yes-2ea44f)](https://github.com/mahdiklidari190/SEAR)
[![SEO](https://img.shields.io/badge/Category-SEO_Intelligence-F59E0B)](https://github.com/mahdiklidari190/SEAR)
[![AI](https://img.shields.io/badge/AI-Powered-8B5CF6)](https://github.com/mahdiklidari190/SEAR)
[![Contributions](https://img.shields.io/badge/Contributions-Welcome-FF69B4)](https://github.com/mahdiklidari190/SEAR/pulls)

**An enterprise-grade, open-source SEO intelligence platform. A powerful, free, and privacy-first alternative to Ahrefs, SEMrush, and Screaming Frog.**

</div>

<br>

---

# 🇬🇧 English Documentation

## 📖 1. Project Overview
> *"Enterprise-level SEO auditing shouldn't cost hundreds of dollars a month, nor should it require sacrificing your data privacy to third-party cloud servers."*

**SEAR** (Smart Enterprise Analysis & Reporting) is a comprehensive, modular, and asynchronous SEO analysis platform built in Python. It solves the problem of fragmented SEO workflows by combining deep crawling, graph analysis, Core Web Vitals estimation, and AI-driven recommendations into a single, cohesive experience. 

Unlike traditional tools that rely on massive, outdated cloud databases, SEAR performs **real-time, on-demand analysis** directly from your machine. This ensures 100% data privacy, up-to-the-second accuracy, and zero subscription fees.

## 🚀 2. Key Features
SEAR is packed with 37+ enterprise-level features designed for SEO professionals, developers, and agencies.

| Category | Feature | Description |
| :--- | :--- | :--- |
| **Core** | **SEO Analysis** | Comprehensive on-page and off-page scoring. |
| | **Technical SEO** | Deep server, header, and protocol analysis. |
| | **Crawl Budget** | Detects wasted budget, duplicates, and parameters. |
| **Links** | **Internal Link Graph** | Visualizes site architecture and authority flow. |
| | **Orphan Pages** | Identifies pages with zero internal inbound links. |
| | **Broken Links** | Detects 404, 410, 500, 502, 503, and DNS errors. |
| | **Redirect Chains** | Maps 301, 302, 307, 308 chains and loops. |
| **Validation** | **Robots & Sitemap** | Validates syntax, rules, and XML/Image/Video sitemaps. |
| | **Schema & Breadcrumbs** | Validates JSON-LD for 13+ schema types and hierarchy. |
| **Performance** | **Core Web Vitals** | Estimates LCP, CLS, INP, FCP, TBT, and TTFB. |
| | **Security & SSL** | Checks HSTS, CSP, X-Frame-Options, and TLS expiry. |
| | **JS Rendering** | Detects React, Vue, Angular, Next.js, and Nuxt. |
| **Content** | **Similarity & Cannibalization** | Uses MinHash/SimHash for near-duplicate detection. |
| | **Competitor Analysis** | Auto-discovers top SERP competitors via search APIs. |
| **Integrations** | **GSC & GA4** | Optional OAuth integration for CTR, clicks, and engagement. |
| | **Backlink APIs** | Optional connectors for Ahrefs, SEMrush, Moz, DataForSEO. |
| **Reporting** | **Multi-Format Export** | Generates TXT, JSON, CSV, PDF, and interactive HTML. |
| | **AI Master Prompt** | Generates a massive, ready-to-use prompt for LLMs. |

## 📂 3. Folder Structure
```text
SEAR/
├── main.py                     # Entry point and CLI orchestrator
├── requirements.txt            # Python dependencies
├── sear_config.json            # Optional API keys and settings
├── config/                     # Configuration and constants
├── models/                     # Pydantic data models
├── core/                       # Fetcher, parser, extractor, scorer
├── analysis/                   # 19 specialized SEO analysis modules
├── keywords/                   # Keyword extraction and processing
├── competitors/                # Competitor discovery engine
├── integrations/               # GSC, GA4, and Backlink API connectors
├── reports/                    # TXT, JSON, CSV, PDF, HTML generators
├── ai/                         # AI Master Prompt generator
└── utils/                      # Helper functions and dependency checks
```

## ⚙️ 4. Installation
> [!TIP]
> Python 3.10 or higher is required.

**Windows / macOS / Linux**
```bash
# 1. Clone the repository
git clone https://github.com/mahdiklidari190/SEAR.git
cd SEAR

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python main.py
```

## 📦 5. Dependencies
| Dependency | Purpose |
| :--- | :--- |
| `httpx` | Async HTTP client with HTTP/2 support for blazing-fast fetching. |
| `pydantic` | Robust data validation and settings management. |
| `beautifulsoup4` & `lxml` | Powerful and forgiving HTML/XML parsing. |
| `rich` | Beautiful terminal output, progress bars, and formatted tables. |
| `tenacity` | Robust retry logic for handling network timeouts gracefully. |
| `networkx` | Graph theory library for internal link mapping. |
| `datasketch` | MinHash and LSH algorithms for near-duplicate content detection. |
| `jinja2` | Templating engine for generating the dynamic HTML dashboard. |
| `reportlab` | PDF document generation for professional client reports. |

## 💡 6. How to Use
1. Run `python main.py` in your terminal.
2. When prompted, enter the target URL (e.g., `https://example.com`) or a Sitemap URL.
3. The engine will automatically detect the sitemap, queue the pages, and begin asynchronous analysis.
4. Watch the real-time progress bars in your terminal.
5. Upon completion, SEAR will automatically open `report.html` in your default web browser.

## 🤖 7. AI Analysis Engine
SEAR doesn't just find problems; it prepares the solution. The **AI Master Prompt** aggregates raw website data, technical metrics, SEO scores, and competitor context. It outputs a single, massive prompt that, when fed to an LLM (like GPT-4 or Claude 3), generates a step-by-step, implementation-ready SEO action plan, including exact JSON-LD code and meta rewrites.

## 🗺️ 8. Roadmap
- [x] Core asynchronous crawling engine
- [x] 24+ Technical and On-Page SEO checks
- [x] Multi-format export (TXT, JSON, CSV, PDF, HTML)
- [x] AI Master Prompt generation
- [x] Google Search Console & Analytics OAuth integration
- [ ] Automated CI/CD testing pipeline
- [ ] FastAPI backend for cloud-based dashboard hosting
- [ ] React-based frontend dashboard replacement

## 🤝 9. Contributing
We welcome contributions! Please follow these steps:
1. **Fork** the repository.
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/SEAR.git`
3. **Create a branch**: `git checkout -b feature/AmazingFeature`
4. **Commit** your changes: `git commit -m 'Add some AmazingFeature'`
5. **Push** to the branch: `git push origin feature/AmazingFeature`
6. Open a **Pull Request**.

---

<br>
<div align="center">
  <h2>🇮🇷 مستندات فارسی</h2>
  <p>برای راحتی کاربران فارسی‌زبان، توضیحات کامل پروژه به زبان فارسی در ادامه آمده است.</p>
</div>
<br>

---

## 📖 ۱. معرفی پروژه
> *"حسابرسی سئو در سطح سازمانی نباید ماهانه صدها دلار هزینه داشته باشد و همچنین نباید نیازمند به خطر انداختن حریم خصوصی داده‌ها و ارسال آن‌ها به سرورهای ابری شخص ثالث باشد."*

**SEAR** (Smart Enterprise Analysis & Reporting) یک پلتفرم جامع، ماژولار و غیرهمگام (Asynchronous) برای آنالیز سئو است که با زبان پایتون ساخته شده است. این ابزار مشکل پراکندگی در گردش کار سئو را با ترکیب خزش عمیق، تحلیل گراف، تخمین Core Web Vitals و پیشنهادات مبتنی بر هوش مصنوعی در یک تجربه یکپارچه حل می‌کند. 

برخلاف ابزارهای سنتی که به پایگاه‌های داده ابری بزرگ و قدیمی متکی هستند، SEAR آنالیز **بلادرنگ و بر اساس تقاضا** را مستقیماً از سیستم شما انجام می‌دهد. این موضوع حریم خصوصی ۱۰۰٪ داده‌ها، دقت لحظه‌ای و حذف هزینه‌های اشتراک را تضمین می‌کند.

## 🚀 ۲. ویژگی‌های کلیدی
پروژه SEAR با بیش از ۳۷ ویژگی در سطح سازمانی طراحی شده است.

| دسته‌بندی | ویژگی | توضیحات |
| :--- | :--- | :--- |
| **هسته** | **آنالیز سئو** | امتیازدهی جامع درون‌صفحه‌ای و برون‌صفحه‌ای. |
| | **سئو تکنیکال** | آنالیز عمیق سرور، هدرها و پروتکل‌ها. |
| | **بودجه خزش** | تشخیص بودجه هدر رفته، صفحات تکراری و پارامتری. |
| **لینک‌ها** | **گراف لینک داخلی** | تصویرسازی معماری سایت و جریان اعتبار (Authority). |
| | **صفحات یتیم** | شناسایی صفحات بدون هیچ لینک داخلی ورودی. |
| | **لینک‌های شکسته** | تشخیص خطاهای 404, 410, 500, 502, 503 و DNS. |
| **اعتبارسنجی** | **Robots و سایت‌مپ** | بررسی سینتکس، قوانین و سایت‌مپ‌های XML/تصویر/ویدیو. |
| | **اسکیما و بردکرامب** | اعتبارسنجی JSON-LD برای بیش از ۱۳ نوع اسکیما. |
| **عملکرد** | **Core Web Vitals** | تخمین LCP, CLS, INP, FCP, TBT و TTFB. |
| | **امنیت و SSL** | بررسی HSTS, CSP, X-Frame-Options و انقضای گواهی. |
| | **رندرینگ جاوااسکریپت** | تشخیص React, Vue, Angular, Next.js و Nuxt. |
| **محتوا** | **شباهت و هم‌نوع‌خواری** | استفاده از MinHash/SimHash برای تشخیص محتوای تکراری. |
| | **آنالیز رقبا** | کشف خودکار رقبای برتر SERP از طریق APIهای جستجو. |
| **یکپارچه‌سازی**| **سرچ کنسول و GA4** | اتصال اختیاری OAuth برای CTR، کلیک و تعامل. |
| | **API بک‌لینک** | اتصال‌دهنده‌های اختیاری برای Ahrefs, SEMrush و Moz. |
| **گزارش‌دهی** | **خروجی چندفرمتی** | تولید گزارش‌های TXT, JSON, CSV, PDF و داشبورد HTML. |
| | **پرامپت استاد هوش مصنوعی** | تولید یک پرامپت عظیم و آماده‌به‌کار برای مدل‌های زبانی. |

## 📂 ۳. ساختار پوشه‌ها
```text
SEAR/
├── main.py                     # نقطه ورود و هماهنگ‌کننده خط فرمان
├── requirements.txt            # وابستگی‌های پایتون
├── sear_config.json            # کلیدهای API و تنظیمات اختیاری
├── config/                     # پیکربندی و ثابت‌ها
├── models/                     # مدل‌های داده Pydantic
├── core/                       # ماژول‌های دریافت، تجزیه، استخراج و امتیازدهی
├── analysis/                   # ۱۹ ماژول تخصصی آنالیز سئو
├── keywords/                   # استخراج و پردازش کلمات کلیدی
├── competitors/                # موتور کشف رقبا
├── integrations/               # اتصال‌دهنده‌های GSC، GA4 و API بک‌لینک
├── reports/                    # تولیدکنندگان گزارش‌های TXT, JSON, CSV, PDF, HTML
├── ai/                         # تولیدکننده پرامپت استاد هوش مصنوعی
└── utils/                      # توابع کمکی و بررسی وابستگی‌ها
```

## ⚙️ ۴. نصب و راه‌اندازی
> [!TIP]
> پایتون نسخه ۳.۱۰ یا بالاتر مورد نیاز است.

**ویندوز / مک / لینوکس**
```bash
# ۱. کلون کردن مخزن
git clone https://github.com/mahdiklidari190/SEAR.git
cd SEAR

# ۲. ساخت محیط مجازی
python -m venv venv

# ۳. فعال‌سازی محیط مجازی
# ویندوز:
venv\Scripts\activate
# مک/لینوکس:
source venv/bin/activate

# ۴. نصب وابستگی‌ها
pip install -r requirements.txt

# ۵. اجرای برنامه
python main.py
```

## 📦 ۵. وابستگی‌ها
| وابستگی | دلیل استفاده |
| :--- | :--- |
| `httpx` | کلاینت HTTP غیرهمگام با پشتیبانی از HTTP/2 برای دریافت فوق‌سریع. |
| `pydantic` | اعتبارسنجی قوی داده‌ها و مدیریت تنظیمات. |
| `beautifulsoup4` و `lxml` | تجزیه و استخراج قدرتمند و انعطاف‌پذیر HTML/XML. |
| `rich` | خروجی زیبای ترمینال، نوارهای پیشرفت و جداول قالب‌بندی شده. |
| `tenacity` | منطق تلاش مجدد (Retry) قوی برای مدیریت قطعی شبکه. |
| `networkx` | کتابخانه نظریه گراف برای نقشه‌برداری لینک داخلی. |
| `datasketch` | الگوریتم‌های MinHash و LSH برای تشخیص محتوای شبه‌تکراری. |
| `jinja2` | موتور قالب‌سازی برای تولید داشبورد HTML پویا. |
| `reportlab` | تولید اسناد PDF برای گزارش‌های حرفه‌ای. |

## 💡 ۶. نحوه استفاده
۱. دستور `python main.py` را در ترمینال خود اجرا کنید.
۲. هنگام درخواست، آدرس URL هدف (مثلاً `https://example.com`) یا آدرس سایت‌مپ را وارد کنید.
۳. موتور به طور خودکار سایت‌مپ را تشخیص داده، صفحات را در صف قرار داده و آنالیز غیرهمگام را آغاز می‌کند.
۴. نوارهای پیشرفت بلادرنگ را در ترمینال خود مشاهده کنید.
۵. پس از اتمام، SEAR به طور خودکار فایل `report.html` را در مرورگر پیش‌فرض وب شما باز می‌کند.

## 🤖 ۷. موتور تحلیل هوش مصنوعی
SEAR فقط مشکلات را پیدا نمی‌کند؛ راه‌حل را آماده می‌کند. **پرامپت استاد هوش مصنوعی** داده‌های خام وب‌سایت، معیارهای فنی، امتیازات سئو و زمینه رقبا را تجمیع می‌کند. این پرامپت یک خروجی واحد و عظیم تولید می‌کند که با دادن آن به یک مدل زبانی بزرگ (مانند GPT-4 یا Claude 3)، یک برنامه عملیاتی سئو گام‌به‌گام و آماده اجرا، شامل کد دقیق JSON-LD و بازنویسی متا تولید می‌شود.

## 🗺️ ۸. نقشه راه (Roadmap)
- [x] موتور خزش غیرهمگام هسته
- [x] بیش از ۲۴ بررسی سئو تکنیکال و درون‌صفحه‌ای
- [x] خروجی چندفرمتی (TXT, JSON, CSV, PDF, HTML)
- [x] تولید پرامپت استاد هوش مصنوعی
- [x] یکپارچه‌سازی OAuth گوگل سرچ کنسول و آنالیتیکس
- [ ] خط لوله تست خودکار CI/CD
- [ ] بک‌اند FastAPI برای میزبانی داشبورد مبتنی بر ابر
- [ ] جایگزینی داشبورد فرانت‌اند مبتنی بر React

## 🤝 ۹. مشارکت در پروژه
ما از مشارکت شما استقبال می‌کنیم! لطفاً این مراحل را دنبال کنید:
۱. مخزن را **Fork** کنید.
۲. فورک خود را **Clone** کنید: `git clone https://github.com/YOUR_USERNAME/SEAR.git`
۳. یک **شاخه (Branch)** بسازید: `git checkout -b feature/AmazingFeature`
۴. تغییرات خود را **Commit** کنید: `git commit -m 'Add some AmazingFeature'`
۵. تغییرات را **Push** کنید: `git push origin feature/AmazingFeature`
۶. یک **Pull Request** باز کنید.

---

<br>
<div align="center">

### 🌐 Connect with the Creator

[![Website](https://img.shields.io/badge/Website-klidari.ir-000000?logo=google-chrome&logoColor=white)](https://klidari.ir/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Bardia_Klidari-0077B5?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/bardia-klidari-64a32a30b?originalSubdomain=ir)
[![GitHub](https://img.shields.io/badge/GitHub-mahdiklidari190-181717?logo=github&logoColor=white)](https://github.com/mahdiklidari190)

<br>

**Made with ❤️ by Bardia Klidari**  
*Smart Enterprise Analysis & Reporting*  
*Open Source Forever*

</div>
