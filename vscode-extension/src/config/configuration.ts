/**
 * ⚙️ Orion Configuration Manager
 * Manages extension configuration and settings
 */

import * as vscode from 'vscode';

export class OrionConfiguration {
    private static readonly section = 'orion';

    getAIEnabled(): boolean {
        return this.getConfig<boolean>('ai.enabled', true);
    }

    getAIModel(): string {
        return this.getConfig<string>('ai.model', 'gpt-4');
    }

    getCodeCompletionEnabled(): boolean {
        return this.getConfig<boolean>('codeCompletion.enabled', true);
    }

    getMobilePreviewEnabled(): boolean {
        return this.getConfig<boolean>('mobile.previewEnabled', true);
    }

    getNetworkDebugEnabled(): boolean {
        return this.getConfig<boolean>('networking.debugEnabled', true);
    }

    getPerformanceMonitoringEnabled(): boolean {
        return this.getConfig<boolean>('performance.monitoringEnabled', true);
    }

    getServerHost(): string {
        return this.getConfig<string>('server.host', 'localhost');
    }

    getServerPort(): number {
        return this.getConfig<number>('server.port', 8000);
    }

    getRetryAttempts(): number {
        return this.getConfig<number>('ai.retryAttempts', 3);
    }

    getConnectionTimeout(): number {
        return this.getConfig<number>('ai.connectionTimeout', 5000);
    }

    getAutoReconnect(): boolean {
        return this.getConfig<boolean>('ai.autoReconnect', true);
    }

    getLoggingLevel(): string {
        return this.getConfig<string>('logging.level', 'info');
    }

    private getConfig<T>(key: string, defaultValue: T): T {
        const config = vscode.workspace.getConfiguration(OrionConfiguration.section);
        return config.get<T>(key, defaultValue);
    }

    async updateConfig(key: string, value: any): Promise<void> {
        const config = vscode.workspace.getConfiguration(OrionConfiguration.section);
        await config.update(key, value, vscode.ConfigurationTarget.Global);
    }
}
