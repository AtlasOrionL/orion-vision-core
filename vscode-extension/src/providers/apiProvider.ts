/**
 * 🔌 Orion Multi-API Provider
 * Manages multiple AI API connections and configurations
 */

import * as vscode from 'vscode';
import { OrionConfiguration } from '../config/configuration';
import { OrionLogger } from '../utils/logger';
import fetch from 'node-fetch';

export interface APIProvider {
    id: string;
    name: string;
    type: 'ollama' | 'openrouter' | 'openai' | 'anthropic' | 'custom';
    baseUrl: string;
    apiKey?: string;
    models: string[];
    isActive: boolean;
    isConnected: boolean;
    lastUsed?: Date;
    usage?: {
        requests: number;
        tokens: number;
        cost: number;
    };
}

export interface APIRequest {
    id: string;
    providerId: string;
    model: string;
    prompt: string;
    response?: string;
    timestamp: Date;
    duration?: number;
    tokens?: number;
    cost?: number;
    status: 'pending' | 'completed' | 'failed';
    error?: string;
}

export class OrionAPIProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'orionAPIProvider';
    
    private _view?: vscode.WebviewView;
    private config: OrionConfiguration;
    private logger: OrionLogger;
    private providers: Map<string, APIProvider> = new Map();
    private activeProvider: APIProvider | null = null;
    private requestHistory: APIRequest[] = [];

    constructor(private readonly _extensionUri: vscode.Uri) {
        this.config = new OrionConfiguration();
        this.logger = new OrionLogger();
        this._initializeDefaultProviders();
    }

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        webviewView.webview.onDidReceiveMessage(
            message => this._handleWebviewMessage(message),
            undefined,
            []
        );

        this.logger.info('🔌 API Provider initialized');
    }

    private async _handleWebviewMessage(message: any) {
        switch (message.type) {
            case 'addProvider':
                await this._addProvider(message.provider);
                break;
            case 'updateProvider':
                await this._updateProvider(message.providerId, message.updates);
                break;
            case 'deleteProvider':
                await this._deleteProvider(message.providerId);
                break;
            case 'testProvider':
                await this._testProvider(message.providerId);
                break;
            case 'setActiveProvider':
                await this._setActiveProvider(message.providerId);
                break;
            case 'testRequest':
                await this._testRequest(message.providerId, message.model, message.prompt);
                break;
            case 'clearHistory':
                await this._clearHistory();
                break;
            case 'exportConfig':
                await this._exportConfig();
                break;
            case 'importConfig':
                await this._importConfig();
                break;
        }
    }

    private async _initializeDefaultProviders() {
        // Ollama (Local)
        const ollama: APIProvider = {
            id: 'ollama-local',
            name: 'Ollama (Local)',
            type: 'ollama',
            baseUrl: 'http://localhost:11434',
            models: ['llama2', 'codellama', 'mistral', 'neural-chat'],
            isActive: true,
            isConnected: false,
            usage: { requests: 0, tokens: 0, cost: 0 }
        };

        // OpenRouter
        const openrouter: APIProvider = {
            id: 'openrouter',
            name: 'OpenRouter',
            type: 'openrouter',
            baseUrl: 'https://openrouter.ai/api/v1',
            models: [
                'microsoft/wizardlm-2-8x22b',
                'meta-llama/llama-3-8b-instruct:free',
                'mistralai/mistral-7b-instruct:free',
                'huggingface/starcoder2-15b:free'
            ],
            isActive: false,
            isConnected: false,
            usage: { requests: 0, tokens: 0, cost: 0 }
        };

        // OpenAI
        const openai: APIProvider = {
            id: 'openai',
            name: 'OpenAI',
            type: 'openai',
            baseUrl: 'https://api.openai.com/v1',
            models: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'gpt-3.5-turbo-16k'],
            isActive: false,
            isConnected: false,
            usage: { requests: 0, tokens: 0, cost: 0 }
        };

        // Anthropic
        const anthropic: APIProvider = {
            id: 'anthropic',
            name: 'Anthropic',
            type: 'anthropic',
            baseUrl: 'https://api.anthropic.com/v1',
            models: ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
            isActive: false,
            isConnected: false,
            usage: { requests: 0, tokens: 0, cost: 0 }
        };

        this.providers.set(ollama.id, ollama);
        this.providers.set(openrouter.id, openrouter);
        this.providers.set(openai.id, openai);
        this.providers.set(anthropic.id, anthropic);

        this.activeProvider = ollama;
        
        // Load saved configurations
        await this._loadSavedConfigurations();
    }

    private async _addProvider(providerData: any) {
        const provider: APIProvider = {
            id: this._generateId(),
            name: providerData.name,
            type: providerData.type,
            baseUrl: providerData.baseUrl,
            apiKey: providerData.apiKey,
            models: providerData.models || [],
            isActive: false,
            isConnected: false,
            usage: { requests: 0, tokens: 0, cost: 0 }
        };

        this.providers.set(provider.id, provider);
        await this._saveConfigurations();
        this._updateWebview();
        
        this.logger.info(`🔌 API Provider added: ${provider.name}`);
    }

    private async _updateProvider(providerId: string, updates: any) {
        const provider = this.providers.get(providerId);
        if (!provider) return;

        Object.assign(provider, updates);
        await this._saveConfigurations();
        this._updateWebview();
        
        this.logger.info(`🔌 API Provider updated: ${provider.name}`);
    }

    private async _deleteProvider(providerId: string) {
        const provider = this.providers.get(providerId);
        if (!provider) return;

        this.providers.delete(providerId);
        
        if (this.activeProvider?.id === providerId) {
            this.activeProvider = Array.from(this.providers.values())[0] || null;
        }

        await this._saveConfigurations();
        this._updateWebview();
        
        this.logger.info(`🗑️ API Provider deleted: ${provider.name}`);
    }

    private async _testProvider(providerId: string) {
        const provider = this.providers.get(providerId);
        if (!provider) return;

        try {
            const isConnected = await this._checkConnection(provider);
            provider.isConnected = isConnected;
            
            if (isConnected) {
                vscode.window.showInformationMessage(`✅ ${provider.name} connection successful`);
            } else {
                vscode.window.showErrorMessage(`❌ ${provider.name} connection failed`);
            }
        } catch (error) {
            provider.isConnected = false;
            vscode.window.showErrorMessage(`❌ ${provider.name} test failed: ${error}`);
        }

        this._updateWebview();
    }

    private async _checkConnection(provider: APIProvider): Promise<boolean> {
        try {
            let endpoint = '';
            let headers: any = {};

            switch (provider.type) {
                case 'ollama':
                    endpoint = `${provider.baseUrl}/api/tags`;
                    break;
                case 'openrouter':
                    endpoint = `${provider.baseUrl}/models`;
                    headers['Authorization'] = `Bearer ${provider.apiKey}`;
                    break;
                case 'openai':
                    endpoint = `${provider.baseUrl}/models`;
                    headers['Authorization'] = `Bearer ${provider.apiKey}`;
                    break;
                case 'anthropic':
                    endpoint = `${provider.baseUrl}/messages`;
                    headers['x-api-key'] = provider.apiKey;
                    headers['anthropic-version'] = '2023-06-01';
                    break;
                default:
                    endpoint = `${provider.baseUrl}/health`;
                    if (provider.apiKey) {
                        headers['Authorization'] = `Bearer ${provider.apiKey}`;
                    }
            }

            const response = await fetch(endpoint, {
                method: 'GET',
                headers: headers,
                signal: AbortSignal.timeout(5000)
            });

            return response.ok;
        } catch (error) {
            this.logger.error(`❌ Connection test failed for ${provider.name}:`, error);
            return false;
        }
    }

    private async _setActiveProvider(providerId: string) {
        const provider = this.providers.get(providerId);
        if (provider) {
            this.activeProvider = provider;
            provider.isActive = true;
            
            // Deactivate other providers
            this.providers.forEach(p => {
                if (p.id !== providerId) {
                    p.isActive = false;
                }
            });

            await this._saveConfigurations();
            this._updateWebview();
            
            vscode.window.showInformationMessage(`🔌 Active provider: ${provider.name}`);
            this.logger.info(`🔌 Active provider set: ${provider.name}`);
        }
    }

    private async _testRequest(providerId: string, model: string, prompt: string) {
        const provider = this.providers.get(providerId);
        if (!provider) return;

        const request: APIRequest = {
            id: this._generateId(),
            providerId: providerId,
            model: model,
            prompt: prompt,
            timestamp: new Date(),
            status: 'pending'
        };

        this.requestHistory.push(request);
        this._updateWebview();

        try {
            const startTime = Date.now();
            const response = await this._sendRequest(provider, model, prompt);
            const duration = Date.now() - startTime;

            request.status = 'completed';
            request.response = response.content;
            request.duration = duration;
            request.tokens = response.tokens;
            request.cost = response.cost;

            // Update provider usage
            provider.usage!.requests++;
            if (response.tokens) provider.usage!.tokens += response.tokens;
            if (response.cost) provider.usage!.cost += response.cost;
            provider.lastUsed = new Date();

        } catch (error) {
            request.status = 'failed';
            request.error = `Request failed: ${error}`;
            this.logger.error('❌ API request failed:', error);
        }

        this._updateWebview();
    }

    private async _sendRequest(provider: APIProvider, model: string, prompt: string): Promise<{content: string, tokens?: number, cost?: number}> {
        // Implementation will vary by provider type
        switch (provider.type) {
            case 'ollama':
                return this._sendOllamaRequest(provider, model, prompt);
            case 'openrouter':
                return this._sendOpenRouterRequest(provider, model, prompt);
            case 'openai':
                return this._sendOpenAIRequest(provider, model, prompt);
            case 'anthropic':
                return this._sendAnthropicRequest(provider, model, prompt);
            default:
                throw new Error(`Unsupported provider type: ${provider.type}`);
        }
    }

    private async _sendOllamaRequest(provider: APIProvider, model: string, prompt: string): Promise<{content: string}> {
        const response = await fetch(`${provider.baseUrl}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: model,
                prompt: prompt,
                stream: false
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        return { content: (data as any).response || 'No response' };
    }

    private async _sendOpenRouterRequest(provider: APIProvider, model: string, prompt: string): Promise<{content: string, tokens?: number, cost?: number}> {
        const response = await fetch(`${provider.baseUrl}/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${provider.apiKey}`,
                'HTTP-Referer': 'https://github.com/krozenking/Orion',
                'X-Title': 'Orion Vision Core'
            },
            body: JSON.stringify({
                model: model,
                messages: [{ role: 'user', content: prompt }],
                max_tokens: 1000
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        return {
            content: (data as any).choices?.[0]?.message?.content || 'No response',
            tokens: (data as any).usage?.total_tokens,
            cost: (data as any).usage?.total_tokens * 0.00001 // Approximate cost
        };
    }

    private async _sendOpenAIRequest(provider: APIProvider, model: string, prompt: string): Promise<{content: string, tokens?: number, cost?: number}> {
        const response = await fetch(`${provider.baseUrl}/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${provider.apiKey}`
            },
            body: JSON.stringify({
                model: model,
                messages: [{ role: 'user', content: prompt }],
                max_tokens: 1000
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        return {
            content: (data as any).choices?.[0]?.message?.content || 'No response',
            tokens: (data as any).usage?.total_tokens,
            cost: this._calculateOpenAICost(model, (data as any).usage?.total_tokens || 0)
        };
    }

    private async _sendAnthropicRequest(provider: APIProvider, model: string, prompt: string): Promise<{content: string, tokens?: number, cost?: number}> {
        const response = await fetch(`${provider.baseUrl}/messages`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': provider.apiKey!,
                'anthropic-version': '2023-06-01'
            },
            body: JSON.stringify({
                model: model,
                max_tokens: 1000,
                messages: [{ role: 'user', content: prompt }]
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        return {
            content: (data as any).content?.[0]?.text || 'No response',
            tokens: (data as any).usage?.input_tokens + (data as any).usage?.output_tokens,
            cost: this._calculateAnthropicCost(model, (data as any).usage?.input_tokens || 0, (data as any).usage?.output_tokens || 0)
        };
    }

    private _calculateOpenAICost(model: string, tokens: number): number {
        const rates: {[key: string]: number} = {
            'gpt-4': 0.00003,
            'gpt-4-turbo': 0.00001,
            'gpt-3.5-turbo': 0.000002
        };
        return (rates[model] || 0.00001) * tokens;
    }

    private _calculateAnthropicCost(model: string, inputTokens: number, outputTokens: number): number {
        const rates: {[key: string]: {input: number, output: number}} = {
            'claude-3-opus-20240229': { input: 0.000015, output: 0.000075 },
            'claude-3-sonnet-20240229': { input: 0.000003, output: 0.000015 },
            'claude-3-haiku-20240307': { input: 0.00000025, output: 0.00000125 }
        };
        const rate = rates[model] || { input: 0.000003, output: 0.000015 };
        return (inputTokens * rate.input) + (outputTokens * rate.output);
    }

    private async _saveConfigurations() {
        const config = {
            providers: Array.from(this.providers.values()),
            activeProviderId: this.activeProvider?.id
        };

        await vscode.workspace.getConfiguration('orion').update(
            'apiProviders',
            config,
            vscode.ConfigurationTarget.Global
        );
    }

    private async _loadSavedConfigurations() {
        const saved = vscode.workspace.getConfiguration('orion').get('apiProviders') as any;
        if (saved?.providers) {
            this.providers.clear();
            saved.providers.forEach((p: APIProvider) => {
                this.providers.set(p.id, p);
            });

            if (saved.activeProviderId) {
                this.activeProvider = this.providers.get(saved.activeProviderId) || null;
            }
        }
    }

    private _updateWebview() {
        if (this._view) {
            this._view.webview.postMessage({
                type: 'updateAPIProviders',
                providers: Array.from(this.providers.values()),
                activeProvider: this.activeProvider,
                requestHistory: this.requestHistory.slice(-50) // Last 50 requests
            });
        }
    }

    private _generateId(): string {
        return Math.random().toString(36).substr(2, 9);
    }

    // Public methods for other providers to use
    public getActiveProvider(): APIProvider | null {
        return this.activeProvider;
    }

    public async sendAIRequest(prompt: string, model?: string): Promise<string> {
        if (!this.activeProvider) {
            throw new Error('No active API provider');
        }

        const selectedModel = model || this.activeProvider.models[0];
        const response = await this._sendRequest(this.activeProvider, selectedModel, prompt);
        return response.content;
    }

    private async _clearHistory() {
        this.requestHistory = [];
        this._updateWebview();
        vscode.window.showInformationMessage('🧹 Request history cleared');
    }

    private async _exportConfig() {
        const config = {
            providers: Array.from(this.providers.values()),
            activeProviderId: this.activeProvider?.id,
            exportedAt: new Date().toISOString(),
            version: '1.0.0'
        };

        const content = JSON.stringify(config, null, 2);
        const fileName = `orion-api-config-${new Date().toISOString().split('T')[0]}.json`;

        const uri = await vscode.window.showSaveDialog({
            defaultUri: vscode.Uri.file(fileName),
            filters: {
                'JSON Files': ['json'],
                'All Files': ['*']
            }
        });

        if (uri) {
            await vscode.workspace.fs.writeFile(uri, Buffer.from(content, 'utf8'));
            vscode.window.showInformationMessage(`💾 API configuration exported to ${uri.fsPath}`);
        }
    }

    private async _importConfig() {
        const uri = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectFolders: false,
            canSelectMany: false,
            filters: {
                'JSON Files': ['json'],
                'All Files': ['*']
            }
        });

        if (uri && uri[0]) {
            try {
                const content = await vscode.workspace.fs.readFile(uri[0]);
                const config = JSON.parse(Buffer.from(content).toString('utf8'));

                if (config.providers && Array.isArray(config.providers)) {
                    this.providers.clear();
                    config.providers.forEach((p: APIProvider) => {
                        this.providers.set(p.id, p);
                    });

                    if (config.activeProviderId) {
                        this.activeProvider = this.providers.get(config.activeProviderId) || null;
                    }

                    await this._saveConfigurations();
                    this._updateWebview();
                    vscode.window.showInformationMessage('📥 API configuration imported successfully');
                } else {
                    throw new Error('Invalid configuration format');
                }
            } catch (error) {
                vscode.window.showErrorMessage(`❌ Failed to import configuration: ${error}`);
            }
        }
    }

    private async _deleteSession(sessionId: string) {
        // Implementation for session management if needed
        this._updateWebview();
    }

    private async _clearSession(sessionId: string) {
        // Implementation for session management if needed
        this._updateWebview();
    }

    private async _exportSession(sessionId: string) {
        // Implementation for session management if needed
        this._updateWebview();
    }

    private _getHtmlForWebview(webview: vscode.Webview): string {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Orion API Manager</title>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    font-size: var(--vscode-font-size);
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                    margin: 0;
                    padding: 10px;
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                }

                .api-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 8px 0;
                    border-bottom: 1px solid var(--vscode-panel-border);
                    margin-bottom: 10px;
                }

                .provider-selector {
                    background: var(--vscode-input-background);
                    color: var(--vscode-input-foreground);
                    border: 1px solid var(--vscode-input-border);
                    padding: 4px;
                    border-radius: 3px;
                }

                .api-actions {
                    display: flex;
                    gap: 5px;
                }

                .btn {
                    background: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    cursor: pointer;
                    font-size: 11px;
                }

                .btn:hover {
                    background: var(--vscode-button-hoverBackground);
                }

                .btn-secondary {
                    background: var(--vscode-button-secondaryBackground);
                    color: var(--vscode-button-secondaryForeground);
                }

                .provider-list {
                    flex: 1;
                    overflow-y: auto;
                    margin-bottom: 10px;
                }

                .provider-item {
                    background: var(--vscode-editor-inactiveSelectionBackground);
                    margin-bottom: 10px;
                    padding: 10px;
                    border-radius: 5px;
                    border-left: 3px solid var(--vscode-terminal-ansiBlue);
                }

                .provider-item.active {
                    border-left-color: var(--vscode-terminal-ansiGreen);
                    background: var(--vscode-list-activeSelectionBackground);
                }

                .provider-item.disconnected {
                    border-left-color: var(--vscode-terminal-ansiRed);
                }

                .provider-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 5px;
                }

                .provider-name {
                    font-weight: bold;
                    font-size: 14px;
                }

                .provider-status {
                    font-size: 11px;
                    padding: 2px 6px;
                    border-radius: 10px;
                }

                .status-connected {
                    background: var(--vscode-terminal-ansiGreen);
                    color: white;
                }

                .status-disconnected {
                    background: var(--vscode-terminal-ansiRed);
                    color: white;
                }

                .provider-details {
                    font-size: 12px;
                    color: var(--vscode-descriptionForeground);
                    margin-bottom: 5px;
                }

                .provider-usage {
                    display: flex;
                    gap: 15px;
                    font-size: 11px;
                    color: var(--vscode-descriptionForeground);
                }

                .test-section {
                    border-top: 1px solid var(--vscode-panel-border);
                    padding-top: 10px;
                }

                .input-group {
                    display: flex;
                    flex-direction: column;
                    gap: 5px;
                    margin-bottom: 10px;
                }

                .input-field {
                    background: var(--vscode-input-background);
                    color: var(--vscode-input-foreground);
                    border: 1px solid var(--vscode-input-border);
                    padding: 4px;
                    border-radius: 3px;
                    font-size: 12px;
                }

                .empty-state {
                    text-align: center;
                    padding: 40px 20px;
                    opacity: 0.7;
                }
            </style>
        </head>
        <body>
            <div class="api-header">
                <h3>🔌 API Provider Manager</h3>
                <div class="api-actions">
                    <button class="btn" onclick="addProvider()">Add</button>
                    <button class="btn btn-secondary" onclick="exportConfig()">Export</button>
                    <button class="btn btn-secondary" onclick="importConfig()">Import</button>
                </div>
            </div>

            <div class="provider-list" id="providerList">
                <div class="empty-state">
                    <h3>🔌 API Provider Manager</h3>
                    <p>Manage multiple AI API connections</p>
                </div>
            </div>

            <div class="test-section">
                <h4>🧪 Test API Request</h4>
                <div class="input-group">
                    <select class="input-field" id="testModel">
                        <option value="">Select model...</option>
                    </select>
                </div>
                <div class="input-group">
                    <input type="text" class="input-field" id="testPrompt" placeholder="Enter test prompt..." />
                </div>
                <button class="btn" onclick="testRequest()">Send Test Request</button>
            </div>

            <script>
                const vscode = acquireVsCodeApi();
                let providers = [];
                let activeProvider = null;

                window.addEventListener('message', event => {
                    const message = event.data;
                    if (message.type === 'updateAPIProviders') {
                        providers = message.providers;
                        activeProvider = message.activeProvider;
                        updateUI();
                    }
                });

                function updateUI() {
                    updateProviderList();
                    updateModelSelector();
                }

                function updateProviderList() {
                    const container = document.getElementById('providerList');

                    if (providers.length === 0) {
                        container.innerHTML = '<div class="empty-state"><h3>🔌 API Provider Manager</h3><p>Manage multiple AI API connections</p></div>';
                        return;
                    }

                    container.innerHTML = '';
                    providers.forEach(provider => {
                        const providerDiv = document.createElement('div');
                        providerDiv.className = \`provider-item \${provider.isActive ? 'active' : ''} \${provider.isConnected ? '' : 'disconnected'}\`;

                        providerDiv.innerHTML = \`
                            <div class="provider-header">
                                <span class="provider-name">\${provider.name}</span>
                                <span class="provider-status \${provider.isConnected ? 'status-connected' : 'status-disconnected'}">
                                    \${provider.isConnected ? 'Connected' : 'Disconnected'}
                                </span>
                            </div>
                            <div class="provider-details">
                                <strong>Type:</strong> \${provider.type} | <strong>URL:</strong> \${provider.baseUrl}
                            </div>
                            <div class="provider-usage">
                                <span>Requests: \${provider.usage?.requests || 0}</span>
                                <span>Tokens: \${provider.usage?.tokens || 0}</span>
                                <span>Cost: $\${(provider.usage?.cost || 0).toFixed(4)}</span>
                            </div>
                            <div style="margin-top: 8px;">
                                <button class="btn" onclick="setActive('\${provider.id}')" \${provider.isActive ? 'disabled' : ''}>
                                    \${provider.isActive ? 'Active' : 'Set Active'}
                                </button>
                                <button class="btn btn-secondary" onclick="testProvider('\${provider.id}')">Test</button>
                                <button class="btn btn-secondary" onclick="editProvider('\${provider.id}')">Edit</button>
                                <button class="btn btn-secondary" onclick="deleteProvider('\${provider.id}')">Delete</button>
                            </div>
                        \`;

                        container.appendChild(providerDiv);
                    });
                }

                function updateModelSelector() {
                    const selector = document.getElementById('testModel');
                    selector.innerHTML = '<option value="">Select model...</option>';

                    if (activeProvider && activeProvider.models) {
                        activeProvider.models.forEach(model => {
                            const option = document.createElement('option');
                            option.value = model;
                            option.textContent = model;
                            selector.appendChild(option);
                        });
                    }
                }

                function addProvider() {
                    const name = prompt('Provider name:');
                    const type = prompt('Provider type (ollama/openrouter/openai/anthropic/custom):');
                    const baseUrl = prompt('Base URL:');
                    const apiKey = prompt('API Key (optional):');

                    if (name && type && baseUrl) {
                        vscode.postMessage({
                            type: 'addProvider',
                            provider: { name, type, baseUrl, apiKey, models: [] }
                        });
                    }
                }

                function setActive(providerId) {
                    vscode.postMessage({
                        type: 'setActiveProvider',
                        providerId: providerId
                    });
                }

                function testProvider(providerId) {
                    vscode.postMessage({
                        type: 'testProvider',
                        providerId: providerId
                    });
                }

                function editProvider(providerId) {
                    // Implementation for editing provider
                    alert('Edit functionality coming soon!');
                }

                function deleteProvider(providerId) {
                    if (confirm('Are you sure you want to delete this provider?')) {
                        vscode.postMessage({
                            type: 'deleteProvider',
                            providerId: providerId
                        });
                    }
                }

                function testRequest() {
                    const model = document.getElementById('testModel').value;
                    const prompt = document.getElementById('testPrompt').value;

                    if (!activeProvider) {
                        alert('Please select an active provider first');
                        return;
                    }

                    if (!model || !prompt) {
                        alert('Please select a model and enter a prompt');
                        return;
                    }

                    vscode.postMessage({
                        type: 'testRequest',
                        providerId: activeProvider.id,
                        model: model,
                        prompt: prompt
                    });
                }

                function exportConfig() {
                    vscode.postMessage({ type: 'exportConfig' });
                }

                function importConfig() {
                    vscode.postMessage({ type: 'importConfig' });
                }
            </script>
        </body>
        </html>`;
    }
}
