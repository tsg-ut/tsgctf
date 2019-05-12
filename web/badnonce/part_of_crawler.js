const puppeteer = require('puppeteer');
const flag1 = process.env.FLAG1;
const flag2 = process.env.FLAG2;

const current_host = process.env.CURRENT_HOST;
const url_base = process.env.APP_URL_BASE;
const timeout = parseInt(process.env.TIMEOUT);

const browser_option = {
    executablePath: 'google-chrome-stable',
    headless: true,
    args: [
        '--no-sandbox',
        '--disable-background-networking',
        '--disable-default-apps',
        '--disable-extensions',
        '--disable-gpu',
        '--disable-sync',
        '--disable-translate',
        '--hide-scrollbars',
        '--metrics-recording-only',
        '--mute-audio',
        '--no-first-run',
        '--safebrowsing-disable-auto-update',
    ],
};
const cookies = [
    {
        "domain": current_host,
        "expirationDate": 1597288045,
        "hostOnly": false,
        "httpOnly": false,
        "name": "flag1",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": false,
        "session": false,
        "storeId": "0",
        "value": flag1,
        "id": 1
    },
    {
        "domain": current_host,
        "expirationDate": 1597288045,
        "hostOnly": false,
        "httpOnly": false,
        "name": "flag2",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": false,
        "session": false,
        "storeId": "0",
        "value": flag2,
        "id": 1
    }];


/* ... */
const browser = await puppeteer.launch(browser_option);
try {
    const page = await browser.newPage();
    await page.goto(url_base, {
        timeout: 3000,
        waitUntil: 'networkidle2'
    });
    await page.setCookie(...cookies);
    await page.goto(url, {
        timeout: timeout,
        waitUntil: 'networkidle0'
    });
} catch (err){
    console.log(err);
}
await browser.close();
/* ... */
