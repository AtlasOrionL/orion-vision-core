/**
 * 🚀 Orion Vision Core - Fixed Extension
 * Gradual provider testing to find the problematic class
 */

import * as vscode from 'vscode';
import { OrionConfiguration } from './config/configuration';
import { OrionLogger } from './utils/logger';

export function activate(context: vscode.ExtensionContext) {
    const logger = new OrionLogger();
    logger.info('🚀 Activating Orion Vision Core extension (Fixed Version)...');

    try {
        // Initialize configuration - TEST 1
        logger.info('📋 Testing Configuration...');
        const config = new OrionConfiguration();
        logger.info('✅ Configuration initialized successfully');

        // Test basic providers one by one
        let aiProvider: any = null;
        let codeCompletionProvider: any = null;
        let mobilePreview: any = null;
        let networkDebugger: any = null;
        let performanceMonitor: any = null;
        let deploymentManager: any = null;
        let webviewProvider: any = null;
        let statusBar: any = null;
        let treeDataProvider: any = null;

        // TEST 2: AI Provider
        try {
            logger.info('🤖 Testing AI Provider...');
            const { OrionAIProvider } = require('./providers/aiProvider');
            aiProvider = new OrionAIProvider(config);
            logger.info('✅ AI Provider initialized successfully');
        } catch (error) {
            logger.error('❌ AI Provider failed:', error);
        }

        // TEST 3: Code Completion Provider
        try {
            logger.info('🔧 Testing Code Completion Provider...');
            const { OrionCodeCompletionProvider } = require('./providers/codeCompletionProvider');
            if (aiProvider) {
                codeCompletionProvider = new OrionCodeCompletionProvider(aiProvider);
                logger.info('✅ Code Completion Provider initialized successfully');
            } else {
                logger.warn('⚠️ Skipping Code Completion Provider (AI Provider failed)');
            }
        } catch (error) {
            logger.error('❌ Code Completion Provider failed:', error);
        }

        // TEST 4: Mobile Preview Provider
        try {
            logger.info('📱 Testing Mobile Preview Provider...');
            const { OrionMobilePreview } = require('./providers/mobilePreviewProvider');
            mobilePreview = new OrionMobilePreview(config);
            logger.info('✅ Mobile Preview Provider initialized successfully');
        } catch (error) {
            logger.error('❌ Mobile Preview Provider failed:', error);
        }

        // TEST 5: Network Debugger Provider
        try {
            logger.info('🌐 Testing Network Debugger Provider...');
            const { OrionNetworkDebugger } = require('./providers/networkDebugProvider');
            networkDebugger = new OrionNetworkDebugger(config);
            logger.info('✅ Network Debugger Provider initialized successfully');
        } catch (error) {
            logger.error('❌ Network Debugger Provider failed:', error);
        }

        // TEST 6: Performance Monitor Provider
        try {
            logger.info('📊 Testing Performance Monitor Provider...');
            const { OrionPerformanceMonitor } = require('./providers/performanceProvider');
            performanceMonitor = new OrionPerformanceMonitor(config);
            logger.info('✅ Performance Monitor Provider initialized successfully');
        } catch (error) {
            logger.error('❌ Performance Monitor Provider failed:', error);
        }

        // TEST 7: Deployment Manager Provider
        try {
            logger.info('🚀 Testing Deployment Manager Provider...');
            const { OrionDeploymentManager } = require('./providers/deploymentProvider');
            deploymentManager = new OrionDeploymentManager(config);
            logger.info('✅ Deployment Manager Provider initialized successfully');
        } catch (error) {
            logger.error('❌ Deployment Manager Provider failed:', error);
        }

        // TEST 8: Webview Provider
        try {
            logger.info('🌐 Testing Webview Provider...');
            const { OrionWebviewProvider } = require('./providers/webviewProvider');
            webviewProvider = new OrionWebviewProvider(context.extensionUri);
            logger.info('✅ Webview Provider initialized successfully');
        } catch (error) {
            logger.error('❌ Webview Provider failed:', error);
        }

        // TEST 9: Status Bar
        try {
            logger.info('📊 Testing Status Bar...');
            const { OrionStatusBar } = require('./ui/statusBar');
            statusBar = new OrionStatusBar();
            logger.info('✅ Status Bar initialized successfully');
        } catch (error) {
            logger.error('❌ Status Bar failed:', error);
        }

        // TEST 10: Tree Data Provider
        try {
            logger.info('🌳 Testing Tree Data Provider...');
            const { OrionTreeDataProvider } = require('./ui/treeDataProvider');
            treeDataProvider = new OrionTreeDataProvider();
            logger.info('✅ Tree Data Provider initialized successfully');
        } catch (error) {
            logger.error('❌ Tree Data Provider failed:', error);
        }

        // Register commands with available providers
        registerCommands(context, {
            aiProvider,
            codeCompletionProvider,
            mobilePreview,
            networkDebugger,
            performanceMonitor,
            deploymentManager,
            webviewProvider
        }, logger);

        // Register providers that were successfully initialized
        registerProviders(context, {
            codeCompletionProvider,
            treeDataProvider,
            webviewProvider
        }, logger);

        // Initialize status bar if available
        if (statusBar) {
            statusBar.show();
            context.subscriptions.push(statusBar);
            logger.info('✅ Status bar activated');
        }

        // Start background services for available providers
        startBackgroundServices({
            aiProvider,
            performanceMonitor,
            networkDebugger
        }, logger);

        logger.info('✅ Orion Vision Core extension activated successfully!');
        vscode.window.showInformationMessage('🚀 Orion Vision Core activated! Check Output panel for details.');

    } catch (error) {
        logger.error('❌ Critical error during extension activation:', error);
        vscode.window.showErrorMessage(`Failed to activate Orion Vision Core: ${error instanceof Error ? error.message : String(error)}`);
    }
}

function registerCommands(context: vscode.ExtensionContext, providers: any, logger: OrionLogger) {
    logger.info('📋 Registering commands...');
    
    const commands = [
        // AI Assistant Commands
        vscode.commands.registerCommand('orion.activateAI', async () => {
            if (providers.aiProvider) {
                try {
                    await providers.aiProvider.activate();
                    vscode.window.showInformationMessage('🤖 Orion AI Assistant activated!');
                    logger.info('✅ AI Assistant activated via command');
                } catch (error) {
                    logger.error('❌ AI Assistant activation failed:', error);
                    vscode.window.showErrorMessage('Failed to activate AI Assistant');
                }
            } else {
                vscode.window.showWarningMessage('🤖 AI Assistant not available (provider failed to initialize)');
                logger.warn('⚠️ AI Assistant command called but provider not available');
            }
        }),

        // Code Completion Commands
        vscode.commands.registerCommand('orion.codeCompletion', async () => {
            if (providers.codeCompletionProvider) {
                const editor = vscode.window.activeTextEditor;
                if (editor) {
                    try {
                        await providers.codeCompletionProvider.provideCompletions(editor);
                        logger.info('✅ Code completion executed');
                    } catch (error) {
                        logger.error('❌ Code completion failed:', error);
                        vscode.window.showErrorMessage('Code completion failed');
                    }
                }
            } else {
                vscode.window.showWarningMessage('🔧 Code Completion not available');
                logger.warn('⚠️ Code completion command called but provider not available');
            }
        }),

        // Smart Search Commands
        vscode.commands.registerCommand('orion.smartSearch', async () => {
            if (providers.aiProvider) {
                const query = await vscode.window.showInputBox({
                    prompt: 'Enter search query for smart code search',
                    placeHolder: 'e.g., "function that handles user authentication"'
                });
                
                if (query) {
                    try {
                        await providers.aiProvider.smartSearch(query);
                        logger.info(`✅ Smart search executed: ${query}`);
                    } catch (error) {
                        logger.error('❌ Smart search failed:', error);
                        vscode.window.showErrorMessage('Smart search failed');
                    }
                }
            } else {
                vscode.window.showWarningMessage('🔍 Smart Search not available');
                logger.warn('⚠️ Smart search command called but AI provider not available');
            }
        }),

        // Mobile Preview Commands
        vscode.commands.registerCommand('orion.mobilePreview', async () => {
            if (providers.mobilePreview) {
                try {
                    await providers.mobilePreview.showPreview();
                    logger.info('✅ Mobile preview executed');
                } catch (error) {
                    logger.error('❌ Mobile preview failed:', error);
                    vscode.window.showErrorMessage('Mobile preview failed');
                }
            } else {
                vscode.window.showWarningMessage('📱 Mobile Preview not available');
                logger.warn('⚠️ Mobile preview command called but provider not available');
            }
        }),

        // Network Debugging Commands
        vscode.commands.registerCommand('orion.networkDebug', async () => {
            if (providers.networkDebugger) {
                try {
                    await providers.networkDebugger.startDebugging();
                    logger.info('✅ Network debugging executed');
                } catch (error) {
                    logger.error('❌ Network debugging failed:', error);
                    vscode.window.showErrorMessage('Network debugging failed');
                }
            } else {
                vscode.window.showWarningMessage('🌐 Network Debug not available');
                logger.warn('⚠️ Network debug command called but provider not available');
            }
        }),

        // Performance Insights Commands
        vscode.commands.registerCommand('orion.performanceInsights', async () => {
            if (providers.performanceMonitor) {
                try {
                    await providers.performanceMonitor.showInsights();
                    logger.info('✅ Performance insights executed');
                } catch (error) {
                    logger.error('❌ Performance insights failed:', error);
                    vscode.window.showErrorMessage('Performance insights failed');
                }
            } else {
                vscode.window.showWarningMessage('📊 Performance Insights not available');
                logger.warn('⚠️ Performance insights command called but provider not available');
            }
        }),

        // Deployment Commands
        vscode.commands.registerCommand('orion.deployApp', async () => {
            if (providers.deploymentManager) {
                try {
                    await providers.deploymentManager.deployApplication();
                    logger.info('✅ Deployment executed');
                } catch (error) {
                    logger.error('❌ Deployment failed:', error);
                    vscode.window.showErrorMessage('Deployment failed');
                }
            } else {
                vscode.window.showWarningMessage('🚀 Deploy Application not available');
                logger.warn('⚠️ Deploy command called but provider not available');
            }
        }),

        // Dashboard Commands
        vscode.commands.registerCommand('orion.openDashboard', async () => {
            // Always use simple dashboard for testing
            const panel = vscode.window.createWebviewPanel(
                'orionDashboard',
                'Orion Dashboard (Testing)',
                vscode.ViewColumn.One,
                { enableScripts: true }
            );
            panel.webview.html = getSimpleDashboardHtml();
            logger.info('✅ Dashboard opened');
        })
    ];

    commands.forEach(command => context.subscriptions.push(command));
    logger.info(`✅ ${commands.length} commands registered successfully`);
}

function registerProviders(context: vscode.ExtensionContext, providers: any, logger: OrionLogger) {
    logger.info('📋 Registering providers...');
    
    try {
        // Register code completion provider if available
        if (providers.codeCompletionProvider) {
            const completionProvider = vscode.languages.registerCompletionItemProvider(
                { scheme: 'file' },
                providers.codeCompletionProvider,
                '.'
            );
            context.subscriptions.push(completionProvider);
            logger.info('✅ Code completion provider registered');
        }

        // Register tree data provider if available
        if (providers.treeDataProvider) {
            const treeView = vscode.window.createTreeView('orionAIAssistant', {
                treeDataProvider: providers.treeDataProvider,
                showCollapseAll: true
            });
            context.subscriptions.push(treeView);
            logger.info('✅ Tree data provider registered');
        }

        // Register webview provider if available
        if (providers.webviewProvider) {
            const webviewProvider = vscode.window.registerWebviewViewProvider(
                'orionDashboard',
                providers.webviewProvider
            );
            context.subscriptions.push(webviewProvider);
            logger.info('✅ Webview provider registered');
        }

    } catch (error) {
        logger.error('❌ Provider registration failed:', error);
    }
}

function startBackgroundServices(services: any, logger: OrionLogger) {
    logger.info('🔄 Starting background services...');
    
    try {
        // Start AI provider background services if available
        if (services.aiProvider) {
            services.aiProvider.startBackgroundServices();
            logger.info('✅ AI provider background services started');
        }
        
        // Start performance monitoring if available
        if (services.performanceMonitor) {
            services.performanceMonitor.startMonitoring();
            logger.info('✅ Performance monitoring started');
        }
        
        // Start network monitoring if available
        if (services.networkDebugger) {
            services.networkDebugger.startMonitoring();
            logger.info('✅ Network monitoring started');
        }
    } catch (error) {
        logger.error('❌ Background services startup failed:', error);
    }
}

function getSimpleDashboardHtml(): string {
    return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Orion Dashboard</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                padding: 20px;
                background-color: var(--vscode-editor-background);
                color: var(--vscode-editor-foreground);
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .status {
                background-color: var(--vscode-badge-background);
                color: var(--vscode-badge-foreground);
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Orion Vision Core Dashboard</h1>
            <p>Fallback Dashboard (Provider Testing Mode)</p>
        </div>
        
        <div class="status">
            ✅ Extension Status: Active (Fixed Version)
        </div>
        
        <div class="status">
            🔍 Provider Testing: In Progress
        </div>
        
        <div class="status">
            📝 Check Output Panel: "Orion Vision Core" for detailed logs
        </div>
    </body>
    </html>
    `;
}

export function deactivate() {
    const logger = new OrionLogger();
    logger.info('🔄 Deactivating Orion Vision Core extension...');
    logger.info('✅ Orion Vision Core extension deactivated successfully!');
}
