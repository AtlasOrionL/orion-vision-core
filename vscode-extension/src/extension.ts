/**
 * 🚀 Orion Vision Core - VS Code Extension
 * AI-powered development assistant with advanced capabilities
 * 
 * Features:
 * - AI-powered code completion
 * - Smart code search and navigation
 * - Mobile app preview and testing
 * - Network debugging tools
 * - Performance insights
 * - Real-time collaboration
 * - Automated deployment
 */

import * as vscode from 'vscode';
import { OrionAIProvider } from './providers/aiProvider';
import { OrionCodeCompletionProvider } from './providers/codeCompletionProvider';
import { OrionMobilePreview } from './providers/mobilePreviewProvider';
import { OrionNetworkDebugger } from './providers/networkDebugProvider';
import { OrionPerformanceMonitor } from './providers/performanceProvider';
import { OrionDeploymentManager } from './providers/deploymentProvider';
import { OrionWebviewProvider } from './providers/webviewProvider';
import { OrionChatProvider } from './providers/chatProvider';
import { OrionTerminalProvider } from './providers/terminalProvider';
import { OrionFileSystemProvider } from './providers/fileSystemProvider';
import { OrionAPIProvider } from './providers/apiProvider';
import { OrionStatusBar } from './ui/statusBar';
import { OrionTreeDataProvider } from './ui/treeDataProvider';
import { OrionConfiguration } from './config/configuration';
import { OrionLogger } from './utils/logger';

export function activate(context: vscode.ExtensionContext) {
    const logger = new OrionLogger();
    logger.info('🚀 Activating Orion Vision Core extension...');

    // Initialize configuration
    const config = new OrionConfiguration();
    
    // Initialize providers
    const aiProvider = new OrionAIProvider(config);
    const codeCompletionProvider = new OrionCodeCompletionProvider(aiProvider);
    const mobilePreview = new OrionMobilePreview(config);
    const networkDebugger = new OrionNetworkDebugger(config);
    const performanceMonitor = new OrionPerformanceMonitor(config);
    const deploymentManager = new OrionDeploymentManager(config);

    // Initialize new enhanced providers
    const chatProvider = new OrionChatProvider(context.extensionUri);
    const terminalProvider = new OrionTerminalProvider(context.extensionUri);
    const fileSystemProvider = new OrionFileSystemProvider(context.extensionUri);
    const apiProvider = new OrionAPIProvider(context.extensionUri);
    
    // Initialize UI components
    const statusBar = new OrionStatusBar();
    const treeDataProvider = new OrionTreeDataProvider();
    const webviewProvider = new OrionWebviewProvider(context.extensionUri);

    // Register commands
    registerCommands(context, {
        aiProvider,
        codeCompletionProvider,
        mobilePreview,
        networkDebugger,
        performanceMonitor,
        deploymentManager,
        webviewProvider,
        chatProvider,
        terminalProvider,
        fileSystemProvider,
        apiProvider
    });

    // Register providers
    registerProviders(context, {
        codeCompletionProvider,
        treeDataProvider,
        webviewProvider,
        chatProvider,
        terminalProvider,
        fileSystemProvider,
        apiProvider
    });

    // Initialize status bar
    statusBar.show();
    statusBar.updateStatus('Disconnected', 'Click to activate AI Assistant');
    context.subscriptions.push(statusBar);

    // Update status bar when AI Provider status changes
    const updateStatusBar = () => {
        if (aiProvider.isAIConnected()) {
            statusBar.updateStatus('Connected', 'AI Assistant is ready');
        } else {
            statusBar.updateStatus('Disconnected', 'Click to activate AI Assistant');
        }
    };

    // Check status periodically
    setInterval(updateStatusBar, 5000);

    // Start background services
    startBackgroundServices({
        aiProvider,
        performanceMonitor,
        networkDebugger
    });

    logger.info('✅ Orion Vision Core extension activated successfully!');
}

function registerCommands(context: vscode.ExtensionContext, providers: any) {
    const commands = [
        // AI Assistant Commands
        vscode.commands.registerCommand('orion.activateAI', async () => {
            await providers.aiProvider.activate();
            vscode.window.showInformationMessage('🤖 Orion AI Assistant activated!');
        }),

        // Code Completion Commands
        vscode.commands.registerCommand('orion.codeCompletion', async () => {
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                await providers.codeCompletionProvider.provideCompletions(editor);
            }
        }),

        // Smart Search Commands
        vscode.commands.registerCommand('orion.smartSearch', async () => {
            const query = await vscode.window.showInputBox({
                prompt: 'Enter search query for smart code search',
                placeHolder: 'e.g., "function that handles user authentication"'
            });
            
            if (query) {
                await providers.aiProvider.smartSearch(query);
            }
        }),

        // Mobile Preview Commands
        vscode.commands.registerCommand('orion.mobilePreview', async () => {
            await providers.mobilePreview.showPreview();
        }),

        // Network Debugging Commands
        vscode.commands.registerCommand('orion.networkDebug', async () => {
            await providers.networkDebugger.startDebugging();
        }),

        // Performance Insights Commands
        vscode.commands.registerCommand('orion.performanceInsights', async () => {
            await providers.performanceMonitor.showInsights();
        }),

        // Deployment Commands
        vscode.commands.registerCommand('orion.deployApp', async () => {
            await providers.deploymentManager.deployApplication();
        }),

        // Dashboard Commands
        vscode.commands.registerCommand('orion.openDashboard', async () => {
            await providers.webviewProvider.showDashboard();
        }),

        // Enhanced Chat Commands
        vscode.commands.registerCommand('orion.openChat', async () => {
            vscode.window.showInformationMessage('💬 Opening Orion AI Chat...');
        }),

        // Terminal Management Commands
        vscode.commands.registerCommand('orion.openTerminal', async () => {
            vscode.window.showInformationMessage('🖥️ Opening Terminal Manager...');
        }),

        // File System Commands
        vscode.commands.registerCommand('orion.openFileSystem', async () => {
            vscode.window.showInformationMessage('📁 Opening File System Manager...');
        }),

        // API Provider Commands
        vscode.commands.registerCommand('orion.openAPIManager', async () => {
            vscode.window.showInformationMessage('🔌 Opening API Provider Manager...');
        }),

        vscode.commands.registerCommand('orion.configureAPIs', async () => {
            const choice = await vscode.window.showQuickPick([
                'Configure Ollama',
                'Configure OpenRouter',
                'Configure OpenAI',
                'Configure Anthropic',
                'Add Custom Provider'
            ], {
                placeHolder: 'Select API provider to configure'
            });

            if (choice) {
                vscode.window.showInformationMessage(`🔧 Configuring ${choice}...`);
            }
        })
    ];

    commands.forEach(command => context.subscriptions.push(command));
}

function registerProviders(context: vscode.ExtensionContext, providers: any) {
    // Register code completion provider
    const completionProvider = vscode.languages.registerCompletionItemProvider(
        { scheme: 'file' },
        providers.codeCompletionProvider,
        '.'
    );

    // Register tree data provider
    const treeView = vscode.window.createTreeView('orionAIAssistant', {
        treeDataProvider: providers.treeDataProvider,
        showCollapseAll: true
    });

    // Register webview provider
    const webviewProvider = vscode.window.registerWebviewViewProvider(
        'orionDashboard',
        providers.webviewProvider
    );

    // Register new enhanced providers
    const chatViewProvider = vscode.window.registerWebviewViewProvider(
        OrionChatProvider.viewType,
        providers.chatProvider
    );

    const terminalViewProvider = vscode.window.registerWebviewViewProvider(
        OrionTerminalProvider.viewType,
        providers.terminalProvider
    );

    const fileSystemViewProvider = vscode.window.registerWebviewViewProvider(
        OrionFileSystemProvider.viewType,
        providers.fileSystemProvider
    );

    const apiViewProvider = vscode.window.registerWebviewViewProvider(
        OrionAPIProvider.viewType,
        providers.apiProvider
    );

    context.subscriptions.push(
        completionProvider,
        treeView,
        webviewProvider,
        chatViewProvider,
        terminalViewProvider,
        fileSystemViewProvider,
        apiViewProvider
    );
}

function startBackgroundServices(services: any) {
    // Start AI provider background services
    services.aiProvider.startBackgroundServices();
    
    // Start performance monitoring
    services.performanceMonitor.startMonitoring();
    
    // Start network monitoring
    services.networkDebugger.startMonitoring();
}

export function deactivate() {
    const logger = new OrionLogger();
    logger.info('🔄 Deactivating Orion Vision Core extension...');
    
    // Cleanup resources
    // This will be called when the extension is deactivated
    
    logger.info('✅ Orion Vision Core extension deactivated successfully!');
}
