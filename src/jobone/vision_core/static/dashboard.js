/**
 * Orion Agent Management Dashboard JavaScript
 * Atlas Prompt 3.1.2 - Web Dashboard Implementation
 */

// Global configuration
const CONFIG = {
    apiUrl: 'http://localhost:8000',
    refreshInterval: 5000, // 5 seconds
    autoRefresh: true
};

// Global state
let refreshTimer = null;
let currentSection = 'dashboard';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Orion Agent Management Dashboard initialized');
    
    // Load settings from localStorage
    loadSettings();
    
    // Start auto refresh
    if (CONFIG.autoRefresh) {
        startAutoRefresh();
    }
    
    // Initial data load
    refreshAll();
    
    // Load modules for create agent modal
    loadModulesForSelect();
});

// Settings management
function loadSettings() {
    const savedApiUrl = localStorage.getItem('apiUrl');
    const savedRefreshInterval = localStorage.getItem('refreshInterval');
    
    if (savedApiUrl) {
        CONFIG.apiUrl = savedApiUrl;
        document.getElementById('api-url').value = savedApiUrl;
    }
    
    if (savedRefreshInterval) {
        CONFIG.refreshInterval = parseInt(savedRefreshInterval) * 1000;
        document.getElementById('refresh-interval').value = parseInt(savedRefreshInterval);
    }
}

function saveSettings() {
    const apiUrl = document.getElementById('api-url').value;
    const refreshInterval = document.getElementById('refresh-interval').value;
    
    CONFIG.apiUrl = apiUrl;
    CONFIG.refreshInterval = parseInt(refreshInterval) * 1000;
    
    localStorage.setItem('apiUrl', apiUrl);
    localStorage.setItem('refreshInterval', refreshInterval);
    
    showNotification('Settings saved successfully', 'success');
    
    // Restart auto refresh with new interval
    if (CONFIG.autoRefresh) {
        stopAutoRefresh();
        startAutoRefresh();
    }
}

// Auto refresh management
function startAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }
    
    refreshTimer = setInterval(() => {
        if (currentSection === 'dashboard') {
            refreshDashboard();
        } else if (currentSection === 'modules') {
            loadModules();
        } else if (currentSection === 'agents') {
            loadAgents();
        }
    }, CONFIG.refreshInterval);
    
    document.getElementById('auto-refresh-status').textContent = 'Enabled';
    document.getElementById('auto-refresh-status').className = 'badge bg-success';
}

function stopAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
        refreshTimer = null;
    }
    
    document.getElementById('auto-refresh-status').textContent = 'Disabled';
    document.getElementById('auto-refresh-status').className = 'badge bg-secondary';
}

// Section management
function showSection(sectionName) {
    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.style.display = 'none';
    });
    
    // Show selected section
    document.getElementById(sectionName + '-section').style.display = 'block';
    
    // Update navigation
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
    });
    
    event.target.classList.add('active');
    currentSection = sectionName;
    
    // Load section data
    if (sectionName === 'dashboard') {
        refreshDashboard();
    } else if (sectionName === 'modules') {
        loadModules();
    } else if (sectionName === 'agents') {
        loadAgents();
    } else if (sectionName === 'logs') {
        loadLogs();
    }
}

// API helper functions
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(CONFIG.apiUrl + endpoint, options);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
        
    } catch (error) {
        console.error('API call failed:', error);
        updateApiStatus('error');
        throw error;
    }
}

function updateApiStatus(status) {
    const statusElement = document.getElementById('api-status');
    
    if (status === 'error') {
        statusElement.textContent = 'Disconnected';
        statusElement.previousElementSibling.className = 'fas fa-circle text-danger me-1';
    } else {
        statusElement.textContent = 'Connected';
        statusElement.previousElementSibling.className = 'fas fa-circle text-success me-1';
    }
}

// Dashboard functions
async function refreshDashboard() {
    try {
        await Promise.all([
            loadSystemStats(),
            loadSystemHealth()
        ]);
        
        updateApiStatus('success');
        document.getElementById('last-updated').textContent = new Date().toLocaleTimeString();
        
    } catch (error) {
        console.error('Dashboard refresh failed:', error);
        showNotification('Failed to refresh dashboard', 'error');
    }
}

async function loadSystemStats() {
    try {
        const response = await apiCall('/system/stats');
        
        if (response.success) {
            const stats = response.data;
            
            // Update metric cards
            document.getElementById('total-modules').textContent = stats.loader.total_modules;
            document.getElementById('total-agents').textContent = stats.loader.total_agents;
            document.getElementById('running-agents').textContent = stats.loader.running_agents;
            document.getElementById('healthy-agents').textContent = stats.registry.healthy_agents;
            
            // Update system stats display
            const statsHtml = `
                <div class="row">
                    <div class="col-6">
                        <strong>Loader Status:</strong><br>
                        <span class="badge bg-primary">${stats.loader.status}</span>
                    </div>
                    <div class="col-6">
                        <strong>Loaded Modules:</strong><br>
                        ${stats.loader.loaded_modules}
                    </div>
                </div>
                <hr>
                <div class="row">
                    <div class="col-6">
                        <strong>Registry Agents:</strong><br>
                        ${stats.registry.total_agents}
                    </div>
                    <div class="col-6">
                        <strong>Agent Types:</strong><br>
                        ${stats.registry.agent_types}
                    </div>
                </div>
            `;
            
            document.getElementById('system-stats').innerHTML = statsHtml;
        }
        
    } catch (error) {
        document.getElementById('system-stats').innerHTML = 
            '<div class="alert alert-danger">Failed to load system statistics</div>';
    }
}

async function loadSystemHealth() {
    try {
        const response = await apiCall('/system/health');
        
        if (response.success) {
            const health = response.data;
            
            const healthClass = health.overall_health === 'healthy' ? 'success' : 'warning';
            
            const healthHtml = `
                <div class="text-center mb-3">
                    <h4 class="text-${healthClass}">
                        <i class="fas fa-heartbeat me-2"></i>
                        ${health.overall_health.toUpperCase()}
                    </h4>
                </div>
                <div class="row text-center">
                    <div class="col-4">
                        <div class="border-end">
                            <h5>${health.running_agents}</h5>
                            <small>Running</small>
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="border-end">
                            <h5>${health.healthy_agents}</h5>
                            <small>Healthy</small>
                        </div>
                    </div>
                    <div class="col-4">
                        <h5>${health.total_agents}</h5>
                        <small>Total</small>
                    </div>
                </div>
            `;
            
            document.getElementById('system-health').innerHTML = healthHtml;
        }
        
    } catch (error) {
        document.getElementById('system-health').innerHTML = 
            '<div class="alert alert-danger">Failed to load system health</div>';
    }
}

// Module functions
async function loadModules() {
    try {
        const response = await apiCall('/modules');
        
        if (response.success) {
            const modules = response.data;
            const container = document.getElementById('modules-container');
            
            if (modules.length === 0) {
                container.innerHTML = '<div class="col-12"><div class="alert alert-info">No modules found</div></div>';
                return;
            }
            
            let modulesHtml = '';
            
            modules.forEach(module => {
                const statusClass = module.is_loaded ? 'success' : 'secondary';
                const statusIcon = module.is_loaded ? 'check-circle' : 'circle';
                
                modulesHtml += `
                    <div class="col-md-4 mb-3">
                        <div class="card module-card">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h6 class="mb-0">${module.module_name}</h6>
                                <span class="badge bg-${statusClass}">
                                    <i class="fas fa-${statusIcon} me-1"></i>
                                    ${module.is_loaded ? 'Loaded' : 'Not Loaded'}
                                </span>
                            </div>
                            <div class="card-body">
                                <p class="card-text">
                                    <strong>Class:</strong> ${module.agent_class_name || 'N/A'}<br>
                                    <strong>Path:</strong> <small>${module.module_path}</small>
                                </p>
                                ${module.error_message ? 
                                    `<div class="alert alert-danger alert-sm">${module.error_message}</div>` : 
                                    ''
                                }
                            </div>
                            <div class="card-footer">
                                <div class="btn-group w-100">
                                    ${!module.is_loaded ? 
                                        `<button class="btn btn-primary btn-sm" onclick="loadModule('${module.module_name}')">
                                            <i class="fas fa-download me-1"></i>Load
                                        </button>` :
                                        `<button class="btn btn-warning btn-sm" onclick="reloadModule('${module.module_name}')">
                                            <i class="fas fa-sync-alt me-1"></i>Reload
                                        </button>`
                                    }
                                    <button class="btn btn-info btn-sm" onclick="showModuleInfo('${module.module_name}')">
                                        <i class="fas fa-info me-1"></i>Info
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            container.innerHTML = modulesHtml;
        }
        
    } catch (error) {
        document.getElementById('modules-container').innerHTML = 
            '<div class="col-12"><div class="alert alert-danger">Failed to load modules</div></div>';
    }
}

async function scanModules() {
    try {
        showNotification('Scanning modules...', 'info');
        const response = await apiCall('/modules/scan', 'POST');
        
        if (response.success) {
            showNotification(`Scan completed: ${response.data.modules.length} modules found`, 'success');
            loadModules();
        }
        
    } catch (error) {
        showNotification('Failed to scan modules', 'error');
    }
}

async function loadModule(moduleName) {
    try {
        showNotification(`Loading module: ${moduleName}`, 'info');
        const response = await apiCall('/modules/load', 'POST', { module_name: moduleName });
        
        if (response.success) {
            showNotification(`Module ${moduleName} loaded successfully`, 'success');
            loadModules();
            loadModulesForSelect(); // Update create agent modal
        }
        
    } catch (error) {
        showNotification(`Failed to load module: ${moduleName}`, 'error');
    }
}

async function reloadModule(moduleName) {
    try {
        showNotification(`Reloading module: ${moduleName}`, 'info');
        const response = await apiCall(`/modules/${moduleName}/reload`, 'POST');
        
        if (response.success) {
            showNotification(`Module ${moduleName} reloaded successfully`, 'success');
            loadModules();
        }
        
    } catch (error) {
        showNotification(`Failed to reload module: ${moduleName}`, 'error');
    }
}

async function loadAllModules() {
    try {
        const response = await apiCall('/modules');
        
        if (response.success) {
            const unloadedModules = response.data.filter(m => !m.is_loaded);
            
            if (unloadedModules.length === 0) {
                showNotification('All modules are already loaded', 'info');
                return;
            }
            
            showNotification(`Loading ${unloadedModules.length} modules...`, 'info');
            
            for (const module of unloadedModules) {
                await loadModule(module.module_name);
            }
            
            showNotification('All modules loaded successfully', 'success');
        }
        
    } catch (error) {
        showNotification('Failed to load all modules', 'error');
    }
}

// Agent functions
async function loadAgents() {
    try {
        const response = await apiCall('/agents');
        
        if (response.success) {
            const agents = response.data;
            const container = document.getElementById('agents-container');
            
            if (agents.length === 0) {
                container.innerHTML = '<div class="col-12"><div class="alert alert-info">No agents found</div></div>';
                return;
            }
            
            let agentsHtml = '';
            
            agents.forEach(agent => {
                const statusClass = getStatusClass(agent.status);
                const statusIcon = getStatusIcon(agent.status);
                
                agentsHtml += `
                    <div class="col-md-6 mb-3">
                        <div class="card agent-card">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h6 class="mb-0">${agent.agent_name}</h6>
                                <span class="badge bg-${statusClass}">
                                    <i class="fas fa-${statusIcon} me-1"></i>
                                    ${agent.status}
                                </span>
                            </div>
                            <div class="card-body">
                                <p class="card-text">
                                    <strong>ID:</strong> ${agent.agent_id}<br>
                                    <strong>Type:</strong> ${agent.agent_type}<br>
                                    <strong>Uptime:</strong> ${formatUptime(agent.uptime)}<br>
                                    <strong>Health:</strong> 
                                    <span class="badge ${agent.is_healthy ? 'bg-success' : 'bg-danger'}">
                                        ${agent.is_healthy ? 'Healthy' : 'Unhealthy'}
                                    </span>
                                </p>
                                <div class="mb-2">
                                    <strong>Capabilities:</strong><br>
                                    ${agent.capabilities.map(cap => 
                                        `<span class="badge bg-info me-1">${cap}</span>`
                                    ).join('')}
                                </div>
                            </div>
                            <div class="card-footer">
                                <div class="btn-group w-100">
                                    ${agent.status === 'running' ?
                                        `<button class="btn btn-warning btn-sm" onclick="stopAgent('${agent.agent_id}')">
                                            <i class="fas fa-stop me-1"></i>Stop
                                        </button>` :
                                        `<button class="btn btn-success btn-sm" onclick="startAgent('${agent.agent_id}')">
                                            <i class="fas fa-play me-1"></i>Start
                                        </button>`
                                    }
                                    <button class="btn btn-info btn-sm" onclick="showAgentInfo('${agent.agent_id}')">
                                        <i class="fas fa-info me-1"></i>Info
                                    </button>
                                    <button class="btn btn-danger btn-sm" onclick="deleteAgent('${agent.agent_id}')">
                                        <i class="fas fa-trash me-1"></i>Delete
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            container.innerHTML = agentsHtml;
        }
        
    } catch (error) {
        document.getElementById('agents-container').innerHTML = 
            '<div class="col-12"><div class="alert alert-danger">Failed to load agents</div></div>';
    }
}

async function loadModulesForSelect() {
    try {
        const response = await apiCall('/modules');
        
        if (response.success) {
            const select = document.getElementById('module-select');
            select.innerHTML = '<option value="">Select a module...</option>';
            
            const loadedModules = response.data.filter(m => m.is_loaded);
            
            loadedModules.forEach(module => {
                const option = document.createElement('option');
                option.value = module.module_name;
                option.textContent = `${module.module_name} (${module.agent_class_name})`;
                select.appendChild(option);
            });
        }
        
    } catch (error) {
        console.error('Failed to load modules for select:', error);
    }
}

async function createAgent() {
    try {
        const moduleName = document.getElementById('module-select').value;
        const agentId = document.getElementById('agent-id').value;
        const configPath = document.getElementById('config-path').value;
        const autoStart = document.getElementById('auto-start').checked;
        
        if (!moduleName || !agentId) {
            showNotification('Please fill in required fields', 'error');
            return;
        }
        
        const data = {
            module_name: moduleName,
            agent_id: agentId,
            auto_start: autoStart
        };
        
        if (configPath) {
            data.config_path = configPath;
        }
        
        showNotification(`Creating agent: ${agentId}`, 'info');
        const response = await apiCall('/agents', 'POST', data);
        
        if (response.success) {
            showNotification(`Agent ${agentId} created successfully`, 'success');
            
            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('createAgentModal'));
            modal.hide();
            document.getElementById('create-agent-form').reset();
            
            // Refresh agents list
            loadAgents();
        }
        
    } catch (error) {
        showNotification('Failed to create agent', 'error');
    }
}

async function startAgent(agentId) {
    try {
        showNotification(`Starting agent: ${agentId}`, 'info');
        const response = await apiCall(`/agents/${agentId}/start`, 'POST');
        
        if (response.success) {
            showNotification(`Agent ${agentId} started successfully`, 'success');
            loadAgents();
        }
        
    } catch (error) {
        showNotification(`Failed to start agent: ${agentId}`, 'error');
    }
}

async function stopAgent(agentId) {
    try {
        showNotification(`Stopping agent: ${agentId}`, 'info');
        const response = await apiCall(`/agents/${agentId}/stop`, 'POST');
        
        if (response.success) {
            showNotification(`Agent ${agentId} stopped successfully`, 'success');
            loadAgents();
        }
        
    } catch (error) {
        showNotification(`Failed to stop agent: ${agentId}`, 'error');
    }
}

async function deleteAgent(agentId) {
    if (!confirm(`Are you sure you want to delete agent: ${agentId}?`)) {
        return;
    }
    
    try {
        showNotification(`Deleting agent: ${agentId}`, 'info');
        const response = await apiCall(`/agents/${agentId}`, 'DELETE');
        
        if (response.success) {
            showNotification(`Agent ${agentId} deleted successfully`, 'success');
            loadAgents();
        }
        
    } catch (error) {
        showNotification(`Failed to delete agent: ${agentId}`, 'error');
    }
}

// Utility functions
function getStatusClass(status) {
    switch (status.toLowerCase()) {
        case 'running': return 'success';
        case 'stopped': return 'secondary';
        case 'error': return 'danger';
        case 'starting': return 'info';
        default: return 'secondary';
    }
}

function getStatusIcon(status) {
    switch (status.toLowerCase()) {
        case 'running': return 'play-circle';
        case 'stopped': return 'stop-circle';
        case 'error': return 'exclamation-circle';
        case 'starting': return 'spinner';
        default: return 'circle';
    }
}

function formatUptime(seconds) {
    if (seconds < 60) {
        return `${Math.floor(seconds)}s`;
    } else if (seconds < 3600) {
        return `${Math.floor(seconds / 60)}m ${Math.floor(seconds % 60)}s`;
    } else {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${minutes}m`;
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function refreshAll() {
    refreshDashboard();
    if (currentSection === 'modules') {
        loadModules();
    } else if (currentSection === 'agents') {
        loadAgents();
    }
}

function loadLogs() {
    // Placeholder for logs functionality
    document.getElementById('logs-container').innerHTML = 
        '<div class="text-muted">Log streaming functionality will be implemented here...</div>';
}

function clearLogs() {
    document.getElementById('logs-container').innerHTML = '';
}
