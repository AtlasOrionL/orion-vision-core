# 🚀 Orion Vision Core VS Code Extension - User Guide

## 📋 **Overview**

Orion Vision Core VS Code Extension is a powerful AI-powered development assistant that provides intelligent code completion, smart search, deployment management, and real-time monitoring capabilities.

## 🎯 **Features**

### **🤖 AI Assistant**
- **AI-powered code completion**
- **Smart code search and analysis**
- **Code explanation and refactoring suggestions**
- **Debug assistance**

### **🚀 Deployment Manager**
- **Multi-platform deployment support**
- **Real-time deployment tracking**
- **6 deployment targets**: Local, Docker, AWS Lambda, Vercel, Netlify, Google Cloud Run

### **📊 Real-time Monitoring**
- **Performance insights**
- **Network debugging**
- **System status monitoring**

## 🛠️ **Installation & Setup**

### **1. Prerequisites**
- VS Code 1.74.0 or higher
- Node.js 16.0 or higher
- Orion Vision Core server running on localhost:8000

### **2. Server Setup**
Before using the extension, start the Orion API server:

```bash
cd local-deployment
python3 basic_server.py
```

The server should be running on `http://localhost:8000`

### **3. Extension Configuration**
Configure the extension through VS Code settings:

```json
{
  "orion.server.host": "localhost",
  "orion.server.port": 8000,
  "orion.ai.retryAttempts": 3,
  "orion.ai.connectionTimeout": 5000,
  "orion.ai.autoReconnect": true,
  "orion.logging.level": "info"
}
```

## 🎮 **Usage Guide**

### **🤖 Activating AI Assistant**

#### **Method 1: Command Palette**
1. Press `Ctrl + Shift + P` (Windows/Linux) or `Cmd + Shift + P` (Mac)
2. Type "Orion: Activate AI Assistant"
3. Press Enter

#### **Method 2: Status Bar**
1. Click on the "$(robot) Orion: Disconnected" in the status bar
2. The extension will attempt to connect to the AI server

#### **Method 3: Settings**
1. Open VS Code Settings (`Ctrl + ,`)
2. Search for "Orion"
3. Configure server settings if needed

### **🔍 Smart Search**

#### **Using Smart Search**
1. Press `Ctrl + Shift + P`
2. Type "Orion: Smart Search"
3. Enter your search query (e.g., "function that handles authentication")
4. View results in the new webview panel

#### **Search Examples**
- "function that validates user input"
- "class for database connection"
- "error handling patterns"
- "async function examples"

### **💻 Code Completion**

#### **Automatic Completion**
- Type code normally
- AI suggestions will appear automatically
- Press `Tab` to accept suggestions

#### **Manual Completion**
1. Press `Ctrl + Shift + P`
2. Type "Orion: Code Completion"
3. AI will analyze current context and provide suggestions

### **🚀 Deployment Manager**

#### **Opening Deployment Manager**
1. Press `Ctrl + Shift + P`
2. Type "Orion: Open Deployment Manager"
3. The deployment dashboard will open

#### **Available Deployment Targets**
- **Local Development**: Deploy to localhost
- **Docker Container**: Containerized deployment
- **AWS Lambda**: Serverless deployment
- **Vercel**: Frontend deployment
- **Netlify**: Static site deployment
- **Google Cloud Run**: Container deployment

#### **Deployment Process**
1. Select target platform
2. Click deployment button
3. Monitor real-time progress
4. View deployment logs

## 🔧 **Troubleshooting**

### **AI Assistant Not Connecting**

#### **Check Server Status**
```bash
curl http://localhost:8000/api/health
```
Expected response:
```json
{
  "status": "healthy",
  "service": "Orion Vision Core API",
  "version": "1.0.0"
}
```

#### **Common Solutions**
1. **Server not running**: Start the Orion API server
2. **Port conflict**: Change port in settings
3. **Network issues**: Check firewall settings
4. **Configuration error**: Verify settings in VS Code

### **Extension Not Loading**

#### **Check Extension Status**
1. Open VS Code Extensions panel
2. Search for "Orion Vision Core"
3. Ensure extension is enabled

#### **Reload Extension**
1. Press `Ctrl + Shift + P`
2. Type "Developer: Reload Window"
3. Press Enter

### **Performance Issues**

#### **Optimize Settings**
```json
{
  "orion.ai.connectionTimeout": 10000,
  "orion.ai.retryAttempts": 5,
  "orion.logging.level": "warn"
}
```

## 📊 **Status Indicators**

### **Status Bar Icons**
- **$(robot) Orion: Connected** - AI Assistant is ready
- **$(robot) Orion: Disconnected** - AI Assistant needs activation
- **$(robot) Orion: Connecting...** - Connection in progress

### **Output Panel**
View detailed logs in VS Code Output panel:
1. View → Output
2. Select "Orion Vision Core" from dropdown
3. Monitor connection status and errors

## ⚙️ **Advanced Configuration**

### **Custom Server Configuration**
```json
{
  "orion.server.host": "your-server.com",
  "orion.server.port": 9000,
  "orion.ai.connectionTimeout": 15000
}
```

### **Logging Configuration**
```json
{
  "orion.logging.level": "debug"
}
```

### **AI Provider Settings**
```json
{
  "orion.ai.retryAttempts": 5,
  "orion.ai.autoReconnect": true
}
```

## 🎯 **Keyboard Shortcuts**

| Action | Shortcut |
|--------|----------|
| Activate AI Assistant | `Ctrl + Shift + P` → "Orion: Activate AI Assistant" |
| Smart Search | `Ctrl + Shift + P` → "Orion: Smart Search" |
| Code Completion | `Ctrl + Shift + P` → "Orion: Code Completion" |
| Open Deployment Manager | `Ctrl + Shift + P` → "Orion: Open Deployment Manager" |
| Open Dashboard | `Ctrl + Shift + P` → "Orion: Open Dashboard" |

## 🆘 **Support**

### **Getting Help**
- Check Output panel for error messages
- Review this user guide
- Verify server is running and accessible

### **Common Error Messages**
- **"AI Assistant not available"**: Server connection failed
- **"Provider failed to initialize"**: Configuration or server issue
- **"Connection timeout"**: Network or server response issue

## 🎉 **Success Indicators**

### **Extension Working Correctly**
- ✅ Status bar shows "Connected"
- ✅ AI commands respond without errors
- ✅ Deployment Manager opens successfully
- ✅ Smart Search returns results

---

**🚀 Enjoy using Orion Vision Core VS Code Extension!**
