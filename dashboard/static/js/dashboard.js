// Dashboard JavaScript

let ws = null;
let scanStatusChart = null;
let vulnSeverityChart = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadDarkMode(); // Load dark mode preference
    connectWebSocket();
    loadStats();
    loadScans();
    loadVulnerabilities();
    loadTargets();
    loadPlugins();
    initializeCharts();
    initializeTerminal();
    initializeCommandPalette();
    initializeKeyboardShortcuts();
    
    // Refresh stats every 5 seconds
    setInterval(loadStats, 5000);
    
    // Auto-refresh scans if on scans view
    setInterval(() => {
        const scansView = document.getElementById('scans-view');
        if (scansView && scansView.classList.contains('active')) {
            loadScans();
        }
    }, 10000); // Every 10 seconds
});

// WebSocket connection
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
    
    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.type === 'scan_progress') {
            updateScanProgress(message);
        }
    };
    
    ws.onclose = () => {
        setTimeout(connectWebSocket, 3000);
    };
}

// View navigation
function showView(viewName) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    
    const view = document.getElementById(`${viewName}-view`);
    if (view) {
        view.classList.add('active');
    }
    
    // Find and activate the clicked nav link
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.textContent.toLowerCase().includes(viewName.toLowerCase())) {
            link.classList.add('active');
        }
    });
    
    // Reload data for the view
    if (viewName === 'scans') {
        loadScans();
    } else if (viewName === 'vulnerabilities') {
        loadVulnerabilities();
    } else if (viewName === 'targets') {
        loadTargets();
    } else if (viewName === 'plugins') {
        loadPlugins();
    } else if (viewName === 'terminal') {
        focusTerminal();
    }
}

// Load dashboard statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        document.getElementById('stat-total-scans').textContent = stats.scans.total;
        document.getElementById('stat-running-scans').textContent = stats.scans.running;
        document.getElementById('stat-vulnerabilities').textContent = stats.vulnerabilities.total;
        document.getElementById('stat-critical').textContent = stats.vulnerabilities.critical;
        
        // Update charts
        if (scanStatusChart) {
            scanStatusChart.data.datasets[0].data = [
                stats.scans.completed,
                stats.scans.running,
                stats.scans.pending,
                stats.scans.failed
            ];
            scanStatusChart.update('none'); // 'none' = no animation for auto-updates
        }
        
        if (vulnSeverityChart) {
            vulnSeverityChart.data.datasets[0].data = [
                stats.vulnerabilities.critical,
                stats.vulnerabilities.high,
                stats.vulnerabilities.medium,
                stats.vulnerabilities.low
            ];
            vulnSeverityChart.update('none');
        }
        
        // Load recent scans
        loadRecentScans();
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Initialize charts
function initializeCharts() {
    // Scan status chart
    const scanCtx = document.getElementById('scan-status-chart').getContext('2d');
    scanStatusChart = new Chart(scanCtx, {
        type: 'doughnut',
        data: {
            labels: ['Completed', 'Running', 'Pending', 'Failed'],
            datasets: [{
                data: [0, 0, 0, 0],
                backgroundColor: ['#28a745', '#17a2b8', '#ffc107', '#dc3545']
            }]
        }
    });
    
    // Vulnerability severity chart
    const vulnCtx = document.getElementById('vuln-severity-chart').getContext('2d');
    vulnSeverityChart = new Chart(vulnCtx, {
        type: 'bar',
        data: {
            labels: ['Critical', 'High', 'Medium', 'Low'],
            datasets: [{
                label: 'Vulnerabilities',
                data: [0, 0, 0, 0],
                backgroundColor: ['#dc3545', '#fd7e14', '#ffc107', '#28a745']
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

let allScans = []; // Store all scans for filtering

// Load scans
async function loadScans() {
    try {
        const status = document.getElementById('filter-status')?.value || '';
        const url = status ? `/api/scans?status=${status}&limit=100` : '/api/scans?limit=100';
        const response = await fetch(url);
        const data = await response.json();
        
        allScans = data.scans; // Store for search filtering
        displayScans(allScans);
    } catch (error) {
        console.error('Error loading scans:', error);
    }
}

// Display scans (used by loadScans and filterScans)
function displayScans(scans) {
    const list = document.getElementById('scans-list');
    list.innerHTML = '';
    
    if (scans.length === 0) {
        list.innerHTML = '<div style="text-align: center; padding: 2rem; color: #666;">No scans found</div>';
        return;
    }
    
    scans.forEach(scan => {
        const item = document.createElement('div');
        item.className = 'scan-item';
        item.setAttribute('data-scan-id', scan.scan_id);
        item.setAttribute('data-scan-name', scan.name.toLowerCase());
        item.setAttribute('data-scan-type', scan.scan_type.toLowerCase());
        item.onclick = () => showScanDetail(scan.scan_id);
        
        const progress = scan.progress * 100;
        const createdDate = scan.created_at ? new Date(scan.created_at).toLocaleString() : 'Unknown';
        item.innerHTML = `
            <div class="scan-header">
                <div class="scan-title">${scan.name}</div>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    <span class="status-badge status-${scan.status}">${scan.status}</span>
                    <button onclick="event.stopPropagation(); exportScan('${scan.scan_id}')" class="btn" style="padding: 0.25rem 0.5rem; font-size: 0.85rem;" title="Export scan">📥</button>
                </div>
            </div>
            <div>Type: ${scan.scan_type} | Plugin: ${scan.plugin_name}</div>
            <div>Created: ${createdDate}</div>
            ${scan.status === 'running' || scan.status === 'pending' ? `
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progress}%"></div>
                </div>
            ` : ''}
            ${scan.error_message ? `<div style="color: #dc3545; margin-top: 0.5rem;">Error: ${scan.error_message}</div>` : ''}
        `;
        list.appendChild(item);
    });
}

// Filter scans by search term
function filterScans() {
    const searchTerm = document.getElementById('search-scans')?.value.toLowerCase() || '';
    if (!searchTerm) {
        displayScans(allScans);
        return;
    }
    
    const filtered = allScans.filter(scan => 
        scan.name.toLowerCase().includes(searchTerm) ||
        scan.scan_type.toLowerCase().includes(searchTerm) ||
        scan.plugin_name.toLowerCase().includes(searchTerm) ||
        (scan.region && scan.region.toLowerCase().includes(searchTerm))
    );
    displayScans(filtered);
}

// Export scan
async function exportScan(scanId) {
    try {
        const response = await fetch(`/api/scans/${scanId}/export?format=json`);
        if (response.ok) {
            const data = await response.json();
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `scan_${scanId}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } else {
            alert('Error exporting scan');
        }
    } catch (error) {
        console.error('Error exporting scan:', error);
        alert('Error exporting scan');
    }
}

// Load recent scans for dashboard
async function loadRecentScans() {
    try {
        const response = await fetch('/api/scans?limit=5');
        const data = await response.json();
        
        const list = document.getElementById('recent-scans-list');
        list.innerHTML = '';
        
        data.scans.forEach(scan => {
            const item = document.createElement('div');
            item.className = 'scan-item';
            item.onclick = () => showScanDetail(scan.scan_id);
            item.innerHTML = `
                <div class="scan-header">
                    <div class="scan-title">${scan.name}</div>
                    <span class="status-badge status-${scan.status}">${scan.status}</span>
                </div>
                <div>${scan.scan_type} | ${new Date(scan.created_at).toLocaleString()}</div>
            `;
            list.appendChild(item);
        });
    } catch (error) {
        console.error('Error loading recent scans:', error);
    }
}

// Show scan detail
async function showScanDetail(scanId) {
    try {
        const response = await fetch(`/api/scans/${scanId}`);
        const scan = await response.json();
        
        const modal = document.getElementById('scan-detail-modal');
        const content = document.getElementById('scan-detail-content');
        
        content.innerHTML = `
            <h2>${scan.name}</h2>
            <p><strong>Status:</strong> <span class="status-badge status-${scan.status}">${scan.status}</span></p>
            <p><strong>Type:</strong> ${scan.scan_type}</p>
            <p><strong>Plugin:</strong> ${scan.plugin_name}</p>
            <p><strong>Progress:</strong> ${(scan.progress * 100).toFixed(1)}%</p>
            <h3>Results (${scan.results.length})</h3>
            <div id="scan-results"></div>
            <h3>Vulnerabilities (${scan.vulnerabilities.length})</h3>
            <div id="scan-vulns"></div>
        `;
        
        const resultsDiv = document.getElementById('scan-results');
        scan.results.forEach(result => {
            const div = document.createElement('div');
            div.className = 'scan-item';
            div.innerHTML = `
                <strong>${result.result_type}</strong><br>
                ${result.target_url || result.target_ip || 'N/A'}<br>
                Success: ${result.success}
            `;
            resultsDiv.appendChild(div);
        });
        
        const vulnsDiv = document.getElementById('scan-vulns');
        scan.vulnerabilities.forEach(vuln => {
            const div = document.createElement('div');
            div.className = 'vuln-item';
            div.innerHTML = `
                <div class="vuln-header">
                    <div class="vuln-title">${vuln.title}</div>
                    <span class="severity-badge severity-${vuln.severity}">${vuln.severity}</span>
                </div>
                <p>${vuln.description}</p>
            `;
            vulnsDiv.appendChild(div);
        });
        
        modal.setAttribute('data-scan-id', scanId);
        modal.classList.add('active');
        
        // Show/hide cancel button
        updateCancelButton(scan);
        
        // Subscribe to scan updates
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'subscribe', scan_id: scanId }));
        }
    } catch (error) {
        console.error('Error loading scan detail:', error);
    }
}

// Update scan progress
function updateScanProgress(message) {
    // Update progress bars for running scans
    const scanItems = document.querySelectorAll('.scan-item');
    scanItems.forEach(item => {
        const scanId = item.getAttribute('data-scan-id');
        if (scanId === message.scan_id) {
            const progressBar = item.querySelector('.progress-fill');
            if (progressBar) {
                progressBar.style.width = `${message.progress * 100}%`;
            }
            const statusBadge = item.querySelector('.status-badge');
            if (statusBadge) {
                statusBadge.className = `status-badge status-${message.status}`;
                statusBadge.textContent = message.status;
            }
        }
    });
    
    // If viewing scan detail, update it
    const detailModal = document.getElementById('scan-detail-modal');
    if (detailModal && detailModal.classList.contains('active')) {
        const scanId = detailModal.getAttribute('data-scan-id');
        if (scanId === message.scan_id) {
            showScanDetail(scanId); // Refresh detail view
        }
    }
}

let allVulnerabilities = []; // Store for filtering

// Load vulnerabilities
async function loadVulnerabilities() {
    try {
        const severity = document.getElementById('filter-severity')?.value || '';
        const url = severity ? `/api/vulnerabilities?severity=${severity}&limit=200` : '/api/vulnerabilities?limit=200';
        const response = await fetch(url);
        const data = await response.json();
        
        allVulnerabilities = data.vulnerabilities;
        displayVulnerabilities(allVulnerabilities);
    } catch (error) {
        console.error('Error loading vulnerabilities:', error);
    }
}

// Display vulnerabilities
function displayVulnerabilities(vulns) {
    const list = document.getElementById('vulnerabilities-list');
    list.innerHTML = '';
    
    if (vulns.length === 0) {
        list.innerHTML = '<div style="text-align: center; padding: 2rem; color: #666;">No vulnerabilities found</div>';
        return;
    }
    
    vulns.forEach(vuln => {
        const item = document.createElement('div');
        item.className = 'vuln-item';
        item.setAttribute('data-vuln-title', vuln.title.toLowerCase());
        item.setAttribute('data-vuln-type', (vuln.vulnerability_type || '').toLowerCase());
        item.innerHTML = `
            <div class="vuln-header">
                <div class="vuln-title">${vuln.title}</div>
                <span class="severity-badge severity-${vuln.severity}">${vuln.severity}</span>
            </div>
            <p>${vuln.description}</p>
            <div>Type: ${vuln.vulnerability_type || 'N/A'} | URL: ${vuln.url || 'N/A'}</div>
            <div>Discovered: ${vuln.discovered_at ? new Date(vuln.discovered_at).toLocaleString() : 'Unknown'}</div>
        `;
        list.appendChild(item);
    });
}

// Filter vulnerabilities
function filterVulnerabilities() {
    const searchTerm = document.getElementById('search-vulns')?.value.toLowerCase() || '';
    if (!searchTerm) {
        displayVulnerabilities(allVulnerabilities);
        return;
    }
    
    const filtered = allVulnerabilities.filter(vuln => 
        vuln.title.toLowerCase().includes(searchTerm) ||
        (vuln.description && vuln.description.toLowerCase().includes(searchTerm)) ||
        (vuln.vulnerability_type && vuln.vulnerability_type.toLowerCase().includes(searchTerm)) ||
        (vuln.url && vuln.url.toLowerCase().includes(searchTerm))
    );
    displayVulnerabilities(filtered);
}

let allTargets = []; // Store for filtering

// Load targets
async function loadTargets() {
    try {
        const status = document.getElementById('filter-target-status')?.value || '';
        const url = status ? `/api/targets?status=${status}` : '/api/targets';
        const response = await fetch(url);
        const data = await response.json();
        
        allTargets = data.targets;
        displayTargets(allTargets);
    } catch (error) {
        console.error('Error loading targets:', error);
        showMessage('Error loading targets', 'error');
    }
}

// Display targets
function displayTargets(targets) {
    const list = document.getElementById('targets-list');
    list.innerHTML = '';
    
    if (targets.length === 0) {
        list.innerHTML = '<div style="text-align: center; padding: 2rem; color: #666;">No targets found. Add your first target to get started!</div>';
        return;
    }
    
    targets.forEach(target => {
        const item = document.createElement('div');
        item.className = 'target-item';
        item.setAttribute('data-target-id', target.id);
        item.setAttribute('data-target-name', (target.name || '').toLowerCase());
        item.setAttribute('data-target-url', (target.url || '').toLowerCase());
        
        const priorityColors = {
            10: '#dc3545', 9: '#dc3545', 8: '#fd7e14',
            7: '#ffc107', 6: '#ffc107', 5: '#28a745',
            4: '#28a745', 3: '#6c757d', 2: '#6c757d', 1: '#6c757d'
        };
        const priorityColor = priorityColors[target.priority] || '#6c757d';
        
        item.innerHTML = `
            <div class="scan-header">
                <div>
                    <div class="scan-title">${target.name || target.url}</div>
                    <div style="font-size: 0.85rem; color: #666; margin-top: 0.25rem;">${target.url}</div>
                </div>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    <span class="status-badge status-${target.status}">${target.status}</span>
                    <span style="background: ${priorityColor}; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem;">P${target.priority}</span>
                </div>
            </div>
            <div style="display: flex; gap: 1rem; margin-top: 1rem; flex-wrap: wrap;">
                ${target.region ? `<div><strong>Region:</strong> ${target.region}</div>` : ''}
                ${target.country_code ? `<div><strong>Country:</strong> ${target.country_code}</div>` : ''}
                ${target.tags && target.tags.length > 0 ? `<div><strong>Tags:</strong> ${target.tags.join(', ')}</div>` : ''}
                ${target.last_scan_at ? `<div><strong>Last Scan:</strong> ${new Date(target.last_scan_at).toLocaleString()}</div>` : '<div style="color: #999;">Never scanned</div>'}
            </div>
            ${target.notes ? `<div style="margin-top: 0.5rem; padding: 0.5rem; background: rgba(0,0,0,0.05); border-radius: 4px; font-size: 0.9rem;">${target.notes}</div>` : ''}
            <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
                <button onclick="event.stopPropagation(); scanTarget(${target.id})" class="btn btn-primary" style="padding: 0.5rem 1rem; font-size: 0.9rem;">🚀 Scan Now</button>
                <button onclick="event.stopPropagation(); showTargetDetail(${target.id})" class="btn" style="padding: 0.5rem 1rem; font-size: 0.9rem;">📋 Details</button>
                <button onclick="event.stopPropagation(); editTarget(${target.id})" class="btn" style="padding: 0.5rem 1rem; font-size: 0.9rem;">✏️ Edit</button>
                <button onclick="event.stopPropagation(); deleteTarget(${target.id})" class="btn btn-danger" style="padding: 0.5rem 1rem; font-size: 0.9rem;">🗑️ Delete</button>
            </div>
        `;
        list.appendChild(item);
    });
}

// Filter targets
function filterTargets() {
    const searchTerm = document.getElementById('search-targets')?.value.toLowerCase() || '';
    if (!searchTerm) {
        displayTargets(allTargets);
        return;
    }
    
    const filtered = allTargets.filter(target => 
        (target.name && target.name.toLowerCase().includes(searchTerm)) ||
        (target.url && target.url.toLowerCase().includes(searchTerm)) ||
        (target.region && target.region.toLowerCase().includes(searchTerm)) ||
        (target.tags && target.tags.some(tag => tag.toLowerCase().includes(searchTerm)))
    );
    displayTargets(filtered);
}

// Show new target modal
function showNewTargetModal() {
    const modal = document.getElementById('new-target-modal');
    modal.classList.add('active');
    document.getElementById('new-target-form').reset();
}

// Create target
async function createTarget(event) {
    event.preventDefault();
    
    const url = document.getElementById('target-url').value.trim();
    const name = document.getElementById('target-name').value.trim();
    const region = document.getElementById('target-region').value;
    const priority = parseInt(document.getElementById('target-priority').value) || 5;
    const tagsInput = document.getElementById('target-tags').value.trim();
    const notes = document.getElementById('target-notes').value.trim();
    
    const tags = tagsInput ? tagsInput.split(',').map(t => t.trim()).filter(t => t) : [];
    
    const targetData = {
        url: url,
        name: name || url,
        region: region || null,
        priority: priority,
        tags: tags,
        notes: notes || null
    };
    
    try {
        const response = await fetch('/api/targets', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(targetData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            closeModal('new-target-modal');
            loadTargets();
            showMessage(`Target "${result.target.name}" added successfully!`, 'success');
        } else {
            showMessage(`Error: ${result.detail || 'Failed to create target'}`, 'error');
        }
    } catch (error) {
        console.error('Error creating target:', error);
        showMessage(`Error creating target: ${error.message}`, 'error');
    }
}

// Scan target
async function scanTarget(targetId) {
    try {
        const response = await fetch(`/api/targets/${targetId}/scan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ plugin: 'browser', scan_type: 'signup' })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage(`Scan started for target!`, 'success');
            showView('scans');
            loadScans();
        } else {
            showMessage(`Error: ${result.detail || 'Failed to start scan'}`, 'error');
        }
    } catch (error) {
        console.error('Error scanning target:', error);
        showMessage(`Error starting scan: ${error.message}`, 'error');
    }
}

// Show target detail
async function showTargetDetail(targetId) {
    try {
        const response = await fetch(`/api/targets/${targetId}`);
        const target = await response.json();
        
        const modal = document.getElementById('target-detail-modal');
        const content = document.getElementById('target-detail-content');
        
        content.innerHTML = `
            <h2>${target.name || target.url}</h2>
            <div style="margin-top: 1.5rem;">
                <p><strong>URL:</strong> ${target.url}</p>
                <p><strong>Status:</strong> <span class="status-badge status-${target.status}">${target.status}</span></p>
                <p><strong>Priority:</strong> ${target.priority}/10</p>
                ${target.region ? `<p><strong>Region:</strong> ${target.region}</p>` : ''}
                ${target.country_code ? `<p><strong>Country:</strong> ${target.country_code}</p>` : ''}
                ${target.tags && target.tags.length > 0 ? `<p><strong>Tags:</strong> ${target.tags.join(', ')}</p>` : ''}
                ${target.notes ? `<p><strong>Notes:</strong><br>${target.notes}</p>` : ''}
                <p><strong>Created:</strong> ${target.created_at ? new Date(target.created_at).toLocaleString() : 'Unknown'}</p>
                <p><strong>Last Scan:</strong> ${target.last_scan_at ? new Date(target.last_scan_at).toLocaleString() : 'Never'}</p>
            </div>
            <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #ddd;">
                <button onclick="scanTarget(${target.id})" class="btn btn-primary">🚀 Scan Now</button>
                <button onclick="editTarget(${target.id})" class="btn">✏️ Edit</button>
                <button onclick="closeModal('target-detail-modal')" class="btn">Close</button>
            </div>
        `;
        
        modal.classList.add('active');
    } catch (error) {
        console.error('Error loading target detail:', error);
        showMessage('Error loading target details', 'error');
    }
}

// Edit target
async function editTarget(targetId) {
    // For now, just show detail and allow editing there
    // Could implement inline editing or separate edit modal
    showTargetDetail(targetId);
}

// Delete target
async function deleteTarget(targetId) {
    if (!confirm('Are you sure you want to delete this target?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/targets/${targetId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showMessage('Target deleted successfully', 'success');
            loadTargets();
        } else {
            showMessage('Error deleting target', 'error');
        }
    } catch (error) {
        console.error('Error deleting target:', error);
        showMessage('Error deleting target', 'error');
    }
}

// Show message helper
function showMessage(text, type = 'success') {
    const message = document.createElement('div');
    message.className = `message message-${type}`;
    message.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 10000; min-width: 300px;';
    message.textContent = text;
    document.body.appendChild(message);
    setTimeout(() => {
        message.style.opacity = '0';
        message.style.transition = 'opacity 0.3s';
        setTimeout(() => message.remove(), 300);
    }, 3000);
}

// Dark mode toggle
function toggleDarkMode() {
    const body = document.body;
    const isDark = body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', isDark);
    document.getElementById('theme-icon').textContent = isDark ? '☀️' : '🌙';
}

// Load dark mode preference
function loadDarkMode() {
    const saved = localStorage.getItem('darkMode');
    if (saved === 'true' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.body.classList.add('dark-mode');
        document.getElementById('theme-icon').textContent = '☀️';
    }
}

// Load plugins
async function loadPlugins() {
    try {
        const response = await fetch('/api/plugins');
        const data = await response.json();
        
        const list = document.getElementById('plugins-list');
        list.innerHTML = '';
        
        data.plugins.forEach(plugin => {
            const item = document.createElement('div');
            item.className = 'plugin-item';
            item.innerHTML = `
                <div class="plugin-info">
                    <h3>${plugin.display_name}</h3>
                    <p>${plugin.description}</p>
                    <p>Version: ${plugin.version} | Running scans: ${plugin.running_scans}</p>
                </div>
                <div class="plugin-actions">
                    <label class="toggle-switch">
                        <input type="checkbox" ${plugin.enabled ? 'checked' : ''} 
                               onchange="togglePlugin('${plugin.name}', this.checked)">
                        <span class="toggle-slider"></span>
                    </label>
                </div>
            `;
            list.appendChild(item);
        });
        
        // Populate plugin select for new scan
        const select = document.getElementById('scan-plugin');
        if (select) {
            select.innerHTML = '<option value="">Select plugin...</option>';
            data.plugins.filter(p => p.enabled).forEach(plugin => {
                const option = document.createElement('option');
                option.value = plugin.name;
                option.textContent = plugin.display_name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading plugins:', error);
    }
}

// Toggle plugin
async function togglePlugin(pluginName, enabled) {
    try {
        const endpoint = enabled ? 'enable' : 'disable';
        await fetch(`/api/plugins/${pluginName}/${endpoint}`, { method: 'POST' });
        loadPlugins();
    } catch (error) {
        console.error('Error toggling plugin:', error);
    }
}

// Show new scan modal
function showNewScanModal() {
    const modal = document.getElementById('new-scan-modal');
    modal.classList.add('active');
    document.getElementById('scan-name').value = '';
    document.getElementById('scan-config').innerHTML = '';
    loadPlugins();
}

// Update scan config based on selected plugin
function updateScanConfig() {
    const plugin = document.getElementById('scan-plugin').value;
    const configDiv = document.getElementById('scan-config');
    configDiv.innerHTML = '';
    
    if (plugin === 'shodan') {
        configDiv.innerHTML = `
            <div class="form-group">
                <label>Shodan Query:</label>
                <input type="text" id="scan-query" placeholder="e.g., casino country:VN" required>
            </div>
            <div class="form-group">
                <label>Limit (optional):</label>
                <input type="number" id="scan-limit" value="100" min="1" max="1000">
            </div>
        `;
    } else if (plugin === 'browser') {
        configDiv.innerHTML = `
            <div class="form-group">
                <label>Target URL:</label>
                <input type="url" id="scan-url" placeholder="https://example.com" required>
            </div>
            <div class="form-group">
                <label>Scan Type:</label>
                <select id="scan-scan-type">
                    <option value="signup">Signup Flow</option>
                    <option value="bonus">Bonus Code</option>
                </select>
            </div>
        `;
    } else if (plugin === 'account_creation') {
        configDiv.innerHTML = `
            <div class="form-group">
                <label>Target URL:</label>
                <input type="url" id="scan-url" placeholder="https://example.com" required>
            </div>
        `;
    } else if (plugin === 'mobile_app') {
        configDiv.innerHTML = `
            <div class="form-group">
                <label>App Path:</label>
                <input type="text" id="scan-app-path" placeholder="/path/to/app.apk" required>
            </div>
            <div class="form-group">
                <label>Platform:</label>
                <select id="scan-platform">
                    <option value="android">Android</option>
                    <option value="ios">iOS</option>
                </select>
            </div>
        `;
    }
}

// Create scan
async function createScan(event) {
    event.preventDefault();
    
    const plugin = document.getElementById('scan-plugin').value;
    const name = document.getElementById('scan-name').value;
    
    if (!plugin || !name) {
        alert('Please fill in all required fields');
        return;
    }
    
    const config = {
        plugin: plugin,
        name: name,
        scan_type: plugin
    };
    
    // Add plugin-specific config
    if (plugin === 'shodan') {
        const query = document.getElementById('scan-query')?.value;
        const limit = document.getElementById('scan-limit')?.value;
        if (!query) {
            alert('Shodan query is required');
            return;
        }
        config.query = query;
        if (limit) config.limit = parseInt(limit);
    } else if (plugin === 'browser') {
        const url = document.getElementById('scan-url')?.value;
        const scanType = document.getElementById('scan-scan-type')?.value || 'signup';
        if (!url) {
            alert('Target URL is required');
            return;
        }
        config.url = url;
        config.scan_type = scanType;
    } else if (plugin === 'account_creation') {
        const url = document.getElementById('scan-url')?.value;
        if (!url) {
            alert('Target URL is required');
            return;
        }
        config.url = url;
    } else if (plugin === 'mobile_app') {
        const appPath = document.getElementById('scan-app-path')?.value;
        const platform = document.getElementById('scan-platform')?.value || 'android';
        if (!appPath) {
            alert('App path is required');
            return;
        }
        config.app_path = appPath;
        config.platform = platform;
    }
    
    try {
        const response = await fetch('/api/scans', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            closeModal('new-scan-modal');
            loadScans();
            showView('scans');
            // Show success message
            const message = document.createElement('div');
            message.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #28a745; color: white; padding: 1rem; border-radius: 4px; z-index: 10000;';
            message.textContent = `Scan "${name}" started successfully!`;
            document.body.appendChild(message);
            setTimeout(() => message.remove(), 3000);
        } else {
            alert(`Error creating scan: ${result.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error creating scan:', error);
        alert(`Error creating scan: ${error.message}`);
    }
}

// Close modal
function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Cancel scan
async function cancelScan() {
    const modal = document.getElementById('scan-detail-modal');
    const scanId = modal.getAttribute('data-scan-id');
    
    if (!scanId) return;
    
    if (!confirm('Are you sure you want to cancel this scan?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/scans/${scanId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            closeModal('scan-detail-modal');
            loadScans();
            showView('scans');
        } else {
            alert('Error cancelling scan');
        }
    } catch (error) {
        console.error('Error cancelling scan:', error);
        alert('Error cancelling scan');
    }
}

// Show cancel button if scan is running
function updateCancelButton(scan) {
    const cancelBtn = document.getElementById('cancel-scan-btn');
    if (cancelBtn) {
        if (scan.status === 'running' || scan.status === 'pending') {
            cancelBtn.style.display = 'inline-block';
        } else {
            cancelBtn.style.display = 'none';
        }
    }
}

// ==================== TERMINAL FUNCTIONALITY ====================

let terminalHistory = [];
let terminalHistoryIndex = -1;

function initializeTerminal() {
    const terminalInput = document.getElementById('terminal-input');
    const terminalOutput = document.getElementById('terminal-output');
    
    if (!terminalInput || !terminalOutput) return;
    
    // Welcome message
    addTerminalLine('Welcome to Casino Scanner Terminal', 'info');
    addTerminalLine('Type "help" for available commands or press Ctrl+U for command palette', 'info');
    addTerminalLine('');
    
    terminalInput.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter') {
            const command = terminalInput.value.trim();
            if (command) {
                terminalHistory.push(command);
                terminalHistoryIndex = terminalHistory.length;
                addTerminalLine(`casino@scanner:~$ ${command}`, 'info');
                terminalInput.value = '';
                await executeTerminalCommand(command);
            }
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (terminalHistoryIndex > 0) {
                terminalHistoryIndex--;
                terminalInput.value = terminalHistory[terminalHistoryIndex];
            }
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (terminalHistoryIndex < terminalHistory.length - 1) {
                terminalHistoryIndex++;
                terminalInput.value = terminalHistory[terminalHistoryIndex];
            } else {
                terminalHistoryIndex = terminalHistory.length;
                terminalInput.value = '';
            }
        }
    });
}

function focusTerminal() {
    const terminalInput = document.getElementById('terminal-input');
    if (terminalInput) {
        setTimeout(() => terminalInput.focus(), 100);
    }
}

function addTerminalLine(text, type = 'info') {
    const terminalOutput = document.getElementById('terminal-output');
    if (!terminalOutput) return;
    
    const line = document.createElement('div');
    line.className = `terminal-line ${type}`;
    line.textContent = text;
    terminalOutput.appendChild(line);
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

async function executeTerminalCommand(command) {
    const parts = command.split(' ');
    const cmd = parts[0].toLowerCase();
    const args = parts.slice(1);
    
    try {
        switch (cmd) {
            case 'help':
                showTerminalHelp();
                break;
            case 'scan':
                await terminalScan(args);
                break;
            case 'targets':
                await terminalListTargets();
                break;
            case 'plugins':
                await terminalListPlugins();
                break;
            case 'stats':
                await terminalStats();
                break;
            case 'clear':
                clearTerminal();
                break;
            case 'browser':
                await terminalBrowserCommand(args);
                break;
            default:
                // Try to execute via API
                const response = await fetch('/api/terminal/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command, args })
                });
                const result = await response.json();
                if (result.success) {
                    addTerminalLine(result.output, 'success');
                } else {
                    addTerminalLine(`Error: ${result.error || 'Unknown command'}`, 'error');
                    addTerminalLine(`Type "help" for available commands`, 'info');
                }
        }
    } catch (error) {
        addTerminalLine(`Error: ${error.message}`, 'error');
    }
}

function showTerminalHelp() {
    const help = [
        'Available Commands:',
        '  help              - Show this help message',
        '  scan <url>        - Start a browser scan on URL',
        '  targets           - List all targets',
        '  plugins           - List all plugins',
        '  stats             - Show dashboard statistics',
        '  browser <cmd>     - Browser control commands',
        '  clear             - Clear terminal',
        '',
        'Browser Commands:',
        '  browser start     - Start browser instance',
        '  browser stop      - Stop browser instance',
        '  browser status    - Check browser status',
        '',
        'Shortcuts:',
        '  Ctrl+U            - Open command palette',
        '  Ctrl+K            - Open command palette',
        '  Arrow Up/Down     - Navigate command history'
    ];
    help.forEach(line => addTerminalLine(line, 'info'));
}

async function terminalScan(args) {
    if (args.length === 0) {
        addTerminalLine('Usage: scan <url> [scan_type]', 'error');
        return;
    }
    const url = args[0];
    const scanType = args[1] || 'signup';
    
    addTerminalLine(`Starting scan on ${url}...`, 'info');
    try {
        const response = await fetch('/api/scans', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                plugin: 'browser',
                name: `Terminal scan: ${url}`,
                url: url,
                scan_type: scanType
            })
        });
        const result = await response.json();
        if (response.ok) {
            addTerminalLine(`Scan started: ${result.scan_id}`, 'success');
            addTerminalLine(`View in dashboard: /scans`, 'info');
        } else {
            addTerminalLine(`Error: ${result.detail}`, 'error');
        }
    } catch (error) {
        addTerminalLine(`Error: ${error.message}`, 'error');
    }
}

async function terminalListTargets() {
    try {
        const response = await fetch('/api/targets');
        const data = await response.json();
        if (data.targets.length === 0) {
            addTerminalLine('No targets found', 'warning');
            return;
        }
        addTerminalLine(`Found ${data.targets.length} target(s):`, 'info');
        data.targets.forEach(target => {
            addTerminalLine(`  [${target.status}] ${target.name || target.url} (Priority: ${target.priority})`, 'info');
        });
    } catch (error) {
        addTerminalLine(`Error: ${error.message}`, 'error');
    }
}

async function terminalListPlugins() {
    try {
        const response = await fetch('/api/plugins');
        const data = await response.json();
        addTerminalLine('Available Plugins:', 'info');
        data.plugins.forEach(plugin => {
            const status = plugin.enabled ? 'ENABLED' : 'DISABLED';
            const color = plugin.enabled ? 'success' : 'warning';
            addTerminalLine(`  [${status}] ${plugin.display_name} v${plugin.version}`, color);
        });
    } catch (error) {
        addTerminalLine(`Error: ${error.message}`, 'error');
    }
}

async function terminalStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        addTerminalLine('Dashboard Statistics:', 'info');
        addTerminalLine(`  Total Scans: ${stats.scans.total}`, 'info');
        addTerminalLine(`  Running: ${stats.scans.running}`, 'info');
        addTerminalLine(`  Vulnerabilities: ${stats.vulnerabilities.total} (${stats.vulnerabilities.critical} critical)`, 'info');
        addTerminalLine(`  Targets: ${stats.targets.total}`, 'info');
    } catch (error) {
        addTerminalLine(`Error: ${error.message}`, 'error');
    }
}

async function terminalBrowserCommand(args) {
    if (args.length === 0) {
        addTerminalLine('Usage: browser <start|stop|status>', 'error');
        return;
    }
    const subcmd = args[0].toLowerCase();
    try {
        const response = await fetch(`/api/browser/${subcmd}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const result = await response.json();
        if (response.ok) {
            addTerminalLine(result.message || 'Success', 'success');
        } else {
            addTerminalLine(`Error: ${result.detail}`, 'error');
        }
    } catch (error) {
        addTerminalLine(`Error: ${error.message}`, 'error');
    }
}

function clearTerminal() {
    const terminalOutput = document.getElementById('terminal-output');
    if (terminalOutput) {
        terminalOutput.innerHTML = '';
    }
}

// ==================== COMMAND PALETTE ====================

const commands = [
    { name: 'New Scan', action: () => showNewScanModal(), shortcut: 'Ctrl+N', desc: 'Create a new scan' },
    { name: 'New Target', action: () => showNewTargetModal(), shortcut: 'Ctrl+T', desc: 'Add a new target' },
    { name: 'Dashboard', action: () => showView('dashboard'), shortcut: 'Ctrl+D', desc: 'Go to dashboard' },
    { name: 'Scans', action: () => showView('scans'), shortcut: 'Ctrl+S', desc: 'View all scans' },
    { name: 'Vulnerabilities', action: () => showView('vulnerabilities'), shortcut: 'Ctrl+V', desc: 'View vulnerabilities' },
    { name: 'Targets', action: () => showView('targets'), desc: 'View targets' },
    { name: 'Plugins', action: () => showView('plugins'), desc: 'View plugins' },
    { name: 'Terminal', action: () => showView('terminal'), shortcut: 'Ctrl+`', desc: 'Open terminal' },
    { name: 'Toggle Dark Mode', action: () => toggleDarkMode(), shortcut: 'Ctrl+Shift+D', desc: 'Toggle dark/light mode' },
    { name: 'Refresh Stats', action: () => loadStats(), desc: 'Refresh dashboard statistics' },
    { name: 'Export Scan', action: () => { showView('scans'); }, desc: 'Export scan results' }
];

let selectedCommandIndex = 0;

function initializeCommandPalette() {
    const palette = document.getElementById('command-palette');
    const search = document.getElementById('command-search');
    const list = document.getElementById('command-list');
    
    if (!palette || !search || !list) return;
    
    // Filter commands based on search
    search.addEventListener('input', (e) => {
        filterCommands(e.target.value);
    });
    
    // Handle selection
    search.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedCommandIndex = Math.min(selectedCommandIndex + 1, commands.length - 1);
            updateCommandSelection();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedCommandIndex = Math.max(selectedCommandIndex - 1, 0);
            updateCommandSelection();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            executeSelectedCommand();
        }
    });
    
    // Initial load
    filterCommands('');
}

function filterCommands(query) {
    const list = document.getElementById('command-list');
    if (!list) return;
    
    const filtered = commands.filter(cmd => 
        cmd.name.toLowerCase().includes(query.toLowerCase()) ||
        (cmd.desc && cmd.desc.toLowerCase().includes(query.toLowerCase()))
    );
    
    list.innerHTML = '';
    selectedCommandIndex = 0;
    
    filtered.forEach((cmd, index) => {
        const item = document.createElement('div');
        item.className = 'command-item';
        if (index === 0) item.classList.add('selected');
        item.innerHTML = `
            <div>
                <div class="command-name">${cmd.name}</div>
                <div class="command-desc">${cmd.desc || ''}</div>
            </div>
            ${cmd.shortcut ? `<div class="command-shortcut">${cmd.shortcut}</div>` : ''}
        `;
        item.onclick = () => {
            selectedCommandIndex = index;
            executeSelectedCommand();
        };
        list.appendChild(item);
    });
}

function updateCommandSelection() {
    const items = document.querySelectorAll('.command-item');
    items.forEach((item, index) => {
        if (index === selectedCommandIndex) {
            item.classList.add('selected');
            item.scrollIntoView({ block: 'nearest' });
        } else {
            item.classList.remove('selected');
        }
    });
}

function executeSelectedCommand() {
    const list = document.getElementById('command-list');
    const items = list.querySelectorAll('.command-item');
    if (items[selectedCommandIndex]) {
        const filtered = commands.filter(cmd => 
            cmd.name.toLowerCase().includes(document.getElementById('command-search').value.toLowerCase())
        );
        if (filtered[selectedCommandIndex]) {
            closeCommandPalette();
            filtered[selectedCommandIndex].action();
        }
    }
}

function showCommandPalette() {
    const palette = document.getElementById('command-palette');
    const search = document.getElementById('command-search');
    if (palette && search) {
        palette.classList.add('active');
        search.value = '';
        filterCommands('');
        setTimeout(() => search.focus(), 100);
    }
}

function closeCommandPalette() {
    const palette = document.getElementById('command-palette');
    if (palette) {
        palette.classList.remove('active');
    }
}

// ==================== KEYBOARD SHORTCUTS ====================

function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl+U or Ctrl+K for command palette
        if ((e.ctrlKey || e.metaKey) && (e.key === 'u' || e.key === 'k')) {
            e.preventDefault();
            const palette = document.getElementById('command-palette');
            if (palette && palette.classList.contains('active')) {
                closeCommandPalette();
            } else {
                showCommandPalette();
            }
        }
        
        // Ctrl+N for new scan
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            showNewScanModal();
        }
        
        // Ctrl+T for new target
        if ((e.ctrlKey || e.metaKey) && e.key === 't' && !e.shiftKey) {
            e.preventDefault();
            showNewTargetModal();
        }
        
        // Ctrl+D for dashboard
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            showView('dashboard');
        }
        
        // Ctrl+S for scans (but not if in input field)
        if ((e.ctrlKey || e.metaKey) && e.key === 's' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
            e.preventDefault();
            showView('scans');
        }
        
        // Ctrl+V for vulnerabilities (but not if in input field)
        if ((e.ctrlKey || e.metaKey) && e.key === 'v' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
            e.preventDefault();
            showView('vulnerabilities');
        }
        
        // Ctrl+` for terminal
        if ((e.ctrlKey || e.metaKey) && e.key === '`') {
            e.preventDefault();
            showView('terminal');
        }
        
        // Ctrl+Shift+D for dark mode
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
            e.preventDefault();
            toggleDarkMode();
        }
        
        // Escape to close modals/palette
        if (e.key === 'Escape') {
            const palette = document.getElementById('command-palette');
            if (palette && palette.classList.contains('active')) {
                closeCommandPalette();
            } else {
                document.querySelectorAll('.modal.active').forEach(modal => {
                    modal.classList.remove('active');
                });
            }
        }
    });
}
