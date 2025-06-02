"use strict";
/**
 * 🌳 Orion Tree Data Provider
 * Tree view for extension features
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
exports.OrionTreeItem = exports.OrionTreeDataProvider = void 0;
const vscode = __importStar(require("vscode"));
class OrionTreeDataProvider {
    constructor() {
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    }
    getTreeItem(element) {
        return element;
    }
    getChildren(element) {
        if (!element) {
            // Root level items
            return Promise.resolve([
                new OrionTreeItem('AI Assistant', vscode.TreeItemCollapsibleState.Collapsed, 'ai', '🧠'),
                new OrionTreeItem('Mobile Tools', vscode.TreeItemCollapsibleState.Collapsed, 'mobile', '📱'),
                new OrionTreeItem('Network Tools', vscode.TreeItemCollapsibleState.Collapsed, 'network', '🌐'),
                new OrionTreeItem('Performance', vscode.TreeItemCollapsibleState.Collapsed, 'performance', '📊'),
                new OrionTreeItem('Deployment', vscode.TreeItemCollapsibleState.Collapsed, 'deployment', '🚀')
            ]);
        }
        else {
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
    refresh() {
        this._onDidChangeTreeData.fire();
    }
}
exports.OrionTreeDataProvider = OrionTreeDataProvider;
class OrionTreeItem extends vscode.TreeItem {
    constructor(label, collapsibleState, category, icon, commandId) {
        super(label, collapsibleState);
        this.label = label;
        this.collapsibleState = collapsibleState;
        this.category = category;
        this.icon = icon;
        this.commandId = commandId;
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
exports.OrionTreeItem = OrionTreeItem;
//# sourceMappingURL=treeDataProvider.js.map