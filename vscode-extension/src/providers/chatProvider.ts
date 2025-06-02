/**
 * 💬 Orion Chat Provider
 * Implements a comprehensive chat interface for AI conversations
 */

import * as vscode from 'vscode';
import { OrionConfiguration } from '../config/configuration';
import { OrionLogger } from '../utils/logger';
import fetch from 'node-fetch';

export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
    metadata?: {
        model?: string;
        tokens?: number;
        cost?: number;
    };
}

export interface ChatSession {
    id: string;
    title: string;
    messages: ChatMessage[];
    createdAt: Date;
    updatedAt: Date;
    model: string;
    systemPrompt?: string;
}

export class OrionChatProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'orionChat';
    
    private _view?: vscode.WebviewView;
    private config: OrionConfiguration;
    private logger: OrionLogger;
    private currentSession: ChatSession | null = null;
    private sessions: Map<string, ChatSession> = new Map();

    constructor(private readonly _extensionUri: vscode.Uri) {
        this.config = new OrionConfiguration();
        this.logger = new OrionLogger();
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

        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(
            message => this._handleWebviewMessage(message),
            undefined,
            []
        );

        this.logger.info('🗨️ Chat provider initialized');
    }

    private async _handleWebviewMessage(message: any) {
        switch (message.type) {
            case 'sendMessage':
                await this._handleSendMessage(message.content, message.model);
                break;
            case 'newSession':
                await this._createNewSession(message.title, message.model);
                break;
            case 'loadSession':
                await this._loadSession(message.sessionId);
                break;
            case 'deleteSession':
                await this._deleteSession(message.sessionId);
                break;
            case 'exportSession':
                await this._exportSession(message.sessionId);
                break;
            case 'clearHistory':
                await this._clearHistory();
                break;
        }
    }

    private async _handleSendMessage(content: string, model: string) {
        if (!this.currentSession) {
            await this._createNewSession('New Chat', model);
        }

        const userMessage: ChatMessage = {
            id: this._generateId(),
            role: 'user',
            content: content,
            timestamp: new Date()
        };

        this.currentSession!.messages.push(userMessage);
        this._updateWebview();

        try {
            // Send to AI provider
            const response = await this._sendToAI(content, model);
            
            const assistantMessage: ChatMessage = {
                id: this._generateId(),
                role: 'assistant',
                content: response.content,
                timestamp: new Date(),
                metadata: {
                    model: model,
                    tokens: response.tokens,
                    cost: response.cost
                }
            };

            this.currentSession!.messages.push(assistantMessage);
            this.currentSession!.updatedAt = new Date();
            this._updateWebview();

        } catch (error) {
            this.logger.error('❌ Chat message failed:', error);
            vscode.window.showErrorMessage(`Chat failed: ${error}`);
        }
    }

    private async _sendToAI(content: string, model: string): Promise<{content: string, tokens?: number, cost?: number}> {
        const baseUrl = `http://${this.config.getServerHost()}:${this.config.getServerPort()}`;
        
        try {
            const response = await fetch(`${baseUrl}/api/ai/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: content,
                    model: model,
                    conversation: this.currentSession?.messages || []
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return {
                content: (data as any).response || (data as any).result || 'No response received',
                tokens: (data as any).tokens,
                cost: (data as any).cost
            };
        } catch (error) {
            this.logger.error('❌ AI API call failed:', error);
            throw error;
        }
    }

    private async _createNewSession(title: string, model: string) {
        const session: ChatSession = {
            id: this._generateId(),
            title: title,
            messages: [],
            createdAt: new Date(),
            updatedAt: new Date(),
            model: model
        };

        this.sessions.set(session.id, session);
        this.currentSession = session;
        this._updateWebview();
        
        this.logger.info(`💬 New chat session created: ${session.id}`);
    }

    private async _loadSession(sessionId: string) {
        const session = this.sessions.get(sessionId);
        if (session) {
            this.currentSession = session;
            this._updateWebview();
            this.logger.info(`💬 Chat session loaded: ${sessionId}`);
        }
    }

    private async _deleteSession(sessionId: string) {
        this.sessions.delete(sessionId);
        if (this.currentSession?.id === sessionId) {
            this.currentSession = null;
        }
        this._updateWebview();
        this.logger.info(`🗑️ Chat session deleted: ${sessionId}`);
    }

    private async _exportSession(sessionId: string) {
        const session = this.sessions.get(sessionId);
        if (!session) return;

        const exportData = {
            session: session,
            exportedAt: new Date().toISOString(),
            version: '1.0.0'
        };

        const content = JSON.stringify(exportData, null, 2);
        const fileName = `orion-chat-${session.title.replace(/[^a-zA-Z0-9]/g, '-')}-${new Date().toISOString().split('T')[0]}.json`;

        const uri = await vscode.window.showSaveDialog({
            defaultUri: vscode.Uri.file(fileName),
            filters: {
                'JSON Files': ['json'],
                'All Files': ['*']
            }
        });

        if (uri) {
            await vscode.workspace.fs.writeFile(uri, Buffer.from(content, 'utf8'));
            vscode.window.showInformationMessage(`💾 Chat exported to ${uri.fsPath}`);
        }
    }

    private async _clearHistory() {
        this.sessions.clear();
        this.currentSession = null;
        this._updateWebview();
        vscode.window.showInformationMessage('🧹 Chat history cleared');
    }

    private _updateWebview() {
        if (this._view) {
            this._view.webview.postMessage({
                type: 'updateChat',
                currentSession: this.currentSession,
                sessions: Array.from(this.sessions.values())
            });
        }
    }

    private _generateId(): string {
        return Math.random().toString(36).substr(2, 9);
    }

    private _getHtmlForWebview(webview: vscode.Webview): string {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Orion Chat</title>
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
                
                .chat-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 10px 0;
                    border-bottom: 1px solid var(--vscode-panel-border);
                    margin-bottom: 10px;
                }
                
                .session-selector {
                    flex: 1;
                    margin-right: 10px;
                }
                
                .chat-actions {
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
                    font-size: 12px;
                }
                
                .btn:hover {
                    background: var(--vscode-button-hoverBackground);
                }
                
                .btn-secondary {
                    background: var(--vscode-button-secondaryBackground);
                    color: var(--vscode-button-secondaryForeground);
                }
                
                .chat-messages {
                    flex: 1;
                    overflow-y: auto;
                    padding: 10px 0;
                    margin-bottom: 10px;
                }
                
                .message {
                    margin-bottom: 15px;
                    padding: 10px;
                    border-radius: 8px;
                    max-width: 90%;
                }
                
                .message.user {
                    background: var(--vscode-inputValidation-infoBorder);
                    margin-left: auto;
                    text-align: right;
                }
                
                .message.assistant {
                    background: var(--vscode-editor-inactiveSelectionBackground);
                }
                
                .message-header {
                    font-size: 11px;
                    opacity: 0.7;
                    margin-bottom: 5px;
                }
                
                .message-content {
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }
                
                .chat-input {
                    display: flex;
                    gap: 10px;
                    padding-top: 10px;
                    border-top: 1px solid var(--vscode-panel-border);
                }
                
                .input-container {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    gap: 5px;
                }
                
                .model-selector {
                    width: 100%;
                    background: var(--vscode-input-background);
                    color: var(--vscode-input-foreground);
                    border: 1px solid var(--vscode-input-border);
                    padding: 4px;
                    border-radius: 3px;
                }
                
                .message-input {
                    width: 100%;
                    min-height: 60px;
                    background: var(--vscode-input-background);
                    color: var(--vscode-input-foreground);
                    border: 1px solid var(--vscode-input-border);
                    padding: 8px;
                    border-radius: 3px;
                    resize: vertical;
                    font-family: inherit;
                }
                
                .send-btn {
                    align-self: flex-end;
                    height: 32px;
                    padding: 0 15px;
                }
                
                .empty-state {
                    text-align: center;
                    padding: 40px 20px;
                    opacity: 0.7;
                }
                
                .loading {
                    opacity: 0.5;
                    pointer-events: none;
                }
            </style>
        </head>
        <body>
            <div class="chat-header">
                <select class="session-selector" id="sessionSelector">
                    <option value="">Select a chat session...</option>
                </select>
                <div class="chat-actions">
                    <button class="btn" onclick="newSession()">New</button>
                    <button class="btn btn-secondary" onclick="exportSession()">Export</button>
                    <button class="btn btn-secondary" onclick="clearHistory()">Clear</button>
                </div>
            </div>
            
            <div class="chat-messages" id="chatMessages">
                <div class="empty-state">
                    <h3>💬 Welcome to Orion Chat</h3>
                    <p>Start a conversation with your AI assistant</p>
                </div>
            </div>
            
            <div class="chat-input">
                <div class="input-container">
                    <select class="model-selector" id="modelSelector">
                        <option value="ollama">Ollama (Local)</option>
                        <option value="openrouter">OpenRouter</option>
                        <option value="openai">OpenAI</option>
                        <option value="anthropic">Anthropic</option>
                    </select>
                    <textarea class="message-input" id="messageInput" placeholder="Type your message here..." rows="3"></textarea>
                </div>
                <button class="btn send-btn" onclick="sendMessage()">Send</button>
            </div>
            
            <script>
                const vscode = acquireVsCodeApi();
                let currentSession = null;
                let sessions = [];
                
                // Handle messages from extension
                window.addEventListener('message', event => {
                    const message = event.data;
                    if (message.type === 'updateChat') {
                        currentSession = message.currentSession;
                        sessions = message.sessions;
                        updateUI();
                    }
                });
                
                function updateUI() {
                    updateSessionSelector();
                    updateMessages();
                }
                
                function updateSessionSelector() {
                    const selector = document.getElementById('sessionSelector');
                    selector.innerHTML = '<option value="">Select a chat session...</option>';
                    
                    sessions.forEach(session => {
                        const option = document.createElement('option');
                        option.value = session.id;
                        option.textContent = session.title;
                        if (currentSession && session.id === currentSession.id) {
                            option.selected = true;
                        }
                        selector.appendChild(option);
                    });
                }
                
                function updateMessages() {
                    const container = document.getElementById('chatMessages');
                    
                    if (!currentSession || currentSession.messages.length === 0) {
                        container.innerHTML = '<div class="empty-state"><h3>💬 Welcome to Orion Chat</h3><p>Start a conversation with your AI assistant</p></div>';
                        return;
                    }
                    
                    container.innerHTML = '';
                    currentSession.messages.forEach(message => {
                        const messageDiv = document.createElement('div');
                        messageDiv.className = \`message \${message.role}\`;
                        
                        const timestamp = new Date(message.timestamp).toLocaleTimeString();
                        const model = message.metadata?.model || '';
                        
                        messageDiv.innerHTML = \`
                            <div class="message-header">\${message.role} • \${timestamp} \${model ? '• ' + model : ''}</div>
                            <div class="message-content">\${message.content}</div>
                        \`;
                        
                        container.appendChild(messageDiv);
                    });
                    
                    container.scrollTop = container.scrollHeight;
                }
                
                function sendMessage() {
                    const input = document.getElementById('messageInput');
                    const modelSelector = document.getElementById('modelSelector');
                    const content = input.value.trim();
                    
                    if (!content) return;
                    
                    vscode.postMessage({
                        type: 'sendMessage',
                        content: content,
                        model: modelSelector.value
                    });
                    
                    input.value = '';
                    document.body.classList.add('loading');
                    setTimeout(() => document.body.classList.remove('loading'), 1000);
                }
                
                function newSession() {
                    const title = prompt('Enter session title:', 'New Chat');
                    if (title) {
                        const modelSelector = document.getElementById('modelSelector');
                        vscode.postMessage({
                            type: 'newSession',
                            title: title,
                            model: modelSelector.value
                        });
                    }
                }
                
                function exportSession() {
                    if (currentSession) {
                        vscode.postMessage({
                            type: 'exportSession',
                            sessionId: currentSession.id
                        });
                    }
                }
                
                function clearHistory() {
                    if (confirm('Are you sure you want to clear all chat history?')) {
                        vscode.postMessage({
                            type: 'clearHistory'
                        });
                    }
                }
                
                // Handle session selection
                document.getElementById('sessionSelector').addEventListener('change', (e) => {
                    if (e.target.value) {
                        vscode.postMessage({
                            type: 'loadSession',
                            sessionId: e.target.value
                        });
                    }
                });
                
                // Handle Enter key in textarea
                document.getElementById('messageInput').addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendMessage();
                    }
                });
            </script>
        </body>
        </html>`;
    }
}
