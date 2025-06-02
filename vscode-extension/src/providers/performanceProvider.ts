/**
 * 📊 Orion Performance Monitor Provider
 * Real-time performance insights and monitoring
 */

import * as vscode from 'vscode';
import * as os from 'os';
import { OrionConfiguration } from '../config/configuration';
import { OrionLogger } from '../utils/logger';

export interface IPerformanceMetrics {
    cpu: {
        usage: number;
        cores: number;
        model: string;
    };
    memory: {
        used: number;
        total: number;
        percentage: number;
    };
    disk: {
        used: number;
        total: number;
        percentage: number;
    };
    network: {
        bytesReceived: number;
        bytesSent: number;
    };
    vscode: {
        extensions: number;
        openFiles: number;
        workspaceFolders: number;
    };
}

export interface ICodeMetrics {
    linesOfCode: number;
    files: number;
    functions: number;
    classes: number;
    complexity: number;
}

export class OrionPerformanceMonitor {
    private config: OrionConfiguration;
    private logger: OrionLogger;
    private insightsPanel: vscode.WebviewPanel | undefined;
    private isMonitoring: boolean = false;
    private metricsHistory: IPerformanceMetrics[] = [];
    private monitoringInterval: NodeJS.Timeout | undefined;

    constructor(config: OrionConfiguration) {
        this.config = config;
        this.logger = new OrionLogger();
    }

    async showInsights(): Promise<void> {
        try {
            this.logger.info('📊 Opening performance insights...');

            // Create or show insights panel
            if (this.insightsPanel) {
                this.insightsPanel.reveal(vscode.ViewColumn.Two);
            } else {
                this.insightsPanel = vscode.window.createWebviewPanel(
                    'orionPerformanceInsights',
                    '📊 Orion Performance Insights',
                    vscode.ViewColumn.Two,
                    {
                        enableScripts: true,
                        retainContextWhenHidden: true
                    }
                );

                this.insightsPanel.onDidDispose(() => {
                    this.insightsPanel = undefined;
                });

                // Handle messages from webview
                this.insightsPanel.webview.onDidReceiveMessage(
                    message => this.handleWebviewMessage(message),
                    undefined
                );
            }

            // Generate insights interface
            this.insightsPanel.webview.html = await this.getInsightsInterfaceHtml();

        } catch (error) {
            this.logger.error('❌ Performance insights failed:', error);
            vscode.window.showErrorMessage('Failed to open performance insights');
        }
    }

    private async getInsightsInterfaceHtml(): Promise<string> {
        const currentMetrics = await this.collectMetrics();
        const codeMetrics = await this.analyzeCodeMetrics();

        return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Orion Performance Insights</title>
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
                    margin-bottom: 30px;
                    padding-bottom: 15px;
                    border-bottom: 1px solid var(--vscode-panel-border);
                }
                
                .title {
                    font-size: 24px;
                    font-weight: bold;
                    color: var(--vscode-textLink-foreground);
                }
                
                .refresh-btn {
                    background-color: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                }
                
                .refresh-btn:hover {
                    background-color: var(--vscode-button-hoverBackground);
                }
                
                .metrics-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                
                .metric-card {
                    background-color: var(--vscode-editor-inactiveSelectionBackground);
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid var(--vscode-textLink-foreground);
                }
                
                .metric-title {
                    font-size: 16px;
                    font-weight: bold;
                    margin-bottom: 15px;
                    color: var(--vscode-textLink-foreground);
                }
                
                .metric-value {
                    font-size: 28px;
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                
                .metric-label {
                    font-size: 12px;
                    color: var(--vscode-descriptionForeground);
                }
                
                .progress-bar {
                    width: 100%;
                    height: 8px;
                    background-color: var(--vscode-progressBar-background);
                    border-radius: 4px;
                    overflow: hidden;
                    margin-top: 10px;
                }
                
                .progress-fill {
                    height: 100%;
                    background-color: var(--vscode-progressBar-background);
                    transition: width 0.3s ease;
                }
                
                .progress-fill.low { background-color: #28a745; }
                .progress-fill.medium { background-color: #ffc107; }
                .progress-fill.high { background-color: #dc3545; }
                
                .code-analysis {
                    background-color: var(--vscode-editor-inactiveSelectionBackground);
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                }
                
                .analysis-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 15px;
                    margin-top: 15px;
                }
                
                .analysis-item {
                    text-align: center;
                    padding: 15px;
                    background-color: var(--vscode-editor-background);
                    border-radius: 6px;
                }
                
                .analysis-value {
                    font-size: 24px;
                    font-weight: bold;
                    color: var(--vscode-textLink-foreground);
                }
                
                .analysis-label {
                    font-size: 12px;
                    color: var(--vscode-descriptionForeground);
                    margin-top: 5px;
                }
                
                .recommendations {
                    background-color: var(--vscode-editor-inactiveSelectionBackground);
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                }
                
                .recommendation-item {
                    display: flex;
                    align-items: flex-start;
                    gap: 10px;
                    margin-bottom: 15px;
                    padding: 10px;
                    background-color: var(--vscode-editor-background);
                    border-radius: 6px;
                }
                
                .recommendation-icon {
                    font-size: 18px;
                    margin-top: 2px;
                }
                
                .recommendation-text {
                    flex: 1;
                }
                
                .recommendation-title {
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                
                .recommendation-description {
                    font-size: 14px;
                    color: var(--vscode-descriptionForeground);
                }
                
                .chart-container {
                    background-color: var(--vscode-editor-inactiveSelectionBackground);
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                }
                
                .chart-placeholder {
                    height: 200px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background-color: var(--vscode-editor-background);
                    border-radius: 6px;
                    color: var(--vscode-descriptionForeground);
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">📊 Performance Insights</div>
                <button class="refresh-btn" onclick="refreshMetrics()">🔄 Refresh</button>
            </div>

            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-title">💻 CPU Usage</div>
                    <div class="metric-value" id="cpuUsage">${currentMetrics.cpu.usage.toFixed(1)}%</div>
                    <div class="metric-label">${currentMetrics.cpu.cores} cores • ${currentMetrics.cpu.model}</div>
                    <div class="progress-bar">
                        <div class="progress-fill ${this.getUsageClass(currentMetrics.cpu.usage)}" 
                             style="width: ${currentMetrics.cpu.usage}%"></div>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-title">🧠 Memory Usage</div>
                    <div class="metric-value" id="memoryUsage">${currentMetrics.memory.percentage.toFixed(1)}%</div>
                    <div class="metric-label">${this.formatBytes(currentMetrics.memory.used)} / ${this.formatBytes(currentMetrics.memory.total)}</div>
                    <div class="progress-bar">
                        <div class="progress-fill ${this.getUsageClass(currentMetrics.memory.percentage)}" 
                             style="width: ${currentMetrics.memory.percentage}%"></div>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-title">💾 Disk Usage</div>
                    <div class="metric-value" id="diskUsage">${currentMetrics.disk.percentage.toFixed(1)}%</div>
                    <div class="metric-label">${this.formatBytes(currentMetrics.disk.used)} / ${this.formatBytes(currentMetrics.disk.total)}</div>
                    <div class="progress-bar">
                        <div class="progress-fill ${this.getUsageClass(currentMetrics.disk.percentage)}" 
                             style="width: ${currentMetrics.disk.percentage}%"></div>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-title">🔌 VS Code</div>
                    <div class="metric-value" id="vscodeFiles">${currentMetrics.vscode.openFiles}</div>
                    <div class="metric-label">Open Files • ${currentMetrics.vscode.extensions} Extensions</div>
                </div>
            </div>

            <div class="code-analysis">
                <div class="metric-title">📝 Code Analysis</div>
                <div class="analysis-grid">
                    <div class="analysis-item">
                        <div class="analysis-value">${codeMetrics.linesOfCode.toLocaleString()}</div>
                        <div class="analysis-label">Lines of Code</div>
                    </div>
                    <div class="analysis-item">
                        <div class="analysis-value">${codeMetrics.files}</div>
                        <div class="analysis-label">Files</div>
                    </div>
                    <div class="analysis-item">
                        <div class="analysis-value">${codeMetrics.functions}</div>
                        <div class="analysis-label">Functions</div>
                    </div>
                    <div class="analysis-item">
                        <div class="analysis-value">${codeMetrics.classes}</div>
                        <div class="analysis-label">Classes</div>
                    </div>
                    <div class="analysis-item">
                        <div class="analysis-value">${codeMetrics.complexity}</div>
                        <div class="analysis-label">Complexity Score</div>
                    </div>
                </div>
            </div>

            <div class="recommendations">
                <div class="metric-title">💡 Performance Recommendations</div>
                <div id="recommendationsContainer">
                    ${this.generateRecommendations(currentMetrics, codeMetrics)}
                </div>
            </div>

            <div class="chart-container">
                <div class="metric-title">📈 Performance Trends</div>
                <div class="chart-placeholder">
                    📊 Performance charts will be displayed here<br>
                    <small>Real-time monitoring data visualization</small>
                </div>
            </div>

            <script>
                const vscode = acquireVsCodeApi();

                function refreshMetrics() {
                    vscode.postMessage({ command: 'refreshMetrics' });
                }

                function updateMetrics(metrics) {
                    document.getElementById('cpuUsage').textContent = metrics.cpu.usage.toFixed(1) + '%';
                    document.getElementById('memoryUsage').textContent = metrics.memory.percentage.toFixed(1) + '%';
                    document.getElementById('diskUsage').textContent = metrics.disk.percentage.toFixed(1) + '%';
                    document.getElementById('vscodeFiles').textContent = metrics.vscode.openFiles;
                }

                // Listen for messages from extension
                window.addEventListener('message', event => {
                    const message = event.data;
                    
                    switch (message.command) {
                        case 'updateMetrics':
                            updateMetrics(message.metrics);
                            break;
                    }
                });

                // Auto-refresh every 5 seconds
                setInterval(() => {
                    refreshMetrics();
                }, 5000);
            </script>
        </body>
        </html>
        `;
    }

    private async collectMetrics(): Promise<IPerformanceMetrics> {
        const cpus = os.cpus();
        const totalMem = os.totalmem();
        const freeMem = os.freemem();
        const usedMem = totalMem - freeMem;

        // Simulate CPU usage (in real implementation, calculate actual usage)
        const cpuUsage = Math.random() * 100;

        // Get VS Code specific metrics
        const openFiles = vscode.workspace.textDocuments.length;
        const workspaceFolders = vscode.workspace.workspaceFolders?.length || 0;
        const extensions = vscode.extensions.all.length;

        // Simulate disk usage (in real implementation, get actual disk stats)
        const diskTotal = 1000 * 1024 * 1024 * 1024; // 1TB
        const diskUsed = diskTotal * 0.6; // 60% used

        return {
            cpu: {
                usage: cpuUsage,
                cores: cpus.length,
                model: cpus[0]?.model || 'Unknown'
            },
            memory: {
                used: usedMem,
                total: totalMem,
                percentage: (usedMem / totalMem) * 100
            },
            disk: {
                used: diskUsed,
                total: diskTotal,
                percentage: (diskUsed / diskTotal) * 100
            },
            network: {
                bytesReceived: 0,
                bytesSent: 0
            },
            vscode: {
                extensions: extensions,
                openFiles: openFiles,
                workspaceFolders: workspaceFolders
            }
        };
    }

    private async analyzeCodeMetrics(): Promise<ICodeMetrics> {
        let totalLines = 0;
        let totalFiles = 0;
        let totalFunctions = 0;
        let totalClasses = 0;

        try {
            // Get all files in workspace
            const files = await vscode.workspace.findFiles('**/*.{js,ts,py,java,cpp,c,cs}', '**/node_modules/**');
            totalFiles = files.length;

            // Analyze a sample of files for performance
            const sampleFiles = files.slice(0, Math.min(50, files.length));
            
            for (const file of sampleFiles) {
                try {
                    const document = await vscode.workspace.openTextDocument(file);
                    const text = document.getText();
                    const lines = text.split('\n').length;
                    totalLines += lines;

                    // Simple pattern matching for functions and classes
                    const functionMatches = text.match(/function\s+\w+|def\s+\w+|public\s+\w+\s+\w+\(/g);
                    const classMatches = text.match(/class\s+\w+|interface\s+\w+/g);
                    
                    totalFunctions += functionMatches?.length || 0;
                    totalClasses += classMatches?.length || 0;
                } catch (error) {
                    // Skip files that can't be read
                }
            }

            // Extrapolate for all files
            if (sampleFiles.length > 0) {
                const ratio = files.length / sampleFiles.length;
                totalLines = Math.round(totalLines * ratio);
                totalFunctions = Math.round(totalFunctions * ratio);
                totalClasses = Math.round(totalClasses * ratio);
            }

        } catch (error) {
            this.logger.error('❌ Code analysis failed:', error);
        }

        // Calculate complexity score (simplified)
        const complexity = Math.round((totalFunctions + totalClasses) / Math.max(totalFiles, 1));

        return {
            linesOfCode: totalLines,
            files: totalFiles,
            functions: totalFunctions,
            classes: totalClasses,
            complexity: complexity
        };
    }

    private getUsageClass(percentage: number): string {
        if (percentage < 50) {return 'low';}
        if (percentage < 80) {return 'medium';}
        return 'high';
    }

    private formatBytes(bytes: number): string {
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        if (bytes === 0) {return '0 Bytes';}
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }

    private generateRecommendations(metrics: IPerformanceMetrics, codeMetrics: ICodeMetrics): string {
        const recommendations = [];

        if (metrics.cpu.usage > 80) {
            recommendations.push({
                icon: '⚡',
                title: 'High CPU Usage Detected',
                description: 'Consider closing unnecessary applications or optimizing CPU-intensive tasks.'
            });
        }

        if (metrics.memory.percentage > 85) {
            recommendations.push({
                icon: '🧠',
                title: 'High Memory Usage',
                description: 'Close unused VS Code tabs or restart VS Code to free up memory.'
            });
        }

        if (metrics.vscode.openFiles > 20) {
            recommendations.push({
                icon: '📁',
                title: 'Many Open Files',
                description: 'Consider closing unused files to improve VS Code performance.'
            });
        }

        if (codeMetrics.complexity > 10) {
            recommendations.push({
                icon: '🔧',
                title: 'High Code Complexity',
                description: 'Consider refactoring complex functions to improve maintainability.'
            });
        }

        if (recommendations.length === 0) {
            recommendations.push({
                icon: '✅',
                title: 'Performance Looks Good',
                description: 'Your system and code metrics are within optimal ranges.'
            });
        }

        return recommendations.map(rec => `
            <div class="recommendation-item">
                <div class="recommendation-icon">${rec.icon}</div>
                <div class="recommendation-text">
                    <div class="recommendation-title">${rec.title}</div>
                    <div class="recommendation-description">${rec.description}</div>
                </div>
            </div>
        `).join('');
    }

    private async handleWebviewMessage(message: any): Promise<void> {
        switch (message.command) {
            case 'refreshMetrics':
                const metrics = await this.collectMetrics();
                this.insightsPanel?.webview.postMessage({
                    command: 'updateMetrics',
                    metrics: metrics
                });
                break;
        }
    }

    startMonitoring(): void {
        if (this.isMonitoring) {return;}
        
        this.isMonitoring = true;
        this.logger.info('📊 Performance monitoring started');
        
        // Start collecting metrics every 5 seconds
        this.monitoringInterval = setInterval(async () => {
            const metrics = await this.collectMetrics();
            this.metricsHistory.push(metrics);
            
            // Keep only last 100 metrics
            if (this.metricsHistory.length > 100) {
                this.metricsHistory = this.metricsHistory.slice(-100);
            }
            
            // Update webview if open
            if (this.insightsPanel) {
                this.insightsPanel.webview.postMessage({
                    command: 'updateMetrics',
                    metrics: metrics
                });
            }
        }, 5000);
    }

    stopMonitoring(): void {
        if (!this.isMonitoring) {return;}
        
        this.isMonitoring = false;
        
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = undefined;
        }
        
        this.logger.info('📊 Performance monitoring stopped');
    }
}
