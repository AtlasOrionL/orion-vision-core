"use strict";
/**
 * 🤖 Orion AI Provider
 * Connects VS Code extension to Orion Vision Core AI capabilities
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
exports.OrionAIProvider = void 0;
const vscode = __importStar(require("vscode"));
const axios_1 = __importDefault(require("axios"));
const logger_1 = require("../utils/logger");
class OrionAIProvider {
    constructor(config) {
        this.isConnected = false;
        this.config = config;
        this.logger = new logger_1.OrionLogger();
        this.baseUrl = `http://${config.getServerHost()}:${config.getServerPort()}`;
    }
    async activate() {
        try {
            this.logger.info('🤖 Activating Orion AI Provider...');
            this.logger.info(`🔗 Attempting to connect to: ${this.baseUrl}`);
            // Test connection with retry logic
            let retries = this.config.getRetryAttempts();
            let lastError;
            for (let i = 0; i < retries; i++) {
                try {
                    await this.testConnection();
                    this.isConnected = true;
                    this.startBackgroundServices();
                    this.logger.info('✅ Orion AI Provider activated successfully!');
                    vscode.window.showInformationMessage('🤖 Connected to Orion Vision Core AI!');
                    return;
                }
                catch (error) {
                    lastError = error;
                    this.logger.warn(`⚠️ Connection attempt ${i + 1}/${retries} failed: ${error}`);
                    if (i < retries - 1) {
                        this.logger.info(`🔄 Retrying in 2 seconds...`);
                        await new Promise(resolve => setTimeout(resolve, 2000));
                    }
                }
            }
            // All retries failed
            throw lastError;
        }
        catch (error) {
            this.logger.error('❌ Failed to activate AI Provider after all retries:', error);
            this.isConnected = false;
            // Show user-friendly error message
            const errorMessage = this.getUserFriendlyErrorMessage(error);
            vscode.window.showErrorMessage(errorMessage, 'Retry', 'Open Settings').then(selection => {
                if (selection === 'Retry') {
                    this.activate();
                }
                else if (selection === 'Open Settings') {
                    vscode.commands.executeCommand('workbench.action.openSettings', 'orion');
                }
            });
        }
    }
    getUserFriendlyErrorMessage(error) {
        const baseMessage = 'AI Assistant not available';
        if (error.message.includes('Server not running')) {
            return `${baseMessage}: Orion server is not running on ${this.baseUrl}. Please start the server first.`;
        }
        else if (error.message.includes('timeout')) {
            return `${baseMessage}: Connection timeout. Please check your network connection.`;
        }
        else if (error.message.includes('ECONNREFUSED')) {
            return `${baseMessage}: Cannot connect to ${this.baseUrl}. Please verify the server is running.`;
        }
        else {
            return `${baseMessage}: ${error.message}`;
        }
    }
    async testConnection() {
        try {
            this.logger.info(`🔗 Testing connection to ${this.baseUrl}/api/health`);
            const response = await axios_1.default.get(`${this.baseUrl}/api/health`, {
                timeout: this.config.getConnectionTimeout(),
                headers: {
                    'Accept': 'application/json',
                    'User-Agent': 'Orion-VS-Code-Extension/1.0.0'
                }
            });
            this.logger.info(`📡 Server response: ${response.status} - ${JSON.stringify(response.data)}`);
            if (response.status !== 200) {
                throw new Error(`Server responded with status ${response.status}`);
            }
            // Validate response structure
            if (!response.data || typeof response.data !== 'object') {
                throw new Error('Invalid response format from server');
            }
            this.logger.info('✅ Connection test successful');
        }
        catch (error) {
            this.logger.error(`❌ Connection test failed: ${error.message}`);
            if (error.code === 'ECONNREFUSED') {
                throw new Error(`Cannot connect to Orion Vision Core at ${this.baseUrl} - Server not running`);
            }
            else if (error.code === 'ETIMEDOUT') {
                throw new Error(`Connection timeout to Orion Vision Core at ${this.baseUrl}`);
            }
            else {
                throw new Error(`Cannot connect to Orion Vision Core at ${this.baseUrl}: ${error.message}`);
            }
        }
    }
    async generateCompletion(request) {
        if (!this.isConnected) {
            throw new Error('AI Provider not connected. Please activate first.');
        }
        try {
            const response = await axios_1.default.post(`${this.baseUrl}/api/ai/completion`, {
                prompt: request.prompt,
                context: request.context,
                language: request.language,
                type: request.type
            }, {
                timeout: 10000,
                headers: {
                    // eslint-disable-next-line @typescript-eslint/naming-convention
                    'Content-Type': 'application/json'
                }
            });
            return {
                result: response.data.result,
                confidence: response.data.confidence || 0.8,
                suggestions: response.data.suggestions || [],
                metadata: response.data.metadata || {}
            };
        }
        catch (error) {
            this.logger.error('❌ AI completion request failed:', error);
            throw new Error('Failed to generate AI completion');
        }
    }
    async smartSearch(query) {
        if (!this.isConnected) {
            vscode.window.showErrorMessage('AI Provider not connected');
            return;
        }
        try {
            const response = await this.generateCompletion({
                prompt: query,
                type: 'search'
            });
            // Show search results in a new webview
            const panel = vscode.window.createWebviewPanel('orionSmartSearch', 'Orion Smart Search Results', vscode.ViewColumn.Two, {
                enableScripts: true,
                retainContextWhenHidden: true
            });
            panel.webview.html = this.getSearchResultsHtml(query, response);
        }
        catch (error) {
            this.logger.error('❌ Smart search failed:', error);
            vscode.window.showErrorMessage('Smart search failed. Please try again.');
        }
    }
    getSearchResultsHtml(query, response) {
        return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Orion Smart Search</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    padding: 20px;
                    background-color: var(--vscode-editor-background);
                    color: var(--vscode-editor-foreground);
                }
                .search-header {
                    border-bottom: 1px solid var(--vscode-panel-border);
                    padding-bottom: 15px;
                    margin-bottom: 20px;
                }
                .search-query {
                    font-size: 18px;
                    font-weight: bold;
                    color: var(--vscode-textLink-foreground);
                }
                .confidence-score {
                    margin-top: 10px;
                    padding: 5px 10px;
                    background-color: var(--vscode-badge-background);
                    color: var(--vscode-badge-foreground);
                    border-radius: 3px;
                    display: inline-block;
                }
                .search-result {
                    background-color: var(--vscode-editor-inactiveSelectionBackground);
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 15px;
                    border-left: 3px solid var(--vscode-textLink-foreground);
                }
                .suggestions {
                    margin-top: 20px;
                }
                .suggestion-item {
                    padding: 8px 12px;
                    background-color: var(--vscode-list-hoverBackground);
                    margin: 5px 0;
                    border-radius: 3px;
                    cursor: pointer;
                }
                .suggestion-item:hover {
                    background-color: var(--vscode-list-activeSelectionBackground);
                }
            </style>
        </head>
        <body>
            <div class="search-header">
                <div class="search-query">🔍 "${query}"</div>
                <div class="confidence-score">Confidence: ${Math.round(response.confidence * 100)}%</div>
            </div>
            
            <div class="search-result">
                <h3>🎯 AI Analysis Result</h3>
                <pre>${response.result}</pre>
            </div>
            
            ${response.suggestions && response.suggestions.length > 0 ? `
            <div class="suggestions">
                <h3>💡 Related Suggestions</h3>
                ${response.suggestions.map(suggestion => `
                    <div class="suggestion-item">${suggestion}</div>
                `).join('')}
            </div>
            ` : ''}
        </body>
        </html>
        `;
    }
    async explainCode(code, language) {
        return await this.generateCompletion({
            prompt: `Explain this ${language} code:\n\n${code}`,
            context: `Language: ${language}`,
            language: language,
            type: 'explanation'
        });
    }
    async refactorCode(code, language) {
        return await this.generateCompletion({
            prompt: `Refactor and improve this ${language} code:\n\n${code}`,
            context: `Language: ${language}`,
            language: language,
            type: 'refactor'
        });
    }
    async debugCode(code, error, language) {
        return await this.generateCompletion({
            prompt: `Debug this ${language} code that has the following error: ${error}\n\nCode:\n${code}`,
            context: `Language: ${language}, Error: ${error}`,
            language: language,
            type: 'debug'
        });
    }
    startBackgroundServices() {
        this.logger.info('🔄 Starting AI Provider background services...');
        // Start periodic health checks
        setInterval(async () => {
            try {
                await this.testConnection();
                if (!this.isConnected) {
                    this.isConnected = true;
                    vscode.window.showInformationMessage('🤖 Reconnected to Orion Vision Core!');
                }
            }
            catch (error) {
                if (this.isConnected) {
                    this.isConnected = false;
                    vscode.window.showWarningMessage('⚠️ Lost connection to Orion Vision Core');
                }
            }
        }, 30000); // Check every 30 seconds
    }
    isAIConnected() {
        return this.isConnected;
    }
    getConnectionStatus() {
        return this.isConnected ? 'Connected' : 'Disconnected';
    }
}
exports.OrionAIProvider = OrionAIProvider;
//# sourceMappingURL=aiProvider.js.map