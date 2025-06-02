"use strict";
/**
 * 🌐 Orion Webview Provider
 * Main dashboard and webview management
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
Object.defineProperty(exports, "__esModule", { value: true });
exports.OrionWebviewProvider = void 0;
const vscode = __importStar(require("vscode"));
class OrionWebviewProvider {
    constructor(_extensionUri) {
        this._extensionUri = _extensionUri;
    }
    resolveWebviewView(webviewView, context, _token) {
        this._view = webviewView;
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        webviewView.webview.onDidReceiveMessage(data => {
            switch (data.type) {
                case 'openAI':
                    vscode.commands.executeCommand('orion.activateAI');
                    break;
                case 'openMobilePreview':
                    vscode.commands.executeCommand('orion.mobilePreview');
                    break;
                case 'openNetworkDebug':
                    vscode.commands.executeCommand('orion.networkDebug');
                    break;
                case 'openPerformance':
                    vscode.commands.executeCommand('orion.performanceInsights');
                    break;
                case 'openDeployment':
                    vscode.commands.executeCommand('orion.deployApp');
                    break;
            }
        });
    }
    async showDashboard() {
        if (this._view) {
            this._view.show?.(true);
        }
        else {
            // Create a new webview panel for full dashboard
            const panel = vscode.window.createWebviewPanel('orionDashboard', '🤖 Orion Dashboard', vscode.ViewColumn.One, {
                enableScripts: true,
                retainContextWhenHidden: true
            });
            panel.webview.html = this._getFullDashboardHtml(panel.webview);
        }
    }
    _getHtmlForWebview(webview) {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Orion Dashboard</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 15px;
                    background-color: var(--vscode-editor-background);
                    color: var(--vscode-editor-foreground);
                }
                
                .header {
                    text-align: center;
                    margin-bottom: 20px;
                    padding-bottom: 15px;
                    border-bottom: 1px solid var(--vscode-panel-border);
                }
                
                .logo {
                    font-size: 24px;
                    margin-bottom: 5px;
                }
                
                .title {
                    font-size: 16px;
                    font-weight: bold;
                    color: var(--vscode-textLink-foreground);
                }
                
                .subtitle {
                    font-size: 12px;
                    color: var(--vscode-descriptionForeground);
                    margin-top: 5px;
                }
                
                .feature-grid {
                    display: grid;
                    gap: 10px;
                }
                
                .feature-card {
                    background-color: var(--vscode-editor-inactiveSelectionBackground);
                    padding: 15px;
                    border-radius: 6px;
                    cursor: pointer;
                    border: 1px solid transparent;
                    transition: all 0.2s ease;
                }
                
                .feature-card:hover {
                    border-color: var(--vscode-textLink-foreground);
                    background-color: var(--vscode-list-hoverBackground);
                }
                
                .feature-icon {
                    font-size: 20px;
                    margin-bottom: 8px;
                }
                
                .feature-title {
                    font-weight: bold;
                    margin-bottom: 5px;
                    font-size: 14px;
                }
                
                .feature-description {
                    font-size: 11px;
                    color: var(--vscode-descriptionForeground);
                    line-height: 1.3;
                }
                
                .status-section {
                    margin-top: 20px;
                    padding-top: 15px;
                    border-top: 1px solid var(--vscode-panel-border);
                }
                
                .status-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 8px 0;
                    font-size: 12px;
                }
                
                .status-label {
                    color: var(--vscode-descriptionForeground);
                }
                
                .status-value {
                    font-weight: bold;
                }
                
                .status-connected {
                    color: #28a745;
                }
                
                .status-disconnected {
                    color: #dc3545;
                }
                
                .quick-actions {
                    margin-top: 15px;
                }
                
                .action-btn {
                    width: 100%;
                    background-color: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    padding: 8px 12px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 12px;
                    margin-bottom: 8px;
                }
                
                .action-btn:hover {
                    background-color: var(--vscode-button-hoverBackground);
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">🤖</div>
                <div class="title">Orion Vision Core</div>
                <div class="subtitle">AI-Powered Development Assistant</div>
            </div>

            <div class="feature-grid">
                <div class="feature-card" onclick="openFeature('openAI')">
                    <div class="feature-icon">🧠</div>
                    <div class="feature-title">AI Assistant</div>
                    <div class="feature-description">Smart code completion and AI-powered development assistance</div>
                </div>

                <div class="feature-card" onclick="openFeature('openMobilePreview')">
                    <div class="feature-icon">📱</div>
                    <div class="feature-title">Mobile Preview</div>
                    <div class="feature-description">Preview and test mobile applications with device simulation</div>
                </div>

                <div class="feature-card" onclick="openFeature('openNetworkDebug')">
                    <div class="feature-icon">🌐</div>
                    <div class="feature-title">Network Debug</div>
                    <div class="feature-description">Advanced networking debugging and monitoring tools</div>
                </div>

                <div class="feature-card" onclick="openFeature('openPerformance')">
                    <div class="feature-icon">📊</div>
                    <div class="feature-title">Performance</div>
                    <div class="feature-description">Real-time performance insights and optimization suggestions</div>
                </div>

                <div class="feature-card" onclick="openFeature('openDeployment')">
                    <div class="feature-icon">🚀</div>
                    <div class="feature-title">Deployment</div>
                    <div class="feature-description">Automated deployment to multiple platforms and environments</div>
                </div>
            </div>

            <div class="status-section">
                <div class="status-item">
                    <span class="status-label">AI Connection:</span>
                    <span class="status-value status-connected">Connected</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Extensions:</span>
                    <span class="status-value">Active</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Version:</span>
                    <span class="status-value">v1.0.0</span>
                </div>
            </div>

            <div class="quick-actions">
                <button class="action-btn" onclick="openFeature('openAI')">🤖 Activate AI Assistant</button>
                <button class="action-btn" onclick="openDashboard()">📊 Open Full Dashboard</button>
            </div>

            <script>
                const vscode = acquireVsCodeApi();

                function openFeature(type) {
                    vscode.postMessage({ type: type });
                }

                function openDashboard() {
                    vscode.postMessage({ type: 'openDashboard' });
                }
            </script>
        </body>
        </html>`;
    }
    _getFullDashboardHtml(webview) {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Orion Vision Core Dashboard</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }
                
                .dashboard-container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                
                .dashboard-header {
                    text-align: center;
                    color: white;
                    margin-bottom: 40px;
                }
                
                .dashboard-title {
                    font-size: 48px;
                    margin-bottom: 10px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }
                
                .dashboard-subtitle {
                    font-size: 18px;
                    opacity: 0.9;
                }
                
                .features-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 40px;
                }
                
                .feature-card {
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 12px;
                    padding: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                    cursor: pointer;
                }
                
                .feature-card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 15px 40px rgba(0,0,0,0.3);
                }
                
                .feature-icon {
                    font-size: 48px;
                    margin-bottom: 20px;
                    text-align: center;
                }
                
                .feature-title {
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 15px;
                    color: #333;
                    text-align: center;
                }
                
                .feature-description {
                    color: #666;
                    line-height: 1.6;
                    text-align: center;
                    margin-bottom: 20px;
                }
                
                .feature-button {
                    width: 100%;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-size: 16px;
                    font-weight: bold;
                    cursor: pointer;
                    transition: opacity 0.3s ease;
                }
                
                .feature-button:hover {
                    opacity: 0.9;
                }
                
                .stats-section {
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 12px;
                    padding: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    margin-bottom: 40px;
                }
                
                .stats-title {
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 20px;
                    color: #333;
                    text-align: center;
                }
                
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                }
                
                .stat-item {
                    text-align: center;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 8px;
                }
                
                .stat-value {
                    font-size: 32px;
                    font-weight: bold;
                    color: #667eea;
                    margin-bottom: 5px;
                }
                
                .stat-label {
                    color: #666;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <div class="dashboard-container">
                <div class="dashboard-header">
                    <div class="dashboard-title">🤖 Orion Vision Core</div>
                    <div class="dashboard-subtitle">AI-Powered Development Assistant Dashboard</div>
                </div>

                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">🧠</div>
                        <div class="feature-title">AI Assistant</div>
                        <div class="feature-description">
                            Advanced AI-powered code completion, smart search, and intelligent development assistance
                        </div>
                        <button class="feature-button" onclick="openFeature('ai')">Activate AI Assistant</button>
                    </div>

                    <div class="feature-card">
                        <div class="feature-icon">📱</div>
                        <div class="feature-title">Mobile Preview</div>
                        <div class="feature-description">
                            Real-time mobile app preview with device simulation and responsive design testing
                        </div>
                        <button class="feature-button" onclick="openFeature('mobile')">Open Mobile Preview</button>
                    </div>

                    <div class="feature-card">
                        <div class="feature-icon">🌐</div>
                        <div class="feature-title">Network Debugging</div>
                        <div class="feature-description">
                            Advanced networking tools for debugging, monitoring, and optimizing network requests
                        </div>
                        <button class="feature-button" onclick="openFeature('network')">Start Network Debug</button>
                    </div>

                    <div class="feature-card">
                        <div class="feature-icon">📊</div>
                        <div class="feature-title">Performance Insights</div>
                        <div class="feature-description">
                            Real-time performance monitoring, code analysis, and optimization recommendations
                        </div>
                        <button class="feature-button" onclick="openFeature('performance')">View Performance</button>
                    </div>

                    <div class="feature-card">
                        <div class="feature-icon">🚀</div>
                        <div class="feature-title">Deployment Manager</div>
                        <div class="feature-description">
                            Automated deployment to multiple platforms with CI/CD integration and monitoring
                        </div>
                        <button class="feature-button" onclick="openFeature('deployment')">Deploy Application</button>
                    </div>

                    <div class="feature-card">
                        <div class="feature-icon">🔄</div>
                        <div class="feature-title">Real-Time Collaboration</div>
                        <div class="feature-description">
                            Live collaboration features with real-time code sharing and team synchronization
                        </div>
                        <button class="feature-button" onclick="openFeature('collaboration')">Start Collaboration</button>
                    </div>
                </div>

                <div class="stats-section">
                    <div class="stats-title">📈 Development Statistics</div>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-value">1,247</div>
                            <div class="stat-label">Lines of Code</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">23</div>
                            <div class="stat-label">Files</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">89%</div>
                            <div class="stat-label">Code Quality</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">156</div>
                            <div class="stat-label">AI Completions</div>
                        </div>
                    </div>
                </div>
            </div>

            <script>
                function openFeature(feature) {
                    switch(feature) {
                        case 'ai':
                            vscode.postMessage({ type: 'openAI' });
                            break;
                        case 'mobile':
                            vscode.postMessage({ type: 'openMobilePreview' });
                            break;
                        case 'network':
                            vscode.postMessage({ type: 'openNetworkDebug' });
                            break;
                        case 'performance':
                            vscode.postMessage({ type: 'openPerformance' });
                            break;
                        case 'deployment':
                            vscode.postMessage({ type: 'openDeployment' });
                            break;
                        case 'collaboration':
                            // Future feature
                            alert('🔄 Real-time collaboration coming soon!');
                            break;
                    }
                }

                const vscode = acquireVsCodeApi();
            </script>
        </body>
        </html>`;
    }
}
exports.OrionWebviewProvider = OrionWebviewProvider;
OrionWebviewProvider.viewType = 'orionDashboard';
//# sourceMappingURL=webviewProvider.js.map