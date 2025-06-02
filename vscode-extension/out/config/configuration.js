"use strict";
/**
 * ⚙️ Orion Configuration Manager
 * Manages extension configuration and settings
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
exports.OrionConfiguration = void 0;
const vscode = __importStar(require("vscode"));
class OrionConfiguration {
    getAIEnabled() {
        return this.getConfig('ai.enabled', true);
    }
    getAIModel() {
        return this.getConfig('ai.model', 'gpt-4');
    }
    getCodeCompletionEnabled() {
        return this.getConfig('codeCompletion.enabled', true);
    }
    getMobilePreviewEnabled() {
        return this.getConfig('mobile.previewEnabled', true);
    }
    getNetworkDebugEnabled() {
        return this.getConfig('networking.debugEnabled', true);
    }
    getPerformanceMonitoringEnabled() {
        return this.getConfig('performance.monitoringEnabled', true);
    }
    getServerHost() {
        return this.getConfig('server.host', 'localhost');
    }
    getServerPort() {
        return this.getConfig('server.port', 8000);
    }
    getRetryAttempts() {
        return this.getConfig('ai.retryAttempts', 3);
    }
    getConnectionTimeout() {
        return this.getConfig('ai.connectionTimeout', 5000);
    }
    getAutoReconnect() {
        return this.getConfig('ai.autoReconnect', true);
    }
    getLoggingLevel() {
        return this.getConfig('logging.level', 'info');
    }
    getConfig(key, defaultValue) {
        const config = vscode.workspace.getConfiguration(OrionConfiguration.section);
        return config.get(key, defaultValue);
    }
    async updateConfig(key, value) {
        const config = vscode.workspace.getConfiguration(OrionConfiguration.section);
        await config.update(key, value, vscode.ConfigurationTarget.Global);
    }
}
exports.OrionConfiguration = OrionConfiguration;
OrionConfiguration.section = 'orion';
//# sourceMappingURL=configuration.js.map