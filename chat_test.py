#!/usr/bin/env python3
"""
Orion Vision Core - Interactive Chat Test
Real-time chat interface with Ollama AI

Author: Atlas-orion (Augment Agent)
Date: 2 Haziran 2025
Purpose: Interactive AI chat testing
"""

import sys
import json
import time
import requests
from datetime import datetime

def print_header():
    """Print chat header"""
    print("🤖 ORION VISION CORE - AI CHAT TEST")
    print("=" * 50)
    print("💬 Interactive chat with Ollama AI")
    print("🎯 Type 'quit' to exit, 'models' to see available models")
    print("=" * 50)

def get_available_models():
    """Get available Ollama models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            return [(model['name'], model.get('size', 0) / (1024*1024*1024)) for model in models]
        return []
    except:
        return []

def send_chat_message(model, message, stream=False):
    """Send message to Ollama and get response"""
    try:
        payload = {
            "model": model,
            "prompt": message,
            "stream": stream
        }
        
        start_time = time.time()
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get('response', 'No response')
            total_duration = data.get('total_duration', 0) / 1e9
            
            return {
                'success': True,
                'response': ai_response,
                'response_time': response_time,
                'generation_time': total_duration,
                'model': model
            }
        else:
            return {
                'success': False,
                'error': f"HTTP {response.status_code}",
                'response_time': response_time
            }
            
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': "Request timeout (30s)",
            'response_time': 30.0
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'response_time': 0
        }

def interactive_chat():
    """Main interactive chat function"""
    print_header()
    
    # Get available models
    models = get_available_models()
    if not models:
        print("❌ No Ollama models available!")
        print("💡 Make sure Ollama is running: ollama serve")
        return
    
    print(f"\n📊 Available models:")
    for i, (name, size) in enumerate(models, 1):
        print(f"  {i}. {name} ({size:.1f}GB)")
    
    # Select model
    while True:
        try:
            choice = input(f"\nSelect model (1-{len(models)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(models):
                selected_model = models[int(choice) - 1][0]
                break
            else:
                print("❌ Invalid choice!")
        except KeyboardInterrupt:
            print("\n👋 Chat cancelled!")
            return
    
    print(f"\n🤖 Selected model: {selected_model}")
    print(f"💬 Chat started! Type your messages below:")
    print("-" * 50)
    
    chat_history = []
    message_count = 0
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Chat ended!")
                break
                
            if user_input.lower() == 'models':
                print(f"\n📊 Available models:")
                for i, (name, size) in enumerate(models, 1):
                    current = " (current)" if name == selected_model else ""
                    print(f"  {i}. {name} ({size:.1f}GB){current}")
                continue
                
            if user_input.lower() == 'history':
                print(f"\n📜 Chat history ({len(chat_history)} messages):")
                for i, (user_msg, ai_msg, timestamp) in enumerate(chat_history, 1):
                    print(f"  {i}. [{timestamp}]")
                    print(f"     👤 {user_msg[:50]}...")
                    print(f"     🤖 {ai_msg[:50]}...")
                continue
                
            if user_input.lower().startswith('switch '):
                try:
                    model_num = int(user_input.split()[1])
                    if 1 <= model_num <= len(models):
                        selected_model = models[model_num - 1][0]
                        print(f"🔄 Switched to model: {selected_model}")
                    else:
                        print("❌ Invalid model number!")
                except:
                    print("❌ Usage: switch <model_number>")
                continue
            
            # Send message to AI
            print("🤖 AI: ", end="", flush=True)
            print("⏳ Thinking...", end="", flush=True)
            
            result = send_chat_message(selected_model, user_input)
            
            print("\r🤖 AI: ", end="", flush=True)
            
            if result['success']:
                ai_response = result['response']
                response_time = result['response_time']
                generation_time = result['generation_time']
                
                # Print AI response
                print(ai_response)
                print(f"⏱️ Response: {response_time:.2f}s | Generation: {generation_time:.2f}s")
                
                # Add to history
                timestamp = datetime.now().strftime("%H:%M:%S")
                chat_history.append((user_input, ai_response, timestamp))
                message_count += 1
                
                # Show stats every 5 messages
                if message_count % 5 == 0:
                    avg_response_time = sum(h[2] for h in chat_history[-5:] if len(h) > 3) / 5
                    print(f"📊 Stats: {message_count} messages, avg response: {avg_response_time:.2f}s")
                
            else:
                print(f"❌ Error: {result['error']}")
                print(f"⏱️ Failed after: {result['response_time']:.2f}s")
            
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
    
    # Final stats
    if chat_history:
        print(f"\n📊 Final Chat Statistics:")
        print(f"  💬 Total messages: {len(chat_history)}")
        print(f"  🤖 Model used: {selected_model}")
        print(f"  ⏱️ Chat duration: {datetime.now().strftime('%H:%M:%S')}")
        
        if len(chat_history) >= 3:
            recent_times = [h[2] for h in chat_history[-3:] if len(h) > 3]
            if recent_times:
                avg_time = sum(recent_times) / len(recent_times)
                print(f"  📈 Avg response time: {avg_time:.2f}s")

def quick_chat_test():
    """Quick automated chat test"""
    print("🧪 QUICK CHAT TEST")
    print("-" * 30)
    
    models = get_available_models()
    if not models:
        print("❌ No models available!")
        return
    
    model = models[0][0]  # Use first available model
    print(f"🤖 Testing with model: {model}")
    
    test_messages = [
        "Merhaba! Nasılsın?",
        "Orion Vision Core hakkında ne düşünüyorsun?",
        "Python programlama hakkında kısa bilgi ver.",
        "Teşekkürler!"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. 👤 User: {message}")
        print("   🤖 AI: ", end="", flush=True)
        
        result = send_chat_message(model, message)
        
        if result['success']:
            response = result['response']
            time_taken = result['response_time']
            print(f"{response}")
            print(f"   ⏱️ {time_taken:.2f}s")
        else:
            print(f"❌ {result['error']}")
    
    print(f"\n✅ Quick chat test completed!")

def main():
    """Main function"""
    print("🎯 Choose chat mode:")
    print("1. Interactive Chat")
    print("2. Quick Test")
    
    choice = input("\nEnter choice (1-2): ").strip()
    
    if choice == "1":
        interactive_chat()
    elif choice == "2":
        quick_chat_test()
    else:
        print("Invalid choice! Starting interactive chat...")
        interactive_chat()

if __name__ == "__main__":
    main()
