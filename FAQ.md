# Frequently Asked Questions (FAQ)

### 1. Is SEAR really free?
Yes, SEAR is 100% free and open-source under the Apache 2.0 license. There are no hidden fees, subscriptions, or paywalls.

### 2. How is this different from Screaming Frog?
While Screaming Frog is an excellent desktop tool, SEAR is built for modern, asynchronous, and programmatic workflows. SEAR also includes built-in AI prompt generation, native Persian NLP support, and a modern HTML dashboard, all without a license fee.

### 3. Does SEAR send my website data to a third-party server?
No. SEAR operates locally on your machine. The only external requests made are to the target website you are analyzing and, optionally, to official APIs (like Google Search Console) if you provide your own OAuth credentials.

### 4. Why do I need to install `lxml` and `beautifulsoup4`?
`beautifulsoup4` provides the parsing interface, while `lxml` is the underlying C-based parser that makes the extraction incredibly fast and forgiving of malformed HTML.

### 5. Can I use SEAR to crawl my competitor's website?
Yes, but please do so responsibly. SEAR respects `robots.txt` by default. Ensure you do not overwhelm the target server with requests; the built-in `crawl_delay` helps mitigate this.

### 6. How do I add my Google Search Console data?
You need to configure OAuth credentials. Create a `sear_config.json` file (or use `.env`) and populate the `client_id`, `client_secret`, `refresh_token`, and `property_url` under the `search_console` section.
