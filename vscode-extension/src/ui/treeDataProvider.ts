/**
 * 🌳 Orion Tree Data Provider
 * Tree view for extension features
 */

import * as vscode from 'vscode';

export class OrionTreeDataProvider implements vscode.TreeDataProvider<OrionTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<OrionTreeItem | undefined | null | void> = new vscode.EventEmitter<OrionTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<OrionTreeItem | undefined | null | void> = this._onDidChangeTreeData.event;

    getTreeItem(element: OrionTreeItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: OrionTreeItem): Thenable<OrionTreeItem[]> {
        if (!element) {
            // Root level items
            return Promise.resolve([
                new OrionTreeItem('AI Assistant', vscode.TreeItemCollapsibleState.Collapsed, 'ai', '🧠'),
                new OrionTreeItem('Mobile Tools', vscode.TreeItemCollapsibleState.Collapsed, 'mobile', '📱'),
                new OrionTreeItem('Network Tools', vscode.TreeItemCollapsibleState.Collapsed, 'network', '🌐'),
                new OrionTreeItem('Performance', vscode.TreeItemCollapsibleState.Collapsed, 'performance', '📊'),
                new OrionTreeItem('Deployment', vscode.TreeItemCollapsibleState.Collapsed, 'deployment', '🚀')
            ]);
        } else {
            // Child items based on category
            switch (element.category) {
                case 'ai':
                    return Promise.resolve([
                        new OrionTreeItem('Activate AI', vscode.TreeItemCollapsibleState.None, 'ai-activate', '🤖', 'orion.activateAI'),
                        new OrionTreeItem('Code Completion', vscode.TreeItemCollapsibleState.None, 'ai-completion', '💻', 'orion.codeCompletion'),
                        new OrionTreeItem('Smart Search', vscode.TreeItemCollapsibleState.None, 'ai-search', '🔍', 'orion.smartSearch')
                    ]);
                case 'mobile':
                    return Promise.resolve([
                        new OrionTreeItem('Mobile Preview', vscode.TreeItemCollapsibleState.None, 'mobile-preview', '📱', 'orion.mobilePreview')
                    ]);
                case 'network':
                    return Promise.resolve([
                        new OrionTreeItem('Network Debug', vscode.TreeItemCollapsibleState.None, 'network-debug', '🌐', 'orion.networkDebug')
                    ]);
                case 'performance':
                    return Promise.resolve([
                        new OrionTreeItem('Performance Insights', vscode.TreeItemCollapsibleState.None, 'performance-insights', '📊', 'orion.performanceInsights')
                    ]);
                case 'deployment':
                    return Promise.resolve([
                        new OrionTreeItem('Deploy App', vscode.TreeItemCollapsibleState.None, 'deploy-app', '🚀', 'orion.deployApp')
                    ]);
                default:
                    return Promise.resolve([]);
            }
        }
    }

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }
}

export class OrionTreeItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly category: string,
        public readonly icon?: string,
        public readonly commandId?: string
    ) {
        super(label, collapsibleState);

        this.tooltip = `${this.label}`;
        this.description = '';

        if (this.icon) {
            this.iconPath = new vscode.ThemeIcon('symbol-misc');
        }

        if (this.commandId) {
            this.command = {
                command: this.commandId,
                title: this.label
            };
        }
    }
}
