#!/usr/bin/env python3
"""
Provider Test Script
Test all extension providers
"""

import requests
import json
import time

def test_orion_server():
    """Test Orion server connectivity"""
    print('🔍 Testing Orion server...')
    
    endpoints = [
        'http://localhost:8000/health',
        'http://localhost:8000/api/status',
        'http://localhost:8000/api/ai/status',
        'http://localhost:8000/api/completion/status'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=2)
            if response.status_code == 200:
                print(f'  ✅ {endpoint}: OK')
            else:
                print(f'  ⚠️ {endpoint}: Status {response.status_code}')
        except requests.exceptions.ConnectionError:
            print(f'  ❌ {endpoint}: Connection failed')
        except requests.exceptions.Timeout:
            print(f'  ⏱️ {endpoint}: Timeout')

def test_ollama_connection():
    """Test Ollama connectivity"""
    print('\n🤖 Testing Ollama connection...')
    
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f'  ✅ Ollama: {len(models)} models available')
            for model in models[:3]:
                print(f'    🤖 {model.get("name", "Unknown")}')
        else:
            print(f'  ⚠️ Ollama: Status {response.status_code}')
    except requests.exceptions.ConnectionError:
        print('  ❌ Ollama: Not running')
    except requests.exceptions.Timeout:
        print('  ⏱️ Ollama: Timeout')

def main():
    print('🧪 PROVIDER CONNECTIVITY TEST')
    print('=' * 40)
    
    test_orion_server()
    test_ollama_connection()
    
    print('\n💡 If tests fail:')
    print('  1. Start Orion server: python orion_server.py')
    print('  2. Start Ollama: ollama serve')
    print('  3. Restart VS Code')

if __name__ == '__main__':
    main()
