// Casino Scanner 4.0 - Content Script
// Runs on casino pages to perform analysis

class CasinoScanner {
    constructor() {
        this.findings = {
            vulnerabilities: [],
            loopholes: [],
            bonuses: [],
            forms: []
        };
    }

    // Main scan function
    async scan(scanType = 'quick') {
        console.log('🔍 Starting Casino Scanner analysis...');

        const results = {
            url: window.location.href,
            scanType: scanType,
            timestamp: Date.now(),
            vulnerabilities: [],
            loopholes: [],
            bonuses: []
        };

        try {
            // Basic site analysis
            this.analyzeSiteBasics(results);

            // Form analysis
            this.analyzeForms(results);

            // Look for casino-specific elements
            this.analyzeCasinoElements(results);

            switch(scanType) {
                case 'quick':
                    await this.quickScan(results);
                    break;
                case 'deep':
                    await this.deepScan(results);
                    break;
                case 'bonus':
                    await this.bonusHunterScan(results);
                    break;
            }

            // Check for known vulnerabilities
            this.checkKnownVulnerabilities(results);

            console.log('✅ Scan complete!', results);
            return results;

        } catch (error) {
            console.error('❌ Scan error:', error);
            results.error = error.message;
            return results;
        }
    }

    analyzeSiteBasics(results) {
        // Check if it's a casino site
        const casinoIndicators = [
            /casino/i, /gambling/i, /poker/i, /slots/i, /bet/i, /jackpot/i,
            /blackjack/i, /roulette/i, /baccarat/i, /craps/i
        ];

        const pageText = document.body.innerText.toLowerCase();
        const isCasinoSite = casinoIndicators.some(indicator => indicator.test(pageText));

        if (isCasinoSite) {
            results.siteType = 'casino';
        } else {
            results.siteType = 'unknown';
        }

        // Check for HTTPS
        if (window.location.protocol !== 'https:') {
            results.vulnerabilities.push({
                title: 'HTTP Only',
                description: 'Site does not use HTTPS encryption',
                severity: 'medium',
                type: 'security'
            });
        }
    }

    analyzeForms(results) {
        const forms = document.querySelectorAll('form');
        results.forms = Array.from(forms).map(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            return {
                action: form.action,
                method: form.method,
                inputs: Array.from(inputs).map(input => ({
                    type: input.type,
                    name: input.name,
                    id: input.id,
                    required: input.required,
                    pattern: input.pattern
                }))
            };
        });

        // Look for signup forms
        const signupSelectors = [
            'form[action*="signup"]', 'form[action*="register"]',
            'form[id*="signup"]', 'form[id*="register"]',
            'form[class*="signup"]', 'form[class*="register"]'
        ];

        signupSelectors.forEach(selector => {
            const signupForm = document.querySelector(selector);
            if (signupForm) {
                this.analyzeSignupForm(signupForm, results);
            }
        });
    }

    analyzeSignupForm(form, results) {
        const inputs = form.querySelectorAll('input');
        let hasEmail = false, hasPhone = false, hasPassword = false;
        let hasCaptcha = false, hasTerms = false;

        inputs.forEach(input => {
            const type = input.type.toLowerCase();
            const name = (input.name || '').toLowerCase();

            if (type === 'email' || name.includes('email')) hasEmail = true;
            if (type === 'tel' || name.includes('phone') || name.includes('mobile')) hasPhone = true;
            if (type === 'password' || name.includes('pass')) hasPassword = true;

            // Check for CAPTCHA
            if (name.includes('captcha') || name.includes('recaptcha') ||
                input.className.toLowerCase().includes('captcha')) {
                hasCaptcha = true;
            }
        });

        // Check for terms checkbox
        const termsCheckboxes = form.querySelectorAll('input[type="checkbox"]');
        termsCheckboxes.forEach(checkbox => {
            const label = checkbox.labels ? Array.from(checkbox.labels).map(l => l.textContent.toLowerCase()).join(' ') : '';
            if (label.includes('terms') || label.includes('conditions') || label.includes('agree')) {
                hasTerms = true;
            }
        });

        // Analyze for loopholes
        if (!hasCaptcha) {
            results.loopholes.push({
                title: 'No CAPTCHA Protection',
                description: 'Signup form lacks CAPTCHA protection - potential for automated account creation',
                type: 'account_creation',
                profitPotential: 'High - Easy bot registration'
            });
        }

        if (!hasPhone && hasEmail) {
            results.loopholes.push({
                title: 'Email-Only Registration',
                description: 'Registration requires only email - easy to create multiple accounts',
                type: 'account_creation',
                profitPotential: 'Medium - Multiple accounts possible'
            });
        }

        if (!hasTerms) {
            results.vulnerabilities.push({
                title: 'No Terms Acceptance',
                description: 'Form does not require terms acceptance - potential legal issues',
                severity: 'low',
                type: 'compliance'
            });
        }
    }

    analyzeCasinoElements(results) {
        // Look for bonus codes
        const bonusSelectors = [
            '.bonus', '.promo', '.offer', '.reward',
            '[class*="bonus"]', '[class*="promo"]'
        ];

        bonusSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                const text = element.textContent;
                const bonusCodes = text.match(/[A-Z0-9]{4,12}/g);
                if (bonusCodes) {
                    results.bonuses.push(...bonusCodes.filter(code =>
                        !results.bonuses.includes(code)
                    ));
                }
            });
        });

        // Look for minimum deposit info
        const minDepositPattern = /\$?\d+(?:\.\d{2})?/g;
        const depositElements = document.querySelectorAll('[class*="deposit"], [id*="deposit"]');
        depositElements.forEach(element => {
            const text = element.textContent;
            const amounts = text.match(minDepositPattern);
            if (amounts) {
                results.loopholes.push({
                    title: 'Deposit Information Found',
                    description: `Minimum deposits: ${amounts.join(', ')}`,
                    type: 'deposit_info'
                });
            }
        });
    }

    async quickScan(results) {
        // Basic checks that don't require interaction

        // Check for exposed API endpoints
        const scripts = document.querySelectorAll('script[src]');
        scripts.forEach(script => {
            const src = script.src;
            if (src.includes('api') || src.includes('graphql')) {
                results.vulnerabilities.push({
                    title: 'API Endpoint Exposed',
                    description: `Potential API endpoint: ${src}`,
                    severity: 'low',
                    type: 'information_disclosure'
                });
            }
        });

        // Check for debug information
        if (window.console && window.console.log) {
            // Temporarily override console to capture debug info
            const originalLog = console.log;
            const logs = [];
            console.log = (...args) => {
                logs.push(args.join(' '));
                originalLog(...args);
            };

            // Restore after a short delay
            setTimeout(() => {
                console.log = originalLog;
                if (logs.some(log => log.includes('debug') || log.includes('error'))) {
                    results.vulnerabilities.push({
                        title: 'Debug Information Exposed',
                        description: 'Console logs contain debug or error information',
                        severity: 'low',
                        type: 'information_disclosure'
                    });
                }
            }, 1000);
        }
    }

    async deepScan(results) {
        await this.quickScan(results);

        // Try to detect rate limiting bypass
        const forms = document.querySelectorAll('form');
        for (const form of forms) {
            const inputs = form.querySelectorAll('input[type="hidden"]');
            inputs.forEach(input => {
                if (input.name.includes('token') || input.name.includes('csrf')) {
                    results.vulnerabilities.push({
                        title: 'CSRF Protection Detected',
                        description: 'Form has CSRF protection - good security practice',
                        severity: 'info',
                        type: 'security_positive'
                    });
                }
            });
        }

        // Check for password requirements
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        passwordInputs.forEach(input => {
            if (input.pattern) {
                // Analyze password pattern
                const pattern = input.pattern;
                if (pattern.length < 8) {
                    results.loopholes.push({
                        title: 'Weak Password Requirements',
                        description: 'Password pattern suggests weak requirements',
                        type: 'account_security'
                    });
                }
            }
        });

        // Look for referral programs
        const referralText = document.body.innerText.toLowerCase();
        if (referralText.includes('referral') || referralText.includes('affiliate')) {
            results.loopholes.push({
                title: 'Referral Program Detected',
                description: 'Site has referral/affiliate program - potential for bonus farming',
                type: 'bonus_farming',
                profitPotential: 'Medium - Referral bonuses available'
            });
        }
    }

    async bonusHunterScan(results) {
        // Focus on finding bonuses and promotional offers

        // Look for bonus amounts
        const bonusPattern = /(\$|USD|EUR|£)?\d+(?:\.\d{2})?\s*(?:bonus|free|deposit)/gi;
        const pageText = document.body.innerText;
        const bonusMatches = pageText.match(bonusPattern);

        if (bonusMatches) {
            results.loopholes.push({
                title: 'Bonus Offers Found',
                description: `Detected bonuses: ${bonusMatches.slice(0, 5).join(', ')}`,
                type: 'bonus_offers',
                profitPotential: 'High - Multiple bonus opportunities'
            });
        }

        // Look for no-deposit bonuses
        if (pageText.toLowerCase().includes('no deposit') ||
            pageText.toLowerCase().includes('free bonus')) {
            results.loopholes.push({
                title: 'No-Deposit Bonus Available',
                description: 'Site offers bonuses without requiring deposits',
                type: 'free_money',
                profitPotential: 'Very High - Risk-free profit potential'
            });
        }

        // Check for wagering requirements
        const wageringPattern = /wagering?\s*(?:requirement|req)?\s*\d+/gi;
        const wageringMatches = pageText.match(wageringPattern);
        if (wageringMatches) {
            results.loopholes.push({
                title: 'Wagering Requirements',
                description: `Found wagering info: ${wageringMatches.join(', ')}`,
                type: 'bonus_terms'
            });
        }
    }

    checkKnownVulnerabilities(results) {
        // Check for common casino site vulnerabilities

        // Check for outdated jQuery
        const jqueryScripts = document.querySelectorAll('script[src*="jquery"]');
        jqueryScripts.forEach(script => {
            const src = script.src;
            if (src.includes('jquery') && src.match(/jquery-(\d+)\.(\d+)/)) {
                const version = src.match(/jquery-(\d+)\.(\d+)/);
                if (version) {
                    const major = parseInt(version[1]);
                    const minor = parseInt(version[2]);
                    if (major < 3 || (major === 3 && minor < 5)) {
                        results.vulnerabilities.push({
                            title: 'Outdated jQuery',
                            description: `Using jQuery ${major}.${minor} - potential security vulnerabilities`,
                            severity: 'medium',
                            type: 'outdated_software'
                        });
                    }
                }
            }
        });

        // Check for exposed admin panels
        const adminSelectors = [
            'a[href*="admin"]', 'a[href*="wp-admin"]',
            'a[href*="administrator"]', 'form[action*="admin"]'
        ];

        adminSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                results.vulnerabilities.push({
                    title: 'Admin Panel Link Found',
                    description: 'Admin panel link is visible on public page',
                    severity: 'low',
                    type: 'information_disclosure'
                });
            }
        });
    }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'scan') {
        const scanner = new CasinoScanner();
        scanner.scan(request.type).then(results => {
            sendResponse(results);
        });
        return true; // Keep the message channel open for async response
    }
});

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}

function initialize() {
    console.log('🎰 Casino Scanner 4.0 loaded on:', window.location.href);
}
