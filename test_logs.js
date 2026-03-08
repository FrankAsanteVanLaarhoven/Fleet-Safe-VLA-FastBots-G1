const puppeteer = require('puppeteer');

(async () => {
    try {
        const browser = await puppeteer.launch({ headless: true });
        const page = await browser.newPage();
        
        page.on('console', msg => {
            if (msg.text().includes('CRASH')) {
                console.log('BROWSER_LOG:', msg.text());
            }
        });
        
        await page.goto('http://localhost:3000/autoniq/mujoco', { waitUntil: 'networkidle2', timeout: 15000 });
        
        // await a bit for React to render and error
        await new Promise(r => setTimeout(r, 4000));
        
        const errors = await page.evaluate(() => window.LAST_R3F_ERROR_ARGS || []);
        console.log("LAST_R3F_ERROR_ARGS:", JSON.stringify(errors));
        
        await browser.close();
    } catch (e) {
        console.error("Puppeteer error:", e.toString());
    }
})();
