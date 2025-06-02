/**
 * 📝 Orion Logger Utility
 * Centralized logging for the extension
 */

import * as vscode from 'vscode';

export class OrionLogger {
    private outputChannel: vscode.OutputChannel;
    private static instance: OrionLogger;

    constructor() {
        this.outputChannel = vscode.window.createOutputChannel('Orion Vision Core');
        this.outputChannel.show(true);
    }

    static getInstance(): OrionLogger {
        if (!OrionLogger.instance) {
            OrionLogger.instance = new OrionLogger();
        }
        return OrionLogger.instance;
    }

    info(message: string, ...args: any[]): void {
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] ✅ INFO: ${message}`;
        this.outputChannel.appendLine(logMessage);

        if (args.length > 0) {
            this.outputChannel.appendLine(`  📋 Args: ${JSON.stringify(args, null, 2)}`);
        }

        console.log(logMessage, ...args);
    }

    request(method: string, url: string, data?: any): void {
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] 🔄 REQUEST: ${method} ${url}`;
        this.outputChannel.appendLine(logMessage);

        if (data) {
            this.outputChannel.appendLine(`  📤 Data: ${JSON.stringify(data, null, 2)}`);
        }
    }

    response(method: string, url: string, status: number, data?: any): void {
        const timestamp = new Date().toISOString();
        const emoji = status >= 200 && status < 300 ? '✅' : status >= 400 ? '❌' : '⚠️';
        const logMessage = `[${timestamp}] ${emoji} RESPONSE: ${method} ${url} - ${status}`;
        this.outputChannel.appendLine(logMessage);

        if (data) {
            this.outputChannel.appendLine(`  📥 Data: ${JSON.stringify(data, null, 2)}`);
        }
    }

    command(command: string, args?: any[]): void {
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] 🎯 COMMAND: ${command}`;
        this.outputChannel.appendLine(logMessage);

        if (args && args.length > 0) {
            this.outputChannel.appendLine(`  📋 Args: ${JSON.stringify(args, null, 2)}`);
        }
    }

    error(message: string, error?: any): void {
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] ❌ ERROR: ${message}`;
        this.outputChannel.appendLine(logMessage);

        if (error) {
            this.outputChannel.appendLine(`  🚨 Error: ${error.toString()}`);
            if (error.stack) {
                this.outputChannel.appendLine(`  📍 Stack: ${error.stack}`);
            }
        }

        console.error(logMessage, error);
        vscode.window.showErrorMessage(`Orion Error: ${message}`);
    }

    warn(message: string, ...args: any[]): void {
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] ⚠️ WARN: ${message}`;
        this.outputChannel.appendLine(logMessage);

        if (args.length > 0) {
            this.outputChannel.appendLine(`  📋 Args: ${JSON.stringify(args, null, 2)}`);
        }

        console.warn(logMessage, ...args);
        vscode.window.showWarningMessage(`Orion Warning: ${message}`);
    }

    debug(message: string, ...args: any[]): void {
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] 🔍 DEBUG: ${message}`;
        this.outputChannel.appendLine(logMessage);

        if (args.length > 0) {
            this.outputChannel.appendLine(`  📋 Args: ${JSON.stringify(args, null, 2)}`);
        }

        console.debug(logMessage, ...args);
    }

    show(): void {
        this.outputChannel.show();
    }

    dispose(): void {
        this.outputChannel.dispose();
    }
}
