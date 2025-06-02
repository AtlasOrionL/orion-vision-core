"use strict";
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
exports.deactivate = exports.activate = void 0;
const vscode = __importStar(require("vscode"));
const aiProvider_1 = require("./providers/aiProvider");
const codeCompletionProvider_1 = require("./providers/codeCompletionProvider");
const mobilePreviewProvider_1 = require("./providers/mobilePreviewProvider");
const networkDebugProvider_1 = require("./providers/networkDebugProvider");
const performanceProvider_1 = require("./providers/performanceProvider");
const deploymentProvider_1 = require("./providers/deploymentProvider");
const webviewProvider_1 = require("./providers/webviewProvider");
const chatProvider_1 = require("./providers/chatProvider");
const terminalProvider_1 = require("./providers/terminalProvider");
const fileSystemProvider_1 = require("./providers/fileSystemProvider");
const apiProvider_1 = require("./providers/apiProvider");
const statusBar_1 = require("./ui/statusBar");
const treeDataProvider_1 = require("./ui/treeDataProvider");
const configuration_1 = require("./config/configuration");
const logger_1 = require("./utils/logger");
function activate(context) {
    const logger = new logger_1.OrionLogger();
    logger.info('🚀 Activating Orion Vision Core extension...');
    // Initialize configuration
    const config = new configuration_1.OrionConfiguration();
    // Initialize providers
    const aiProvider = new aiProvider_1.OrionAIProvider(config);
    const codeCompletionProvider = new codeCompletionProvider_1.OrionCodeCompletionProvider(aiProvider);
    const mobilePreview = new mobilePreviewProvider_1.OrionMobilePreview(config);
    const networkDebugger = new networkDebugProvider_1.OrionNetworkDebugger(config);
    const performanceMonitor = new performanceProvider_1.OrionPerformanceMonitor(config);
    const deploymentManager = new deploymentProvider_1.OrionDeploymentManager(config);
    // Initialize new enhanced providers
    const chatProvider = new chatProvider_1.OrionChatProvider(context.extensionUri);
    const terminalProvider = new terminalProvider_1.OrionTerminalProvider(context.extensionUri);
    const fileSystemProvider = new fileSystemProvider_1.OrionFileSystemProvider(context.extensionUri);
    const apiProvider = new apiProvider_1.OrionAPIProvider(context.extensionUri);
    // Initialize UI components
    const statusBar = new statusBar_1.OrionStatusBar();
    const treeDataProvider = new treeDataProvider_1.OrionTreeDataProvider();
    const webviewProvider = new webviewProvider_1.OrionWebviewProvider(context.extensionUri);
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
        }
        else {
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
exports.activate = activate;
function registerCommands(context, providers) {
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
function registerProviders(context, providers) {
    // Register code completion provider
    const completionProvider = vscode.languages.registerCompletionItemProvider({ scheme: 'file' }, providers.codeCompletionProvider, '.');
    // Register tree data provider
    const treeView = vscode.window.createTreeView('orionAIAssistant', {
        treeDataProvider: providers.treeDataProvider,
        showCollapseAll: true
    });
    // Register webview provider
    const webviewProvider = vscode.window.registerWebviewViewProvider('orionDashboard', providers.webviewProvider);
    // Register new enhanced providers
    const chatViewProvider = vscode.window.registerWebviewViewProvider(chatProvider_1.OrionChatProvider.viewType, providers.chatProvider);
    const terminalViewProvider = vscode.window.registerWebviewViewProvider(terminalProvider_1.OrionTerminalProvider.viewType, providers.terminalProvider);
    const fileSystemViewProvider = vscode.window.registerWebviewViewProvider(fileSystemProvider_1.OrionFileSystemProvider.viewType, providers.fileSystemProvider);
    const apiViewProvider = vscode.window.registerWebviewViewProvider(apiProvider_1.OrionAPIProvider.viewType, providers.apiProvider);
    context.subscriptions.push(completionProvider, treeView, webviewProvider, chatViewProvider, terminalViewProvider, fileSystemViewProvider, apiViewProvider);
}
function startBackgroundServices(services) {
    // Start AI provider background services
    services.aiProvider.startBackgroundServices();
    // Start performance monitoring
    services.performanceMonitor.startMonitoring();
    // Start network monitoring
    services.networkDebugger.startMonitoring();
}
function deactivate() {
    const logger = new logger_1.OrionLogger();
    logger.info('🔄 Deactivating Orion Vision Core extension...');
    // Cleanup resources
    // This will be called when the extension is deactivated
    logger.info('✅ Orion Vision Core extension deactivated successfully!');
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map