/**
 * 📁 Orion File System Provider
 * Provides secure file system access and operations
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { OrionConfiguration } from '../config/configuration';
import { OrionLogger } from '../utils/logger';

export interface FileOperation {
    id: string;
    type: 'read' | 'write' | 'create' | 'delete' | 'copy' | 'move' | 'mkdir' | 'list';
    path: string;
    content?: string;
    destination?: string;
    timestamp: Date;
    status: 'pending' | 'completed' | 'failed';
    error?: string;
    size?: number;
}

export interface FileSystemSession {
    id: string;
    name: string;
    workingDirectory: string;
    operations: FileOperation[];
    createdAt: Date;
    permissions: {
        read: boolean;
        write: boolean;
        execute: boolean;
        delete: boolean;
    };
}

export class OrionFileSystemProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'orionFileSystem';
    
    private _view?: vscode.WebviewView;
    private config: OrionConfiguration;
    private logger: OrionLogger;
    private sessions: Map<string, FileSystemSession> = new Map();
    private activeSession: FileSystemSession | null = null;

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

        this.logger.info('📁 File System provider initialized');
    }

    private async _handleWebviewMessage(message: any) {
        switch (message.type) {
            case 'readFile':
                await this._readFile(message.path);
                break;
            case 'writeFile':
                await this._writeFile(message.path, message.content);
                break;
            case 'createFile':
                await this._createFile(message.path, message.content);
                break;
            case 'deleteFile':
                await this._deleteFile(message.path);
                break;
            case 'copyFile':
                await this._copyFile(message.source, message.destination);
                break;
            case 'moveFile':
                await this._moveFile(message.source, message.destination);
                break;
            case 'createDirectory':
                await this._createDirectory(message.path);
                break;
            case 'listDirectory':
                await this._listDirectory(message.path);
                break;
            case 'createSession':
                await this._createSession(message.name, message.workingDirectory, message.permissions);
                break;
            case 'switchSession':
                await this._switchSession(message.sessionId);
                break;
            case 'deleteSession':
                await this._deleteSession(message.sessionId);
                break;
            case 'exportSession':
                await this._exportSession(message.sessionId);
                break;
            case 'clearSession':
                await this._clearSession(message.sessionId);
                break;
        }
    }

    private async _readFile(filePath: string) {
        if (!this._checkPermission('read')) return;

        const operation: FileOperation = {
            id: this._generateId(),
            type: 'read',
            path: filePath,
            timestamp: new Date(),
            status: 'pending'
        };

        this.activeSession!.operations.push(operation);
        this._updateWebview();

        try {
            const fullPath = this._resolvePath(filePath);
            const uri = vscode.Uri.file(fullPath);
            
            // Check if file exists
            try {
                await vscode.workspace.fs.stat(uri);
            } catch {
                throw new Error(`File not found: ${filePath}`);
            }

            const content = await vscode.workspace.fs.readFile(uri);
            const textContent = Buffer.from(content).toString('utf8');
            
            operation.status = 'completed';
            operation.content = textContent;
            operation.size = content.length;

            // Send content back to webview
            this._view?.webview.postMessage({
                type: 'fileContent',
                operationId: operation.id,
                path: filePath,
                content: textContent,
                size: content.length
            });

        } catch (error) {
            operation.status = 'failed';
            operation.error = `Read failed: ${error}`;
            this.logger.error('❌ File read failed:', error);
        }

        this._updateWebview();
    }

    private async _writeFile(filePath: string, content: string) {
        if (!this._checkPermission('write')) return;

        const operation: FileOperation = {
            id: this._generateId(),
            type: 'write',
            path: filePath,
            content: content,
            timestamp: new Date(),
            status: 'pending'
        };

        this.activeSession!.operations.push(operation);
        this._updateWebview();

        try {
            const fullPath = this._resolvePath(filePath);
            const uri = vscode.Uri.file(fullPath);
            const buffer = Buffer.from(content, 'utf8');
            
            await vscode.workspace.fs.writeFile(uri, buffer);
            
            operation.status = 'completed';
            operation.size = buffer.length;

        } catch (error) {
            operation.status = 'failed';
            operation.error = `Write failed: ${error}`;
            this.logger.error('❌ File write failed:', error);
        }

        this._updateWebview();
    }

    private async _createFile(filePath: string, content: string = '') {
        if (!this._checkPermission('write')) return;

        const operation: FileOperation = {
            id: this._generateId(),
            type: 'create',
            path: filePath,
            content: content,
            timestamp: new Date(),
            status: 'pending'
        };

        this.activeSession!.operations.push(operation);
        this._updateWebview();

        try {
            const fullPath = this._resolvePath(filePath);
            const uri = vscode.Uri.file(fullPath);
            
            // Check if file already exists
            try {
                await vscode.workspace.fs.stat(uri);
                throw new Error(`File already exists: ${filePath}`);
            } catch (statError) {
                // File doesn't exist, which is what we want
            }

            const buffer = Buffer.from(content, 'utf8');
            await vscode.workspace.fs.writeFile(uri, buffer);
            
            operation.status = 'completed';
            operation.size = buffer.length;

        } catch (error) {
            operation.status = 'failed';
            operation.error = `Create failed: ${error}`;
            this.logger.error('❌ File create failed:', error);
        }

        this._updateWebview();
    }

    private async _deleteFile(filePath: string) {
        if (!this._checkPermission('delete')) return;

        const operation: FileOperation = {
            id: this._generateId(),
            type: 'delete',
            path: filePath,
            timestamp: new Date(),
            status: 'pending'
        };

        this.activeSession!.operations.push(operation);
        this._updateWebview();

        try {
            const fullPath = this._resolvePath(filePath);
            const uri = vscode.Uri.file(fullPath);
            
            await vscode.workspace.fs.delete(uri);
            
            operation.status = 'completed';

        } catch (error) {
            operation.status = 'failed';
            operation.error = `Delete failed: ${error}`;
            this.logger.error('❌ File delete failed:', error);
        }

        this._updateWebview();
    }

    private async _createDirectory(dirPath: string) {
        if (!this._checkPermission('write')) return;

        const operation: FileOperation = {
            id: this._generateId(),
            type: 'mkdir',
            path: dirPath,
            timestamp: new Date(),
            status: 'pending'
        };

        this.activeSession!.operations.push(operation);
        this._updateWebview();

        try {
            const fullPath = this._resolvePath(dirPath);
            const uri = vscode.Uri.file(fullPath);
            
            await vscode.workspace.fs.createDirectory(uri);
            
            operation.status = 'completed';

        } catch (error) {
            operation.status = 'failed';
            operation.error = `Directory creation failed: ${error}`;
            this.logger.error('❌ Directory creation failed:', error);
        }

        this._updateWebview();
    }

    private _resolvePath(filePath: string): string {
        if (path.isAbsolute(filePath)) {
            return filePath;
        }
        return path.join(this.activeSession!.workingDirectory, filePath);
    }

    private _checkPermission(operation: 'read' | 'write' | 'execute' | 'delete'): boolean {
        if (!this.activeSession) {
            vscode.window.showErrorMessage('No active file system session');
            return false;
        }

        if (!this.activeSession.permissions[operation]) {
            vscode.window.showErrorMessage(`Permission denied: ${operation} operation not allowed`);
            return false;
        }

        return true;
    }

    private async _createDefaultSession() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        const defaultPath = workspaceFolder?.uri.fsPath || process.cwd();
        
        await this._createSession('Default', defaultPath, {
            read: true,
            write: true,
            execute: false,
            delete: false
        });
    }

    private async _createSession(name: string, workingDirectory: string, permissions: any) {
        const session: FileSystemSession = {
            id: this._generateId(),
            name: name,
            workingDirectory: workingDirectory,
            operations: [],
            createdAt: new Date(),
            permissions: permissions
        };

        this.sessions.set(session.id, session);
        await this._switchSession(session.id);
        
        this.logger.info(`📁 File system session created: ${session.name}`);
    }

    private async _switchSession(sessionId: string) {
        const session = this.sessions.get(sessionId);
        if (session) {
            this.activeSession = session;
            this._updateWebview();
            this.logger.info(`📁 Switched to file system session: ${session.name}`);
        }
    }

    private _updateWebview() {
        if (this._view) {
            this._view.webview.postMessage({
                type: 'updateFileSystem',
                activeSession: this.activeSession,
                sessions: Array.from(this.sessions.values())
            });
        }
    }

    private _generateId(): string {
        return Math.random().toString(36).substr(2, 9);
    }

    // Eksik metodları ekleyelim
    private async _copyFile(source: string, destination: string) {
        if (!this._checkPermission('read') || !this._checkPermission('write')) return;

        const operation: FileOperation = {
            id: this._generateId(),
            type: 'copy',
            path: `${source} -> ${destination}`,
            timestamp: new Date(),
            status: 'pending'
        };

        this.activeSession!.operations.push(operation);
        this._updateWebview();

        try {
            const sourceUri = vscode.Uri.file(this._resolvePath(source));
            const destUri = vscode.Uri.file(this._resolvePath(destination));

            await vscode.workspace.fs.copy(sourceUri, destUri);

            operation.status = 'completed';
            this.logger.info(`📁 File copied: ${source} -> ${destination}`);

        } catch (error) {
            operation.status = 'failed';
            operation.error = `Copy failed: ${error}`;
            this.logger.error('❌ File copy failed:', error);
        }

        this._updateWebview();
    }

    private async _moveFile(source: string, destination: string) {
        if (!this._checkPermission('write') || !this._checkPermission('delete')) return;

        const operation: FileOperation = {
            id: this._generateId(),
            type: 'move',
            path: `${source} -> ${destination}`,
            timestamp: new Date(),
            status: 'pending'
        };

        this.activeSession!.operations.push(operation);
        this._updateWebview();

        try {
            const sourceUri = vscode.Uri.file(this._resolvePath(source));
            const destUri = vscode.Uri.file(this._resolvePath(destination));

            await vscode.workspace.fs.rename(sourceUri, destUri);

            operation.status = 'completed';
            this.logger.info(`📁 File moved: ${source} -> ${destination}`);

        } catch (error) {
            operation.status = 'failed';
            operation.error = `Move failed: ${error}`;
            this.logger.error('❌ File move failed:', error);
        }

        this._updateWebview();
    }

    private async _listDirectory(dirPath: string) {
        if (!this._checkPermission('read')) return;

        const operation: FileOperation = {
            id: this._generateId(),
            type: 'list',
            path: dirPath,
            timestamp: new Date(),
            status: 'pending'
        };

        this.activeSession!.operations.push(operation);
        this._updateWebview();

        try {
            const fullPath = this._resolvePath(dirPath);
            const uri = vscode.Uri.file(fullPath);

            const entries = await vscode.workspace.fs.readDirectory(uri);
            const fileList = entries.map(([name, type]) => ({
                name,
                type: type === vscode.FileType.Directory ? 'directory' : 'file'
            }));

            operation.status = 'completed';
            operation.content = JSON.stringify(fileList, null, 2);

            // Send directory listing back to webview
            this._view?.webview.postMessage({
                type: 'directoryListing',
                operationId: operation.id,
                path: dirPath,
                entries: fileList
            });

        } catch (error) {
            operation.status = 'failed';
            operation.error = `List failed: ${error}`;
            this.logger.error('❌ Directory listing failed:', error);
        }

        this._updateWebview();
    }

    private async _deleteSession(sessionId: string) {
        const session = this.sessions.get(sessionId);
        if (session) {
            this.sessions.delete(sessionId);

            // Switch to another session if this was active
            if (this.activeSession?.id === sessionId) {
                const remainingSessions = Array.from(this.sessions.values());
                if (remainingSessions.length > 0) {
                    await this._switchSession(remainingSessions[0].id);
                } else {
                    await this._createDefaultSession();
                }
            }

            this._updateWebview();
            this.logger.info(`📁 Session deleted: ${session.name}`);
        }
    }

    private async _exportSession(sessionId: string) {
        const session = this.sessions.get(sessionId);
        if (session) {
            const exportData = {
                session: {
                    name: session.name,
                    workingDirectory: session.workingDirectory,
                    permissions: session.permissions,
                    createdAt: session.createdAt
                },
                operations: session.operations
            };

            const exportJson = JSON.stringify(exportData, null, 2);

            // Show save dialog
            const uri = await vscode.window.showSaveDialog({
                defaultUri: vscode.Uri.file(`orion-session-${session.name}.json`),
                filters: {
                    'JSON Files': ['json']
                }
            });

            if (uri) {
                await vscode.workspace.fs.writeFile(uri, Buffer.from(exportJson, 'utf8'));
                vscode.window.showInformationMessage(`Session exported: ${uri.fsPath}`);
                this.logger.info(`📁 Session exported: ${session.name}`);
            }
        }
    }

    private async _clearSession(sessionId: string) {
        const session = this.sessions.get(sessionId);
        if (session) {
            session.operations = [];
            this._updateWebview();
            this.logger.info(`📁 Session cleared: ${session.name}`);
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview): string {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Orion File System</title>
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

                .fs-header {
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

                .fs-actions {
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

                .fs-content {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }

                .file-operations {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                    margin-bottom: 10px;
                }

                .operation-group {
                    background: var(--vscode-editor-inactiveSelectionBackground);
                    padding: 10px;
                    border-radius: 5px;
                }

                .operation-group h4 {
                    margin: 0 0 10px 0;
                    font-size: 12px;
                    color: var(--vscode-descriptionForeground);
                }

                .input-group {
                    display: flex;
                    flex-direction: column;
                    gap: 5px;
                    margin-bottom: 10px;
                }

                .input-group label {
                    font-size: 11px;
                    color: var(--vscode-descriptionForeground);
                }

                .input-field {
                    background: var(--vscode-input-background);
                    color: var(--vscode-input-foreground);
                    border: 1px solid var(--vscode-input-border);
                    padding: 4px;
                    border-radius: 3px;
                    font-size: 12px;
                }

                .textarea-field {
                    min-height: 60px;
                    resize: vertical;
                    font-family: 'Consolas', monospace;
                }

                .operations-log {
                    flex: 1;
                    overflow-y: auto;
                    background: var(--vscode-editor-background);
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 3px;
                    padding: 10px;
                }

                .operation-entry {
                    margin-bottom: 10px;
                    padding: 8px;
                    border-left: 3px solid var(--vscode-terminal-ansiBlue);
                    background: rgba(0,0,0,0.1);
                    border-radius: 3px;
                }

                .operation-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 5px;
                    font-size: 11px;
                }

                .operation-type {
                    font-weight: bold;
                    text-transform: uppercase;
                }

                .operation-path {
                    font-family: 'Consolas', monospace;
                    color: var(--vscode-terminal-ansiCyan);
                    margin-bottom: 5px;
                }

                .operation-content {
                    background: rgba(0,0,0,0.2);
                    padding: 5px;
                    border-radius: 3px;
                    font-family: 'Consolas', monospace;
                    font-size: 11px;
                    white-space: pre-wrap;
                    max-height: 100px;
                    overflow-y: auto;
                }

                .operation-error {
                    color: var(--vscode-terminal-ansiRed);
                    background: rgba(255,0,0,0.1);
                }

                .status-pending { border-left-color: var(--vscode-terminal-ansiYellow); }
                .status-completed { border-left-color: var(--vscode-terminal-ansiGreen); }
                .status-failed { border-left-color: var(--vscode-terminal-ansiRed); }

                .permissions-display {
                    font-size: 11px;
                    color: var(--vscode-descriptionForeground);
                    margin-left: 10px;
                }

                .permission-badge {
                    display: inline-block;
                    padding: 2px 4px;
                    margin: 0 2px;
                    border-radius: 2px;
                    font-size: 10px;
                }

                .permission-granted {
                    background: var(--vscode-terminal-ansiGreen);
                    color: white;
                }

                .permission-denied {
                    background: var(--vscode-terminal-ansiRed);
                    color: white;
                }

                .empty-state {
                    text-align: center;
                    padding: 40px 20px;
                    opacity: 0.7;
                }
            </style>
        </head>
        <body>
            <div class="fs-header">
                <div class="session-info">
                    <select class="session-selector" id="sessionSelector">
                        <option value="">Select file system session...</option>
                    </select>
                    <div class="permissions-display" id="permissionsDisplay"></div>
                </div>
                <div class="fs-actions">
                    <button class="btn" onclick="newSession()">New</button>
                    <button class="btn btn-secondary" onclick="clearSession()">Clear</button>
                    <button class="btn btn-secondary" onclick="exportSession()">Export</button>
                </div>
            </div>

            <div class="fs-content">
                <div class="file-operations">
                    <div class="operation-group">
                        <h4>📖 Read Operations</h4>
                        <div class="input-group">
                            <label>File Path:</label>
                            <input type="text" class="input-field" id="readPath" placeholder="path/to/file.txt" />
                        </div>
                        <button class="btn" onclick="readFile()">Read File</button>
                        <button class="btn btn-secondary" onclick="listDirectory()">List Directory</button>
                    </div>

                    <div class="operation-group">
                        <h4>✏️ Write Operations</h4>
                        <div class="input-group">
                            <label>File Path:</label>
                            <input type="text" class="input-field" id="writePath" placeholder="path/to/file.txt" />
                        </div>
                        <div class="input-group">
                            <label>Content:</label>
                            <textarea class="input-field textarea-field" id="writeContent" placeholder="File content..."></textarea>
                        </div>
                        <button class="btn" onclick="writeFile()">Write File</button>
                        <button class="btn" onclick="createFile()">Create File</button>
                    </div>
                </div>

                <div class="operations-log" id="operationsLog">
                    <div class="empty-state">
                        <h3>📁 Orion File System</h3>
                        <p>Secure file operations with permission control</p>
                    </div>
                </div>
            </div>

            <script>
                const vscode = acquireVsCodeApi();
                let activeSession = null;
                let sessions = [];

                window.addEventListener('message', event => {
                    const message = event.data;
                    if (message.type === 'updateFileSystem') {
                        activeSession = message.activeSession;
                        sessions = message.sessions;
                        updateUI();
                    } else if (message.type === 'fileContent') {
                        displayFileContent(message);
                    }
                });

                function updateUI() {
                    updateSessionSelector();
                    updatePermissions();
                    updateOperationsLog();
                }

                function updateSessionSelector() {
                    const selector = document.getElementById('sessionSelector');
                    selector.innerHTML = '<option value="">Select file system session...</option>';

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

                function updatePermissions() {
                    const element = document.getElementById('permissionsDisplay');
                    if (!activeSession) {
                        element.innerHTML = '';
                        return;
                    }

                    const perms = activeSession.permissions;
                    element.innerHTML = \`
                        <span class="permission-badge \${perms.read ? 'permission-granted' : 'permission-denied'}">R</span>
                        <span class="permission-badge \${perms.write ? 'permission-granted' : 'permission-denied'}">W</span>
                        <span class="permission-badge \${perms.execute ? 'permission-granted' : 'permission-denied'}">X</span>
                        <span class="permission-badge \${perms.delete ? 'permission-granted' : 'permission-denied'}">D</span>
                    \`;
                }

                function updateOperationsLog() {
                    const container = document.getElementById('operationsLog');

                    if (!activeSession || activeSession.operations.length === 0) {
                        container.innerHTML = '<div class="empty-state"><h3>📁 Orion File System</h3><p>Secure file operations with permission control</p></div>';
                        return;
                    }

                    container.innerHTML = '';
                    activeSession.operations.forEach(op => {
                        const opDiv = document.createElement('div');
                        opDiv.className = \`operation-entry status-\${op.status}\`;

                        const timestamp = new Date(op.timestamp).toLocaleTimeString();

                        let contentHtml = '';
                        if (op.content && op.type !== 'read') {
                            const preview = op.content.length > 200 ? op.content.substring(0, 200) + '...' : op.content;
                            contentHtml = \`<div class="operation-content">\${preview}</div>\`;
                        }
                        if (op.error) {
                            contentHtml += \`<div class="operation-content operation-error">\${op.error}</div>\`;
                        }

                        opDiv.innerHTML = \`
                            <div class="operation-header">
                                <span class="operation-type">\${op.type}</span>
                                <span>\${timestamp}</span>
                                <span>Status: \${op.status}</span>
                                \${op.size ? \`<span>Size: \${op.size} bytes</span>\` : ''}
                            </div>
                            <div class="operation-path">\${op.path}</div>
                            \${contentHtml}
                        \`;

                        container.appendChild(opDiv);
                    });

                    container.scrollTop = container.scrollHeight;
                }

                function readFile() {
                    const path = document.getElementById('readPath').value.trim();
                    if (!path) return;

                    vscode.postMessage({
                        type: 'readFile',
                        path: path
                    });
                }

                function writeFile() {
                    const path = document.getElementById('writePath').value.trim();
                    const content = document.getElementById('writeContent').value;
                    if (!path) return;

                    vscode.postMessage({
                        type: 'writeFile',
                        path: path,
                        content: content
                    });
                }

                function createFile() {
                    const path = document.getElementById('writePath').value.trim();
                    const content = document.getElementById('writeContent').value;
                    if (!path) return;

                    vscode.postMessage({
                        type: 'createFile',
                        path: path,
                        content: content
                    });
                }

                function listDirectory() {
                    const path = document.getElementById('readPath').value.trim() || '.';

                    vscode.postMessage({
                        type: 'listDirectory',
                        path: path
                    });
                }

                function newSession() {
                    const name = prompt('Enter session name:', 'File System Session');
                    const workingDirectory = prompt('Enter working directory:', activeSession?.workingDirectory || '');

                    if (name && workingDirectory) {
                        const permissions = {
                            read: confirm('Allow read operations?'),
                            write: confirm('Allow write operations?'),
                            execute: confirm('Allow execute operations?'),
                            delete: confirm('Allow delete operations?')
                        };

                        vscode.postMessage({
                            type: 'createSession',
                            name: name,
                            workingDirectory: workingDirectory,
                            permissions: permissions
                        });
                    }
                }

                function clearSession() {
                    if (activeSession && confirm('Clear all operations in this session?')) {
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

                function displayFileContent(message) {
                    // Create a new window or panel to display file content
                    const content = message.content;
                    const path = message.path;

                    // For now, just show in a simple alert - could be enhanced with a proper viewer
                    if (content.length > 1000) {
                        const preview = content.substring(0, 1000) + '...';
                        alert(\`File: \${path}\\n\\nContent (first 1000 chars):\\n\${preview}\`);
                    } else {
                        alert(\`File: \${path}\\n\\nContent:\\n\${content}\`);
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
            </script>
        </body>
        </html>`;
    }
}
