/**
 * 📊 Orion Status Bar
 * Status bar integration for quick access
 */

import * as vscode from 'vscode';

export class OrionStatusBar {
    private statusBarItem: vscode.StatusBarItem;

    constructor() {
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );
        
        this.statusBarItem.text = '$(robot) Orion';
        this.statusBarItem.tooltip = 'Orion Vision Core - AI Development Assistant';
        this.statusBarItem.command = 'orion.activateAI';
    }

    show(): void {
        this.statusBarItem.show();
    }

    hide(): void {
        this.statusBarItem.hide();
    }

    updateStatus(status: string, tooltip?: string): void {
        this.statusBarItem.text = `$(robot) Orion: ${status}`;
        if (tooltip) {
            this.statusBarItem.tooltip = tooltip;
        }
    }

    dispose(): void {
        this.statusBarItem.dispose();
    }
}
