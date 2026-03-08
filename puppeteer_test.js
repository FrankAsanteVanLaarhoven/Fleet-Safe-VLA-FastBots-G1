const puppeteer = require('puppeteer');

(async () => {
    try {
        const browser = await puppeteer.launch({ headless: "new" });
        const page = await browser.newPage();
        
        page.on('console', msg => {
            if (msg.type() === 'error' || msg.text().includes('REACT-THREE-FIBER CRASH')) {
                console.log('BROWSER_LOG:', msg.text());
            }
        });
        
        page.on('pageerror', err => {
            console.log('BROWSER_ERROR:', err.toString());
        });
        
        await page.goto('http://localhost:3000/autoniq', { waitUntil: 'networkidle2', timeout: 10000 });
        
        // await a bit for React to render
        await new Promise(r => setTimeout(r, 2000));
        
        await browser.close();
    } catch (e) {
        console.error("Puppeteer error:", e.toString());
    }
})();
