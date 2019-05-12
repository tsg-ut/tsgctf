/* this code is a part of our crawler. */

const puppeteer = require('puppeteer');
const url_base = process.env.APP_URL_BASE;
const admin_password = process.env.ADMIN_PASSWORD;
const browser_option = {
    executablePath: 'google-chrome-stable',
    headless: true,
    args: [
        '--no-sandbox',
        '--disable-background-networking',
        '--disk-cache-dir=/dev/null',
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


/* ... */

const browser = await puppeteer.launch(browser_option);
try{ 
    const page = await browser.newPage();
    await page.goto(url_base, {waitUntil: 'networkidle2'});
    await page.type('#username', 'admin');
    await page.type('#password', admin_password);
    await Promise.all([
        page.click('#signin_submit'),
        page.waitForNavigation()
    ]);
    await page.goto(`${url_base}/profile/${username}`, {
        waitUntil: 'networkidle0',
        timeout: 20000,
    });
} catch (err){
    console.log(err);
}
await browser.close();

/* ... */

