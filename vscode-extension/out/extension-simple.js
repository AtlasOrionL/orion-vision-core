"use strict";
/**
 * 🚀 Orion Vision Core - Simple Test Extension
 * Minimal version to test command registration
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
function activate(context) {
    console.log('🚀 Activating Orion Vision Core extension...');
    // Create output channel for logging
    const outputChannel = vscode.window.createOutputChannel('Orion Vision Core');
    outputChannel.appendLine('🚀 Orion Vision Core extension starting...');
    outputChannel.show();
    // Register simple commands without dependencies
    const commands = [
        vscode.commands.registerCommand('orion.activateAI', async () => {
            vscode.window.showInformationMessage('🤖 Orion AI Assistant activated! (Simple Test)');
            outputChannel.appendLine('✅ AI Assistant command executed');
        }),
        vscode.commands.registerCommand('orion.codeCompletion', async () => {
            vscode.window.showInformationMessage('🔧 Code Completion activated! (Simple Test)');
            outputChannel.appendLine('✅ Code Completion command executed');
        }),
        vscode.commands.registerCommand('orion.smartSearch', async () => {
            const query = await vscode.window.showInputBox({
                prompt: 'Enter search query',
                placeHolder: 'Search for code...'
            });
            if (query) {
                vscode.window.showInformationMessage(`🔍 Searching for: ${query} (Simple Test)`);
                outputChannel.appendLine(`✅ Smart Search executed: ${query}`);
            }
        }),
        vscode.commands.registerCommand('orion.mobilePreview', async () => {
            vscode.window.showInformationMessage('📱 Mobile Preview activated! (Simple Test)');
            outputChannel.appendLine('✅ Mobile Preview command executed');
        }),
        vscode.commands.registerCommand('orion.networkDebug', async () => {
            vscode.window.showInformationMessage('🌐 Network Debug activated! (Simple Test)');
            outputChannel.appendLine('✅ Network Debug command executed');
        }),
        vscode.commands.registerCommand('orion.performanceInsights', async () => {
            vscode.window.showInformationMessage('📊 Performance Insights activated! (Simple Test)');
            outputChannel.appendLine('✅ Performance Insights command executed');
        }),
        vscode.commands.registerCommand('orion.deployApp', async () => {
            vscode.window.showInformationMessage('🚀 Deploy Application activated! (Simple Test)');
            outputChannel.appendLine('✅ Deploy Application command executed');
        }),
        vscode.commands.registerCommand('orion.openDashboard', async () => {
            // Create simple webview panel
            const panel = vscode.window.createWebviewPanel('orionDashboard', 'Orion Dashboard', vscode.ViewColumn.One, {
                enableScripts: true
            });
            panel.webview.html = getSimpleDashboardHtml();
            outputChannel.appendLine('✅ Dashboard opened');
        })
    ];
    // Add all commands to subscriptions
    commands.forEach(command => context.subscriptions.push(command));
    // Add output channel to subscriptions
    context.subscriptions.push(outputChannel);
    outputChannel.appendLine('✅ Orion Vision Core extension activated successfully!');
    console.log('✅ Orion Vision Core extension activated successfully!');
}
exports.activate = activate;
function getSimpleDashboardHtml() {
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
            <p>Simple Test Version</p>
        </div>
        
        <div class="status">
            ✅ Extension Status: Active
        </div>
        
        <div class="status">
            🤖 AI Assistant: Ready
        </div>
        
        <div class="status">
            📊 Performance Monitor: Running
        </div>
        
        <div class="status">
            🌐 Network Debug: Available
        </div>
        
        <div class="status">
            📱 Mobile Preview: Ready
        </div>
    </body>
    </html>
    `;
}
function deactivate() {
    console.log('🔄 Deactivating Orion Vision Core extension...');
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension-simple.js.map