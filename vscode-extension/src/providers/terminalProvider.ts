/**
 * 🖥️ Orion Terminal Provider
 * Provides secure terminal access and command execution capabilities
 */

import * as vscode from 'vscode';
import { OrionConfiguration } from '../config/configuration';
import { OrionLogger } from '../utils/logger';
import fetch from 'node-fetch';

export interface TerminalCommand {
    id: string;
    command: string;
    workingDirectory?: string;
    timestamp: Date;
    status: 'pending' | 'running' | 'completed' | 'failed';
    output?: string;
    error?: string;
    exitCode?: number;
}

export interface TerminalSession {
    id: string;
    name: string;
    workingDirectory: string;
    commands: TerminalCommand[];
    createdAt: Date;
    isActive: boolean;
}

export class OrionTerminalProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'orionTerminal';
    
    private _view?: vscode.WebviewView;
    private config: OrionConfiguration;
    private logger: OrionLogger;
    private sessions: Map<string, TerminalSession> = new Map();
    private activeSession: TerminalSession | null = null;
    private terminals: Map<string, vscode.Terminal> = new Map();

    constructor(private readonly _extensionUri: vscode.Uri) {
        this.config = new OrionConfiguration();
        this.logger = new OrionLogger();
        this._createDefaultSession();
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

        this.logger.info('🖥️ Terminal provider initialized');
    }

    private async _handleWebviewMessage(message: any) {
        switch (message.type) {
            case 'executeCommand':
                await this._executeCommand(message.command, message.workingDirectory);
                break;
            case 'createSession':
                await this._createSession(message.name, message.workingDirectory);
                break;
            case 'switchSession':
                await this._switchSession(message.sessionId);
                break;
            case 'deleteSession':
                await this._deleteSession(message.sessionId);
                break;
            case 'openInVSCodeTerminal':
                await this._openInVSCodeTerminal(message.command);
                break;
            case 'clearSession':
                await this._clearSession(message.sessionId);
                break;
            case 'exportSession':
                await this._exportSession(message.sessionId);
                break;
        }
    }

    private async _executeCommand(command: string, workingDirectory?: string) {
        if (!this.activeSession) {
            await this._createDefaultSession();
        }

        const cmd: TerminalCommand = {
            id: this._generateId(),
            command: command,
            workingDirectory: workingDirectory || this.activeSession!.workingDirectory,
            timestamp: new Date(),
            status: 'pending'
        };

        this.activeSession!.commands.push(cmd);
        this._updateWebview();

        try {
            // Execute command via Orion server
            const result = await this._sendCommandToServer(command, cmd.workingDirectory || process.cwd());
            
            cmd.status = result.exitCode === 0 ? 'completed' : 'failed';
            cmd.output = result.output;
            cmd.error = result.error;
            cmd.exitCode = result.exitCode;

        } catch (error) {
            cmd.status = 'failed';
            cmd.error = `Execution failed: ${error}`;
            this.logger.error('❌ Command execution failed:', error);
        }

        this._updateWebview();
    }

    private async _sendCommandToServer(command: string, workingDirectory: string): Promise<{output: string, error?: string, exitCode: number}> {
        const baseUrl = `http://${this.config.getServerHost()}:${this.config.getServerPort()}`;
        
        try {
            const response = await fetch(`${baseUrl}/api/terminal/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    command: command,
                    workingDirectory: workingDirectory,
                    timeout: 30000 // 30 second timeout
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return {
                output: (data as any).output || '',
                error: (data as any).error,
                exitCode: (data as any).exitCode || 0
            };
        } catch (error) {
            this.logger.error('❌ Terminal API call failed:', error);
            throw error;
        }
    }

    private async _createSession(name: string, workingDirectory: string) {
        const session: TerminalSession = {
            id: this._generateId(),
            name: name,
            workingDirectory: workingDirectory,
            commands: [],
            createdAt: new Date(),
            isActive: false
        };

        this.sessions.set(session.id, session);
        await this._switchSession(session.id);
        
        this.logger.info(`🖥️ Terminal session created: ${session.name}`);
    }

    private async _switchSession(sessionId: string) {
        const session = this.sessions.get(sessionId);
        if (session) {
            // Deactivate current session
            if (this.activeSession) {
                this.activeSession.isActive = false;
            }
            
            // Activate new session
            session.isActive = true;
            this.activeSession = session;
            this._updateWebview();
            
            this.logger.info(`🖥️ Switched to terminal session: ${session.name}`);
        }
    }

    private async _deleteSession(sessionId: string) {
        const session = this.sessions.get(sessionId);
        if (!session) return;

        // Close associated VS Code terminal if exists
        const terminal = this.terminals.get(sessionId);
        if (terminal) {
            terminal.dispose();
            this.terminals.delete(sessionId);
        }

        this.sessions.delete(sessionId);
        
        // If this was the active session, switch to another or create default
        if (this.activeSession?.id === sessionId) {
            const remainingSessions = Array.from(this.sessions.values());
            if (remainingSessions.length > 0) {
                await this._switchSession(remainingSessions[0].id);
            } else {
                await this._createDefaultSession();
            }
        }

        this._updateWebview();
        this.logger.info(`🗑️ Terminal session deleted: ${session.name}`);
    }

    private async _openInVSCodeTerminal(command?: string) {
        if (!this.activeSession) return;

        let terminal = this.terminals.get(this.activeSession.id);
        
        if (!terminal) {
            terminal = vscode.window.createTerminal({
                name: `Orion: ${this.activeSession.name}`,
                cwd: this.activeSession.workingDirectory
            });
            this.terminals.set(this.activeSession.id, terminal);
        }

        terminal.show();
        
        if (command) {
            terminal.sendText(command);
        }

        this.logger.info(`🖥️ Opened VS Code terminal for session: ${this.activeSession.name}`);
    }

    private async _clearSession(sessionId: string) {
        const session = this.sessions.get(sessionId);
        if (session) {
            session.commands = [];
            this._updateWebview();
            this.logger.info(`🧹 Terminal session cleared: ${session.name}`);
        }
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
        const fileName = `orion-terminal-${session.name.replace(/[^a-zA-Z0-9]/g, '-')}-${new Date().toISOString().split('T')[0]}.json`;

        const uri = await vscode.window.showSaveDialog({
            defaultUri: vscode.Uri.file(fileName),
            filters: {
                'JSON Files': ['json'],
                'All Files': ['*']
            }
        });

        if (uri) {
            await vscode.workspace.fs.writeFile(uri, Buffer.from(content, 'utf8'));
            vscode.window.showInformationMessage(`💾 Terminal session exported to ${uri.fsPath}`);
        }
    }

    private async _createDefaultSession() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        const defaultPath = workspaceFolder?.uri.fsPath || process.cwd();
        
        await this._createSession('Default', defaultPath);
    }

    private _updateWebview() {
        if (this._view) {
            this._view.webview.postMessage({
                type: 'updateTerminal',
                activeSession: this.activeSession,
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
            <title>Orion Terminal</title>
            <style>
                body {
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    font-size: 13px;
                    color: var(--vscode-terminal-foreground);
                    background-color: var(--vscode-terminal-background);
                    margin: 0;
                    padding: 10px;
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                }
                
                .terminal-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 8px 0;
                    border-bottom: 1px solid var(--vscode-panel-border);
                    margin-bottom: 10px;
                }
                
                .session-info {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .session-selector {
                    background: var(--vscode-input-background);
                    color: var(--vscode-input-foreground);
                    border: 1px solid var(--vscode-input-border);
                    padding: 4px;
                    border-radius: 3px;
                }
                
                .terminal-actions {
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
                
                .terminal-output {
                    flex: 1;
                    overflow-y: auto;
                    padding: 10px;
                    background: var(--vscode-terminal-background);
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 3px;
                    margin-bottom: 10px;
                }
                
                .command-entry {
                    margin-bottom: 15px;
                    border-left: 3px solid var(--vscode-terminal-ansiBlue);
                    padding-left: 10px;
                }
                
                .command-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 5px;
                    font-size: 11px;
                    opacity: 0.8;
                }
                
                .command-text {
                    color: var(--vscode-terminal-ansiGreen);
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                
                .command-output {
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    background: rgba(0,0,0,0.2);
                    padding: 8px;
                    border-radius: 3px;
                    margin: 5px 0;
                }
                
                .command-error {
                    color: var(--vscode-terminal-ansiRed);
                    background: rgba(255,0,0,0.1);
                }
                
                .status-pending { border-left-color: var(--vscode-terminal-ansiYellow); }
                .status-running { border-left-color: var(--vscode-terminal-ansiBlue); }
                .status-completed { border-left-color: var(--vscode-terminal-ansiGreen); }
                .status-failed { border-left-color: var(--vscode-terminal-ansiRed); }
                
                .terminal-input {
                    display: flex;
                    gap: 10px;
                    padding-top: 10px;
                    border-top: 1px solid var(--vscode-panel-border);
                }
                
                .command-input {
                    flex: 1;
                    background: var(--vscode-input-background);
                    color: var(--vscode-input-foreground);
                    border: 1px solid var(--vscode-input-border);
                    padding: 8px;
                    border-radius: 3px;
                    font-family: inherit;
                }
                
                .execute-btn {
                    padding: 8px 15px;
                }
                
                .empty-state {
                    text-align: center;
                    padding: 40px 20px;
                    opacity: 0.7;
                }
                
                .working-directory {
                    font-size: 11px;
                    opacity: 0.6;
                    margin-left: 10px;
                }
            </style>
        </head>
        <body>
            <div class="terminal-header">
                <div class="session-info">
                    <select class="session-selector" id="sessionSelector">
                        <option value="">Select terminal session...</option>
                    </select>
                    <span class="working-directory" id="workingDirectory"></span>
                </div>
                <div class="terminal-actions">
                    <button class="btn" onclick="newSession()">New</button>
                    <button class="btn btn-secondary" onclick="openInVSCode()">VS Code</button>
                    <button class="btn btn-secondary" onclick="clearSession()">Clear</button>
                    <button class="btn btn-secondary" onclick="exportSession()">Export</button>
                </div>
            </div>
            
            <div class="terminal-output" id="terminalOutput">
                <div class="empty-state">
                    <h3>🖥️ Orion Terminal</h3>
                    <p>Execute commands securely through the Orion server</p>
                </div>
            </div>
            
            <div class="terminal-input">
                <input type="text" class="command-input" id="commandInput" placeholder="Enter command..." />
                <button class="btn execute-btn" onclick="executeCommand()">Execute</button>
            </div>
            
            <script>
                const vscode = acquireVsCodeApi();
                let activeSession = null;
                let sessions = [];
                
                window.addEventListener('message', event => {
                    const message = event.data;
                    if (message.type === 'updateTerminal') {
                        activeSession = message.activeSession;
                        sessions = message.sessions;
                        updateUI();
                    }
                });
                
                function updateUI() {
                    updateSessionSelector();
                    updateOutput();
                    updateWorkingDirectory();
                }
                
                function updateSessionSelector() {
                    const selector = document.getElementById('sessionSelector');
                    selector.innerHTML = '<option value="">Select terminal session...</option>';
                    
                    sessions.forEach(session => {
                        const option = document.createElement('option');
                        option.value = session.id;
                        option.textContent = session.name;
                        if (activeSession && session.id === activeSession.id) {
                            option.selected = true;
                        }
                        selector.appendChild(option);
                    });
                }
                
                function updateWorkingDirectory() {
                    const element = document.getElementById('workingDirectory');
                    element.textContent = activeSession ? activeSession.workingDirectory : '';
                }
                
                function updateOutput() {
                    const container = document.getElementById('terminalOutput');
                    
                    if (!activeSession || activeSession.commands.length === 0) {
                        container.innerHTML = '<div class="empty-state"><h3>🖥️ Orion Terminal</h3><p>Execute commands securely through the Orion server</p></div>';
                        return;
                    }
                    
                    container.innerHTML = '';
                    activeSession.commands.forEach(cmd => {
                        const cmdDiv = document.createElement('div');
                        cmdDiv.className = \`command-entry status-\${cmd.status}\`;
                        
                        const timestamp = new Date(cmd.timestamp).toLocaleTimeString();
                        
                        let outputHtml = '';
                        if (cmd.output) {
                            outputHtml += \`<div class="command-output">\${cmd.output}</div>\`;
                        }
                        if (cmd.error) {
                            outputHtml += \`<div class="command-output command-error">\${cmd.error}</div>\`;
                        }
                        
                        cmdDiv.innerHTML = \`
                            <div class="command-header">
                                <span>\${timestamp}</span>
                                <span>Status: \${cmd.status}</span>
                                <span>Exit: \${cmd.exitCode !== undefined ? cmd.exitCode : 'N/A'}</span>
                            </div>
                            <div class="command-text">$ \${cmd.command}</div>
                            \${outputHtml}
                        \`;
                        
                        container.appendChild(cmdDiv);
                    });
                    
                    container.scrollTop = container.scrollHeight;
                }
                
                function executeCommand() {
                    const input = document.getElementById('commandInput');
                    const command = input.value.trim();
                    
                    if (!command) return;
                    
                    vscode.postMessage({
                        type: 'executeCommand',
                        command: command,
                        workingDirectory: activeSession?.workingDirectory
                    });
                    
                    input.value = '';
                }
                
                function newSession() {
                    const name = prompt('Enter session name:', 'Terminal Session');
                    const workingDirectory = prompt('Enter working directory:', activeSession?.workingDirectory || '');
                    
                    if (name && workingDirectory) {
                        vscode.postMessage({
                            type: 'createSession',
                            name: name,
                            workingDirectory: workingDirectory
                        });
                    }
                }
                
                function openInVSCode() {
                    const command = document.getElementById('commandInput').value.trim();
                    vscode.postMessage({
                        type: 'openInVSCodeTerminal',
                        command: command || undefined
                    });
                }
                
                function clearSession() {
                    if (activeSession && confirm('Clear all commands in this session?')) {
                        vscode.postMessage({
                            type: 'clearSession',
                            sessionId: activeSession.id
                        });
                    }
                }
                
                function exportSession() {
                    if (activeSession) {
                        vscode.postMessage({
                            type: 'exportSession',
                            sessionId: activeSession.id
                        });
                    }
                }
                
                // Handle session selection
                document.getElementById('sessionSelector').addEventListener('change', (e) => {
                    if (e.target.value) {
                        vscode.postMessage({
                            type: 'switchSession',
                            sessionId: e.target.value
                        });
                    }
                });
                
                // Handle Enter key
                document.getElementById('commandInput').addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        executeCommand();
                    }
                });
            </script>
        </body>
        </html>`;
    }
}
