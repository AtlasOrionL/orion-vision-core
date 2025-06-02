/**
 * 📱 Orion Mobile Preview Provider
 * Mobile app preview and testing capabilities
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { OrionConfiguration } from '../config/configuration';
import { OrionLogger } from '../utils/logger';

export interface IMobileDevice {
    name: string;
    width: number;
    height: number;
    pixelRatio: number;
    userAgent: string;
}

export class OrionMobilePreview {
    private config: OrionConfiguration;
    private logger: OrionLogger;
    private previewPanel: vscode.WebviewPanel | undefined;

    private readonly devices: IMobileDevice[] = [
        {
            name: 'iPhone 14 Pro',
            width: 393,
            height: 852,
            pixelRatio: 3,
            userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15'
        },
        {
            name: 'iPhone 14 Pro Max',
            width: 430,
            height: 932,
            pixelRatio: 3,
            userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15'
        },
        {
            name: 'Samsung Galaxy S23',
            width: 360,
            height: 780,
            pixelRatio: 3,
            userAgent: 'Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36'
        },
        {
            name: 'iPad Pro 12.9"',
            width: 1024,
            height: 1366,
            pixelRatio: 2,
            userAgent: 'Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15'
        },
        {
            name: 'Google Pixel 7',
            width: 412,
            height: 915,
            pixelRatio: 2.625,
            userAgent: 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36'
        }
    ];

    constructor(config: OrionConfiguration) {
        this.config = config;
        this.logger = new OrionLogger();
    }

    async showPreview(): Promise<void> {
        try {
            this.logger.info('📱 Opening mobile preview...');

            // Get current file
            const activeEditor = vscode.window.activeTextEditor;
            if (!activeEditor) {
                vscode.window.showErrorMessage('No active file to preview');
                return;
            }

            const document = activeEditor.document;
            const filePath = document.fileName;
            const fileExtension = path.extname(filePath).toLowerCase();

            // Check if file is previewable
            if (!this.isPreviewableFile(fileExtension)) {
                vscode.window.showErrorMessage('File type not supported for mobile preview');
                return;
            }

            // Select device
            const selectedDevice = await this.selectDevice();
            if (!selectedDevice) {
                return;
            }

            // Create or show preview panel
            if (this.previewPanel) {
                this.previewPanel.reveal(vscode.ViewColumn.Two);
            } else {
                this.previewPanel = vscode.window.createWebviewPanel(
                    'orionMobilePreview',
                    `📱 Mobile Preview - ${selectedDevice.name}`,
                    vscode.ViewColumn.Two,
                    {
                        enableScripts: true,
                        retainContextWhenHidden: true,
                        localResourceRoots: [vscode.Uri.file(path.dirname(filePath))]
                    }
                );

                this.previewPanel.onDidDispose(() => {
                    this.previewPanel = undefined;
                });
            }

            // Generate preview content
            const previewContent = await this.generatePreviewContent(filePath, selectedDevice);
            this.previewPanel.webview.html = previewContent;

            // Set up auto-refresh on file changes
            this.setupAutoRefresh(document, selectedDevice);

        } catch (error) {
            this.logger.error('❌ Mobile preview failed:', error);
            vscode.window.showErrorMessage('Failed to open mobile preview');
        }
    }

    private isPreviewableFile(extension: string): boolean {
        const supportedExtensions = ['.html', '.htm', '.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte'];
        return supportedExtensions.includes(extension);
    }

    private async selectDevice(): Promise<IMobileDevice | undefined> {
        const deviceOptions = this.devices.map(device => ({
            label: device.name,
            description: `${device.width}x${device.height} @${device.pixelRatio}x`,
            device: device
        }));

        const selected = await vscode.window.showQuickPick(deviceOptions, {
            placeHolder: 'Select mobile device for preview'
        });

        return selected?.device;
    }

    private async generatePreviewContent(filePath: string, device: IMobileDevice): Promise<string> {
        const fileUri = vscode.Uri.file(filePath);
        const webviewUri = this.previewPanel?.webview.asWebviewUri(fileUri);

        return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Orion Mobile Preview</title>
            <style>
                body {
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                
                .device-frame {
                    background: #1a1a1a;
                    border-radius: 30px;
                    padding: 20px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                    position: relative;
                }
                
                .device-screen {
                    width: ${device.width}px;
                    height: ${device.height}px;
                    background: white;
                    border-radius: 20px;
                    overflow: hidden;
                    position: relative;
                    border: 2px solid #333;
                }
                
                .device-header {
                    background: #000;
                    color: white;
                    padding: 10px;
                    text-align: center;
                    font-size: 12px;
                    font-weight: bold;
                }
                
                .preview-iframe {
                    width: 100%;
                    height: calc(100% - 40px);
                    border: none;
                    background: white;
                }
                
                .device-controls {
                    position: absolute;
                    top: -50px;
                    right: 0;
                    display: flex;
                    gap: 10px;
                }
                
                .control-btn {
                    background: rgba(255,255,255,0.2);
                    border: none;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 12px;
                }
                
                .control-btn:hover {
                    background: rgba(255,255,255,0.3);
                }
                
                .device-info {
                    position: absolute;
                    bottom: -40px;
                    left: 0;
                    color: white;
                    font-size: 12px;
                    opacity: 0.8;
                }
                
                .loading {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100%;
                    font-size: 16px;
                    color: #666;
                }
                
                .error {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100%;
                    font-size: 14px;
                    color: #e74c3c;
                    text-align: center;
                    padding: 20px;
                }
            </style>
        </head>
        <body>
            <div class="device-frame">
                <div class="device-controls">
                    <button class="control-btn" onclick="refreshPreview()">🔄 Refresh</button>
                    <button class="control-btn" onclick="toggleOrientation()">📱 Rotate</button>
                    <button class="control-btn" onclick="openDevTools()">🔧 DevTools</button>
                </div>
                
                <div class="device-screen" id="deviceScreen">
                    <div class="device-header">
                        📱 ${device.name} - ${device.width}x${device.height}
                    </div>
                    
                    <div id="previewContent" class="preview-iframe">
                        <div class="loading">
                            🔄 Loading preview...
                        </div>
                    </div>
                </div>
                
                <div class="device-info">
                    Resolution: ${device.width}x${device.height} | Pixel Ratio: ${device.pixelRatio}x
                </div>
            </div>

            <script>
                let isLandscape = false;
                
                function loadPreview() {
                    const content = document.getElementById('previewContent');
                    
                    try {
                        // Determine how to load the file based on extension
                        const filePath = '${filePath}';
                        const extension = filePath.split('.').pop().toLowerCase();
                        
                        if (extension === 'html' || extension === 'htm') {
                            // Load HTML file directly
                            content.innerHTML = '<iframe src="${webviewUri}" class="preview-iframe"></iframe>';
                        } else if (extension === 'js' || extension === 'ts') {
                            // Show JavaScript/TypeScript code with syntax highlighting
                            content.innerHTML = \`
                                <div style="padding: 20px; font-family: monospace; font-size: 14px; line-height: 1.5;">
                                    <h3>📄 JavaScript/TypeScript Preview</h3>
                                    <p>This file contains JavaScript/TypeScript code.</p>
                                    <p>For full mobile preview, create an HTML file that includes this script.</p>
                                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin-top: 15px;">
                                        <strong>Suggestions:</strong><br>
                                        • Create an HTML file that imports this script<br>
                                        • Use a bundler like Webpack or Vite<br>
                                        • Test with a local development server
                                    </div>
                                </div>
                            \`;
                        } else {
                            // Unsupported file type
                            content.innerHTML = \`
                                <div class="error">
                                    ❌ File type not supported for mobile preview<br>
                                    Supported: HTML, JavaScript, TypeScript
                                </div>
                            \`;
                        }
                    } catch (error) {
                        content.innerHTML = \`
                            <div class="error">
                                ❌ Failed to load preview<br>
                                \${error.message}
                            </div>
                        \`;
                    }
                }
                
                function refreshPreview() {
                    loadPreview();
                }
                
                function toggleOrientation() {
                    const screen = document.getElementById('deviceScreen');
                    const currentWidth = ${device.width};
                    const currentHeight = ${device.height};
                    
                    if (!isLandscape) {
                        screen.style.width = currentHeight + 'px';
                        screen.style.height = currentWidth + 'px';
                        isLandscape = true;
                    } else {
                        screen.style.width = currentWidth + 'px';
                        screen.style.height = currentHeight + 'px';
                        isLandscape = false;
                    }
                }
                
                function openDevTools() {
                    // Simulate opening dev tools
                    alert('🔧 DevTools would open here in a real mobile environment');
                }
                
                // Load preview on page load
                window.addEventListener('load', loadPreview);
            </script>
        </body>
        </html>
        `;
    }

    private setupAutoRefresh(document: vscode.TextDocument, device: IMobileDevice): void {
        // Watch for file changes and auto-refresh preview
        const disposable = vscode.workspace.onDidSaveTextDocument(async (savedDocument) => {
            if (savedDocument.uri.toString() === document.uri.toString() && this.previewPanel) {
                this.logger.info('📱 Auto-refreshing mobile preview...');
                const newContent = await this.generatePreviewContent(savedDocument.fileName, device);
                this.previewPanel.webview.html = newContent;
            }
        });

        // Clean up when preview panel is disposed
        this.previewPanel?.onDidDispose(() => {
            disposable.dispose();
        });
    }
}
