// Casino Scanner 4.0 - Popup Script

document.addEventListener('DOMContentLoaded', function() {
    const quickScanBtn = document.getElementById('quick-scan');
    const deepScanBtn = document.getElementById('deep-scan');
    const bonusHunterBtn = document.getElementById('bonus-hunter');
    const exportReportBtn = document.getElementById('export-report');
    const clearResultsBtn = document.getElementById('clear-results');

    const currentUrlDiv = document.getElementById('current-url');
    const resultsContainer = document.getElementById('results-container');
    const resultsContent = document.getElementById('results-content');
    const loadingIndicator = document.getElementById('loading-indicator');
    const vulnsList = document.getElementById('vulns-list');
    const loopholesList = document.getElementById('loopholes-list');

    // Get current tab URL
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        const currentTab = tabs[0];
        currentUrlDiv.textContent = currentTab.url;
    });

    // Quick Scan - Basic vulnerability check
    quickScanBtn.addEventListener('click', function() {
        performScan('quick');
    });

    // Deep Scan - Comprehensive analysis
    deepScanBtn.addEventListener('click', function() {
        performScan('deep');
    });

    // Bonus Hunter - Look for bonuses and loopholes
    bonusHunterBtn.addEventListener('click', function() {
        performScan('bonus');
    });

    // Export Report
    exportReportBtn.addEventListener('click', function() {
        exportReport();
    });

    // Clear Results
    clearResultsBtn.addEventListener('click', function() {
        clearResults();
    });

    function performScan(scanType) {
        showLoading();

        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            const currentTab = tabs[0];

            // Inject scanner script
            chrome.scripting.executeScript({
                target: { tabId: currentTab.id },
                files: ['scanner.js']
            }, function() {
                // Send scan command to content script
                chrome.tabs.sendMessage(currentTab.id, {
                    action: 'scan',
                    type: scanType
                }, function(response) {
                    hideLoading();
                    if (response) {
                        displayResults(response);
                    }
                });
            });
        });
    }

    function showLoading() {
        loadingIndicator.style.display = 'block';
        resultsContent.innerHTML = '';
        vulnsList.innerHTML = '<div class="no-vulns">Scanning...</div>';
        loopholesList.innerHTML = '<div class="no-loopholes">Analyzing...</div>';
    }

    function hideLoading() {
        loadingIndicator.style.display = 'none';
    }

    function displayResults(results) {
        // Clear previous results
        resultsContent.innerHTML = '';
        vulnsList.innerHTML = '';
        loopholesList.innerHTML = '';

        // Display scan summary
        const summary = document.createElement('div');
        summary.innerHTML = `
            <h4>Scan Complete</h4>
            <p><strong>Site:</strong> ${results.url}</p>
            <p><strong>Scan Type:</strong> ${results.scanType}</p>
            <p><strong>Timestamp:</strong> ${new Date(results.timestamp).toLocaleString()}</p>
        `;
        resultsContent.appendChild(summary);

        // Display vulnerabilities
        if (results.vulnerabilities && results.vulnerabilities.length > 0) {
            results.vulnerabilities.forEach(vuln => {
                const vulnDiv = document.createElement('div');
                vulnDiv.className = `vuln-item ${vuln.severity}`;
                vulnDiv.innerHTML = `
                    <div class="vuln-title">${vuln.title}</div>
                    <div class="vuln-desc">${vuln.description}</div>
                    <div class="vuln-severity">Severity: ${vuln.severity.toUpperCase()}</div>
                `;
                vulnsList.appendChild(vulnDiv);
            });
        } else {
            vulnsList.innerHTML = '<div class="no-vulns">No vulnerabilities detected</div>';
        }

        // Display loopholes and opportunities
        if (results.loopholes && results.loopholes.length > 0) {
            results.loopholes.forEach(loophole => {
                const loopholeDiv = document.createElement('div');
                loopholeDiv.className = 'loophole-item';
                loopholeDiv.innerHTML = `
                    <div class="loophole-title">${loophole.title}</div>
                    <div class="loophole-desc">${loophole.description}</div>
                    ${loophole.profitPotential ? `<div class="profit-potential">💰 Potential: ${loophole.profitPotential}</div>` : ''}
                `;
                loopholesList.appendChild(loopholeDiv);
            });
        } else {
            loopholesList.innerHTML = '<div class="no-loopholes">No loopholes found</div>';
        }

        // Store results for export
        localStorage.setItem('lastScanResults', JSON.stringify(results));
    }

    function exportReport() {
        const results = localStorage.getItem('lastScanResults');
        if (!results) {
            alert('No scan results to export. Please run a scan first.');
            return;
        }

        const data = JSON.parse(results);
        const report = {
            timestamp: new Date().toISOString(),
            scanner: 'Casino Scanner 4.0',
            results: data
        };

        const blob = new Blob([JSON.stringify(report, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);

        chrome.downloads.download({
            url: url,
            filename: `casino-scan-report-${Date.now()}.json`
        });
    }

    function clearResults() {
        resultsContent.innerHTML = '';
        vulnsList.innerHTML = '<div class="no-vulns">No vulnerabilities detected</div>';
        loopholesList.innerHTML = '<div class="no-loopholes">No loopholes found</div>';
        localStorage.removeItem('lastScanResults');
    }

    // Load last results if available
    const lastResults = localStorage.getItem('lastScanResults');
    if (lastResults) {
        try {
            displayResults(JSON.parse(lastResults));
        } catch (e) {
            console.error('Error loading last results:', e);
        }
    }
});
