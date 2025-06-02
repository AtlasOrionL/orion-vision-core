"use strict";
/**
 * 🌐 Orion Network Debug Provider
 * Advanced networking debugging and monitoring tools
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.OrionNetworkDebugger = void 0;
const vscode = __importStar(require("vscode"));
const axios_1 = __importDefault(require("axios"));
const logger_1 = require("../utils/logger");
class OrionNetworkDebugger {
    constructor(config) {
        this.isMonitoring = false;
        this.requests = [];
        this.stats = {
            totalRequests: 0,
            successfulRequests: 0,
            failedRequests: 0,
            averageResponseTime: 0,
            totalDataTransferred: 0
        };
        this.config = config;
        this.logger = new logger_1.OrionLogger();
    }
    async startDebugging() {
        try {
            this.logger.info('🌐 Starting network debugging...');
            // Create or show debug panel
            if (this.debugPanel) {
                this.debugPanel.reveal(vscode.ViewColumn.Two);
            }
            else {
                this.debugPanel = vscode.window.createWebviewPanel('orionNetworkDebug', '🌐 Orion Network Debugger', vscode.ViewColumn.Two, {
                    enableScripts: true,
                    retainContextWhenHidden: true
                });
                this.debugPanel.onDidDispose(() => {
                    this.debugPanel = undefined;
                    this.stopMonitoring();
                });
                // Handle messages from webview
                this.debugPanel.webview.onDidReceiveMessage(message => this.handleWebviewMessage(message), undefined);
            }
            // Generate debug interface
            this.debugPanel.webview.html = this.getDebugInterfaceHtml();
            // Start monitoring if not already started
            if (!this.isMonitoring) {
                this.startMonitoring();
            }
        }
        catch (error) {
            this.logger.error('❌ Network debugging failed:', error);
            vscode.window.showErrorMessage('Failed to start network debugging');
        }
    }
    getDebugInterfaceHtml() {
        return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Orion Network Debugger</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: var(--vscode-editor-background);
                    color: var(--vscode-editor-foreground);
                }
                
                .header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                    padding-bottom: 15px;
                    border-bottom: 1px solid var(--vscode-panel-border);
                }
                
                .title {
                    font-size: 24px;
                    font-weight: bold;
                    color: var(--vscode-textLink-foreground);
                }
                
                .controls {
                    display: flex;
                    gap: 10px;
                }
                
                .btn {
                    background-color: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                }
                
                .btn:hover {
                    background-color: var(--vscode-button-hoverBackground);
                }
                
                .btn.secondary {
                    background-color: var(--vscode-button-secondaryBackground);
                    color: var(--vscode-button-secondaryForeground);
                }
                
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-bottom: 30px;
                }
                
                .stat-card {
                    background-color: var(--vscode-editor-inactiveSelectionBackground);
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid var(--vscode-textLink-foreground);
                }
                
                .stat-value {
                    font-size: 24px;
                    font-weight: bold;
                    color: var(--vscode-textLink-foreground);
                }
                
                .stat-label {
                    font-size: 12px;
                    color: var(--vscode-descriptionForeground);
                    margin-top: 5px;
                }
                
                .requests-section {
                    margin-top: 30px;
                }
                
                .section-title {
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 15px;
                    color: var(--vscode-textLink-foreground);
                }
                
                .requests-table {
                    width: 100%;
                    border-collapse: collapse;
                    background-color: var(--vscode-editor-background);
                }
                
                .requests-table th,
                .requests-table td {
                    padding: 10px;
                    text-align: left;
                    border-bottom: 1px solid var(--vscode-panel-border);
                }
                
                .requests-table th {
                    background-color: var(--vscode-editor-inactiveSelectionBackground);
                    font-weight: bold;
                }
                
                .method {
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-size: 11px;
                    font-weight: bold;
                }
                
                .method.GET { background-color: #28a745; color: white; }
                .method.POST { background-color: #007bff; color: white; }
                .method.PUT { background-color: #ffc107; color: black; }
                .method.DELETE { background-color: #dc3545; color: white; }
                
                .status {
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-size: 11px;
                    font-weight: bold;
                }
                
                .status.success { background-color: #28a745; color: white; }
                .status.error { background-color: #dc3545; color: white; }
                .status.warning { background-color: #ffc107; color: black; }
                
                .response-time {
                    font-family: monospace;
                    font-size: 12px;
                }
                
                .url {
                    max-width: 300px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }
                
                .monitoring-status {
                    display: inline-flex;
                    align-items: center;
                    gap: 5px;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: bold;
                }
                
                .monitoring-status.active {
                    background-color: #28a745;
                    color: white;
                }
                
                .monitoring-status.inactive {
                    background-color: #6c757d;
                    color: white;
                }
                
                .empty-state {
                    text-align: center;
                    padding: 40px;
                    color: var(--vscode-descriptionForeground);
                }
                
                .test-section {
                    margin-top: 30px;
                    padding: 20px;
                    background-color: var(--vscode-editor-inactiveSelectionBackground);
                    border-radius: 8px;
                }
                
                .test-form {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    margin-bottom: 15px;
                }
                
                .form-group {
                    display: flex;
                    flex-direction: column;
                }
                
                .form-group label {
                    margin-bottom: 5px;
                    font-weight: bold;
                }
                
                .form-group input,
                .form-group select {
                    padding: 8px;
                    border: 1px solid var(--vscode-input-border);
                    border-radius: 4px;
                    background-color: var(--vscode-input-background);
                    color: var(--vscode-input-foreground);
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">🌐 Network Debugger</div>
                <div class="controls">
                    <div class="monitoring-status" id="monitoringStatus">
                        <span id="statusDot">●</span>
                        <span id="statusText">Monitoring</span>
                    </div>
                    <button class="btn" onclick="toggleMonitoring()" id="toggleBtn">Stop</button>
                    <button class="btn secondary" onclick="clearRequests()">Clear</button>
                    <button class="btn secondary" onclick="exportData()">Export</button>
                </div>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value" id="totalRequests">0</div>
                    <div class="stat-label">Total Requests</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="successfulRequests">0</div>
                    <div class="stat-label">Successful</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="failedRequests">0</div>
                    <div class="stat-label">Failed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="avgResponseTime">0ms</div>
                    <div class="stat-label">Avg Response Time</div>
                </div>
            </div>

            <div class="test-section">
                <div class="section-title">🧪 Test Network Request</div>
                <div class="test-form">
                    <div class="form-group">
                        <label for="testMethod">Method</label>
                        <select id="testMethod">
                            <option value="GET">GET</option>
                            <option value="POST">POST</option>
                            <option value="PUT">PUT</option>
                            <option value="DELETE">DELETE</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="testUrl">URL</label>
                        <input type="text" id="testUrl" placeholder="https://api.example.com/endpoint" value="https://jsonplaceholder.typicode.com/posts/1">
                    </div>
                </div>
                <button class="btn" onclick="testRequest()">Send Test Request</button>
            </div>

            <div class="requests-section">
                <div class="section-title">📊 Network Requests</div>
                <div id="requestsContainer">
                    <div class="empty-state">
                        <p>No network requests captured yet.</p>
                        <p>Start monitoring to see requests appear here.</p>
                    </div>
                </div>
            </div>

            <script>
                const vscode = acquireVsCodeApi();
                let isMonitoring = true;
                let requests = [];

                function updateStats(stats) {
                    document.getElementById('totalRequests').textContent = stats.totalRequests;
                    document.getElementById('successfulRequests').textContent = stats.successfulRequests;
                    document.getElementById('failedRequests').textContent = stats.failedRequests;
                    document.getElementById('avgResponseTime').textContent = stats.averageResponseTime + 'ms';
                }

                function updateRequestsTable(requestsList) {
                    requests = requestsList;
                    const container = document.getElementById('requestsContainer');
                    
                    if (requests.length === 0) {
                        container.innerHTML = \`
                            <div class="empty-state">
                                <p>No network requests captured yet.</p>
                                <p>Start monitoring to see requests appear here.</p>
                            </div>
                        \`;
                        return;
                    }

                    const table = \`
                        <table class="requests-table">
                            <thead>
                                <tr>
                                    <th>Method</th>
                                    <th>URL</th>
                                    <th>Status</th>
                                    <th>Response Time</th>
                                    <th>Timestamp</th>
                                </tr>
                            </thead>
                            <tbody>
                                \${requests.map(req => \`
                                    <tr onclick="showRequestDetails('\${req.id}')">
                                        <td><span class="method \${req.method}">\${req.method}</span></td>
                                        <td class="url" title="\${req.url}">\${req.url}</td>
                                        <td><span class="status \${getStatusClass(req.status)}">\${req.status}</span></td>
                                        <td class="response-time">\${req.responseTime}ms</td>
                                        <td>\${new Date(req.timestamp).toLocaleTimeString()}</td>
                                    </tr>
                                \`).join('')}
                            </tbody>
                        </table>
                    \`;
                    
                    container.innerHTML = table;
                }

                function getStatusClass(status) {
                    if (status >= 200 && status < 300) return 'success';
                    if (status >= 400) return 'error';
                    return 'warning';
                }

                function toggleMonitoring() {
                    isMonitoring = !isMonitoring;
                    vscode.postMessage({
                        command: 'toggleMonitoring',
                        monitoring: isMonitoring
                    });
                    updateMonitoringStatus();
                }

                function updateMonitoringStatus() {
                    const status = document.getElementById('monitoringStatus');
                    const statusText = document.getElementById('statusText');
                    const toggleBtn = document.getElementById('toggleBtn');
                    
                    if (isMonitoring) {
                        status.className = 'monitoring-status active';
                        statusText.textContent = 'Monitoring';
                        toggleBtn.textContent = 'Stop';
                    } else {
                        status.className = 'monitoring-status inactive';
                        statusText.textContent = 'Stopped';
                        toggleBtn.textContent = 'Start';
                    }
                }

                function clearRequests() {
                    vscode.postMessage({ command: 'clearRequests' });
                }

                function exportData() {
                    vscode.postMessage({ command: 'exportData' });
                }

                function testRequest() {
                    const method = document.getElementById('testMethod').value;
                    const url = document.getElementById('testUrl').value;
                    
                    if (!url) {
                        alert('Please enter a URL');
                        return;
                    }

                    vscode.postMessage({
                        command: 'testRequest',
                        method: method,
                        url: url
                    });
                }

                function showRequestDetails(requestId) {
                    vscode.postMessage({
                        command: 'showRequestDetails',
                        requestId: requestId
                    });
                }

                // Listen for messages from extension
                window.addEventListener('message', event => {
                    const message = event.data;
                    
                    switch (message.command) {
                        case 'updateStats':
                            updateStats(message.stats);
                            break;
                        case 'updateRequests':
                            updateRequestsTable(message.requests);
                            break;
                        case 'monitoringToggled':
                            isMonitoring = message.monitoring;
                            updateMonitoringStatus();
                            break;
                    }
                });

                // Initialize
                updateMonitoringStatus();
                vscode.postMessage({ command: 'ready' });
            </script>
        </body>
        </html>
        `;
    }
    async handleWebviewMessage(message) {
        switch (message.command) {
            case 'ready':
                this.sendStatsUpdate();
                this.sendRequestsUpdate();
                break;
            case 'toggleMonitoring':
                if (message.monitoring) {
                    this.startMonitoring();
                }
                else {
                    this.stopMonitoring();
                }
                break;
            case 'clearRequests':
                this.clearRequests();
                break;
            case 'exportData':
                await this.exportData();
                break;
            case 'testRequest':
                await this.testRequest(message.method, message.url);
                break;
            case 'showRequestDetails':
                this.showRequestDetails(message.requestId);
                break;
        }
    }
    startMonitoring() {
        if (this.isMonitoring) {
            return;
        }
        this.isMonitoring = true;
        this.logger.info('🌐 Network monitoring started');
        // Send monitoring status update
        this.debugPanel?.webview.postMessage({
            command: 'monitoringToggled',
            monitoring: true
        });
    }
    stopMonitoring() {
        this.isMonitoring = false;
        this.logger.info('🌐 Network monitoring stopped');
        // Send monitoring status update
        this.debugPanel?.webview.postMessage({
            command: 'monitoringToggled',
            monitoring: false
        });
    }
    clearRequests() {
        this.requests = [];
        this.stats = {
            totalRequests: 0,
            successfulRequests: 0,
            failedRequests: 0,
            averageResponseTime: 0,
            totalDataTransferred: 0
        };
        this.sendStatsUpdate();
        this.sendRequestsUpdate();
    }
    async exportData() {
        try {
            const data = {
                stats: this.stats,
                requests: this.requests,
                exportedAt: new Date().toISOString()
            };
            const uri = await vscode.window.showSaveDialog({
                defaultUri: vscode.Uri.file('network-debug-export.json'),
                filters: {
                    'jsonFiles': ['json']
                }
            });
            if (uri) {
                await vscode.workspace.fs.writeFile(uri, Buffer.from(JSON.stringify(data, null, 2)));
                vscode.window.showInformationMessage('Network debug data exported successfully!');
            }
        }
        catch (error) {
            this.logger.error('❌ Export failed:', error);
            vscode.window.showErrorMessage('Failed to export network debug data');
        }
    }
    async testRequest(method, url) {
        const startTime = Date.now();
        try {
            const response = await (0, axios_1.default)({
                method: method.toLowerCase(),
                url: url,
                timeout: 10000
            });
            const responseTime = Date.now() - startTime;
            const request = {
                id: Date.now().toString(),
                method: method,
                url: url,
                status: response.status,
                responseTime: responseTime,
                timestamp: new Date(),
                headers: response.headers,
                response: response.data
            };
            this.addRequest(request);
        }
        catch (error) {
            const responseTime = Date.now() - startTime;
            const request = {
                id: Date.now().toString(),
                method: method,
                url: url,
                status: error.response?.status || 0,
                responseTime: responseTime,
                timestamp: new Date(),
                headers: error.response?.headers || {},
                response: error.message
            };
            this.addRequest(request);
        }
    }
    addRequest(request) {
        this.requests.unshift(request); // Add to beginning
        // Limit to last 100 requests
        if (this.requests.length > 100) {
            this.requests = this.requests.slice(0, 100);
        }
        // Update stats
        this.updateStats(request);
        // Send updates to webview
        this.sendStatsUpdate();
        this.sendRequestsUpdate();
    }
    updateStats(request) {
        this.stats.totalRequests++;
        if (request.status >= 200 && request.status < 300) {
            this.stats.successfulRequests++;
        }
        else {
            this.stats.failedRequests++;
        }
        // Update average response time
        const totalTime = this.stats.averageResponseTime * (this.stats.totalRequests - 1) + request.responseTime;
        this.stats.averageResponseTime = Math.round(totalTime / this.stats.totalRequests);
    }
    sendStatsUpdate() {
        this.debugPanel?.webview.postMessage({
            command: 'updateStats',
            stats: this.stats
        });
    }
    sendRequestsUpdate() {
        this.debugPanel?.webview.postMessage({
            command: 'updateRequests',
            requests: this.requests
        });
    }
    showRequestDetails(requestId) {
        const request = this.requests.find(r => r.id === requestId);
        if (!request) {
            return;
        }
        // Show request details in a new webview or quick pick
        vscode.window.showInformationMessage(`Request Details: ${request.method} ${request.url} - ${request.status} (${request.responseTime}ms)`);
    }
}
exports.OrionNetworkDebugger = OrionNetworkDebugger;
//# sourceMappingURL=networkDebugProvider.js.map