"use strict";
/**
 * 💻 Orion Code Completion Provider
 * AI-powered intelligent code completion
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
exports.OrionCodeCompletionProvider = void 0;
const vscode = __importStar(require("vscode"));
const logger_1 = require("../utils/logger");
class OrionCodeCompletionProvider {
    constructor(aiProvider) {
        this.aiProvider = aiProvider;
        this.logger = new logger_1.OrionLogger();
    }
    async provideCompletionItems(document, position, token, context) {
        if (!this.aiProvider.isAIConnected()) {
            return [];
        }
        try {
            // Get current line and context
            const line = document.lineAt(position);
            const linePrefix = line.text.substring(0, position.character);
            const lineText = line.text;
            // Get surrounding context (5 lines before and after)
            const startLine = Math.max(0, position.line - 5);
            const endLine = Math.min(document.lineCount - 1, position.line + 5);
            const contextRange = new vscode.Range(startLine, 0, endLine, 0);
            const contextText = document.getText(contextRange);
            // Determine language
            const language = document.languageId;
            // Skip if the line is empty or just whitespace
            if (linePrefix.trim().length === 0) {
                return [];
            }
            // Generate AI completion
            const aiResponse = await this.aiProvider.generateCompletion({
                prompt: `Complete this ${language} code:\n${linePrefix}`,
                context: `File: ${document.fileName}\nLanguage: ${language}\nContext:\n${contextText}`,
                language: language,
                type: 'completion'
            });
            // Parse AI response and create completion items
            const completions = this.parseAIResponse(aiResponse.result, linePrefix, language);
            // Add metadata to completions
            completions.forEach(completion => {
                completion.detail = `Orion AI (${Math.round(aiResponse.confidence * 100)}% confidence)`;
                completion.documentation = new vscode.MarkdownString(`🤖 **AI-Generated Completion**\n\nConfidence: ${Math.round(aiResponse.confidence * 100)}%`);
            });
            return completions;
        }
        catch (error) {
            this.logger.error('❌ Code completion failed:', error);
            return [];
        }
    }
    parseAIResponse(response, linePrefix, language) {
        const completions = [];
        try {
            // Split response into lines and filter relevant completions
            const lines = response.split('\n').filter(line => line.trim().length > 0);
            for (const line of lines) {
                const trimmedLine = line.trim();
                // Skip comments and empty lines
                if (this.isComment(trimmedLine, language) || trimmedLine.length === 0) {
                    continue;
                }
                // Create completion item
                const completion = new vscode.CompletionItem(trimmedLine, this.getCompletionKind(trimmedLine, language));
                completion.insertText = trimmedLine;
                completion.filterText = trimmedLine;
                completion.sortText = '0'; // High priority
                // Add additional info based on language
                this.enhanceCompletion(completion, trimmedLine, language);
                completions.push(completion);
            }
        }
        catch (error) {
            this.logger.error('❌ Failed to parse AI response:', error);
        }
        return completions.slice(0, 10); // Limit to top 10 suggestions
    }
    isComment(line, language) {
        const commentPrefixes = {
            'javascript': ['//', '/*', '*'],
            'typescript': ['//', '/*', '*'],
            'python': ['#'],
            'java': ['//', '/*', '*'],
            'csharp': ['//', '/*', '*'],
            'cpp': ['//', '/*', '*'],
            'c': ['//', '/*', '*'],
            'go': ['//', '/*', '*'],
            'rust': ['//', '/*', '*'],
            'php': ['//', '/*', '*', '#'],
            'ruby': ['#'],
            'shell': ['#'],
            'bash': ['#']
        };
        const prefixes = commentPrefixes[language] || ['//'];
        return prefixes.some(prefix => line.startsWith(prefix));
    }
    getCompletionKind(text, language) {
        // Determine completion kind based on content
        if (text.includes('function') || text.includes('def ') || text.includes('func ')) {
            return vscode.CompletionItemKind.Function;
        }
        if (text.includes('class ') || text.includes('interface ')) {
            return vscode.CompletionItemKind.Class;
        }
        if (text.includes('const ') || text.includes('let ') || text.includes('var ')) {
            return vscode.CompletionItemKind.Variable;
        }
        if (text.includes('import ') || text.includes('from ') || text.includes('#include')) {
            return vscode.CompletionItemKind.Module;
        }
        if (text.includes('if ') || text.includes('for ') || text.includes('while ')) {
            return vscode.CompletionItemKind.Keyword;
        }
        return vscode.CompletionItemKind.Text;
    }
    enhanceCompletion(completion, text, language) {
        // Add language-specific enhancements
        switch (language) {
            case 'javascript':
            case 'typescript':
                this.enhanceJavaScriptCompletion(completion, text);
                break;
            case 'python':
                this.enhancePythonCompletion(completion, text);
                break;
            case 'java':
                this.enhanceJavaCompletion(completion, text);
                break;
            default:
                // Generic enhancement
                break;
        }
    }
    enhanceJavaScriptCompletion(completion, text) {
        if (text.includes('function')) {
            completion.insertText = new vscode.SnippetString(text.replace('()', '($1)$0'));
        }
        if (text.includes('console.log')) {
            completion.insertText = new vscode.SnippetString(text.replace('()', '($1)$0'));
        }
    }
    enhancePythonCompletion(completion, text) {
        if (text.includes('def ')) {
            completion.insertText = new vscode.SnippetString(text.replace('():', '($1):$0'));
        }
        if (text.includes('print')) {
            completion.insertText = new vscode.SnippetString(text.replace('()', '($1)$0'));
        }
    }
    enhanceJavaCompletion(completion, text) {
        if (text.includes('public ') || text.includes('private ') || text.includes('protected ')) {
            completion.insertText = new vscode.SnippetString(text.replace('()', '($1)$0'));
        }
    }
    async provideCompletions(editor) {
        if (!this.aiProvider.isAIConnected()) {
            vscode.window.showWarningMessage('Orion AI is not connected. Please activate AI first.');
            return;
        }
        const document = editor.document;
        const position = editor.selection.active;
        // Get current context
        const line = document.lineAt(position);
        const linePrefix = line.text.substring(0, position.character);
        if (linePrefix.trim().length === 0) {
            vscode.window.showInformationMessage('Place cursor after some code to get AI completions.');
            return;
        }
        try {
            // Show progress
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "🤖 Generating AI completions...",
                cancellable: true
            }, async (progress, token) => {
                const completions = await this.provideCompletionItems(document, position, token, { triggerKind: vscode.CompletionTriggerKind.Invoke, triggerCharacter: undefined });
                if (completions && completions.length > 0) {
                    // Show completion picker
                    const selected = await vscode.window.showQuickPick(completions.map(item => ({
                        label: item.label,
                        description: item.detail,
                        item: item
                    })), {
                        placeHolder: 'Select AI completion',
                        matchOnDescription: true
                    });
                    if (selected) {
                        // Insert selected completion
                        const edit = new vscode.WorkspaceEdit();
                        const range = new vscode.Range(position, position);
                        edit.replace(document.uri, range, selected.item.insertText);
                        await vscode.workspace.applyEdit(edit);
                    }
                }
                else {
                    vscode.window.showInformationMessage('No AI completions available for current context.');
                }
            });
        }
        catch (error) {
            this.logger.error('❌ Manual completion failed:', error);
            vscode.window.showErrorMessage('Failed to generate AI completions.');
        }
    }
}
exports.OrionCodeCompletionProvider = OrionCodeCompletionProvider;
//# sourceMappingURL=codeCompletionProvider.js.map