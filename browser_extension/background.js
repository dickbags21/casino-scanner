// Casino Scanner 4.0 - Background Script

chrome.runtime.onInstalled.addListener(function() {
    console.log('🎰 Casino Scanner 4.0 installed');

    // Create context menu for quick scanning
    chrome.contextMenus.create({
        id: 'casino-scan',
        title: '🔍 Scan for Casino Vulnerabilities',
        contexts: ['page']
    });

    chrome.contextMenus.create({
        id: 'casino-bonus-hunt',
        title: '💰 Hunt for Bonuses & Loopholes',
        contexts: ['page']
    });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(function(info, tab) {
    if (info.menuItemId === 'casino-scan') {
        performBackgroundScan(tab, 'quick');
    } else if (info.menuItemId === 'casino-bonus-hunt') {
        performBackgroundScan(tab, 'bonus');
    }
});

function performBackgroundScan(tab, scanType) {
    // Inject content script if not already loaded
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content.js']
    }, function() {
        // Send scan command
        chrome.tabs.sendMessage(tab.id, {
            action: 'scan',
            type: scanType
        }, function(response) {
            if (response) {
                // Show notification with results summary
                showScanNotification(response);
            }
        });
    });
}

function showScanNotification(results) {
    const vulnCount = results.vulnerabilities ? results.vulnerabilities.length : 0;
    const loopholeCount = results.loopholes ? results.loopholes.length : 0;

    let title = 'Casino Scan Complete';
    let message = `Found ${vulnCount} vulnerabilities, ${loopholeCount} loopholes`;

    if (loopholeCount > 0) {
        title = '💰 Loopholes Found!';
        message = `Discovered ${loopholeCount} potential profit opportunities`;
    } else if (vulnCount > 0) {
        title = '🚨 Vulnerabilities Detected';
        message = `Found ${vulnCount} security issues to investigate`;
    }

    chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon128.png',
        title: title,
        message: message,
        buttons: [
            {title: 'View Details'},
            {title: 'Export Report'}
        ]
    });
}

// Handle notification button clicks
chrome.notifications.onButtonClicked.addListener(function(notificationId, buttonIndex) {
    if (buttonIndex === 0) {
        // View Details - open popup
        chrome.action.openPopup();
    } else if (buttonIndex === 1) {
        // Export Report - trigger download
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {action: 'export_report'});
        });
    }
});

// Handle web requests to monitor casino API calls
chrome.webRequest.onBeforeRequest.addListener(
    function(details) {
        // Monitor API calls that might reveal vulnerabilities
        if (details.url.includes('/api/') || details.url.includes('/graphql')) {
            console.log('🎰 API Call Detected:', details.url);
            // Could store these for analysis
        }
    },
    {urls: ["http://*/*", "https://*/*"]},
    []
);
