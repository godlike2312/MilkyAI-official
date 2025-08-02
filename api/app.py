from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import requests
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
import time
from datetime import datetime
import re

app = Flask(__name__)
CORS(app)

# Initialize Firebase Admin SDK
try:
    # Use service account key if available, otherwise use default credentials
    if os.path.exists('serviceAccountKey.json'):
        cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(cred)
    else:
        firebase_admin.initialize_app()
    db = firestore.client()
    print("Firebase Admin SDK initialized successfully")
except Exception as e:
    print(f"Firebase initialization error: {e}")
    db = None

# Model configurations
MODEL_OPTIONS = {
    'deepseek/deepseek-chat-v3-0324:free': {
        'name': 'GPT-4o',
        'provider': 'openrouter',
        'supports_deep_thinking': True
    },
    'mistralai/mistral-7b-instruct:free': {
        'name': 'Milky Basic',
        'provider': 'openrouter',
        'supports_deep_thinking': True
    },
    'google/gemma-3n-e4b-it:free': {
        'name': 'Milky-S1',
        'provider': 'openrouter',
        'supports_deep_thinking': True
    },
    'agentica-org/deepcoder-14b-preview:free': {
        'name': 'MilkyCoder Pro',
        'provider': 'openrouter',
        'supports_deep_thinking': True
    },
    'deepseek/deepseek-v3-base:free': {
        'name': 'Milky 3.7 sonnet',
        'provider': 'openrouter',
        'supports_deep_thinking': True
    },
    'groq/llama3-70b': {
        'name': 'Milky Edge',
        'provider': 'groq',
        'supports_deep_thinking': True
    },
    'cohere/command-r-plus': {
        'name': 'Milky S2',
        'provider': 'openrouter',
        'supports_deep_thinking': True
    },
    'cohere/command-r': {
        'name': 'Milky 2o',
        'provider': 'openrouter',
        'supports_deep_thinking': True
    },
    'anthropic/claude-3-5-sonnet': {
        'name': 'Claude 3.5 Sonnet',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'meta-llama/llama-3.1-8b-instruct': {
        'name': 'Llama 3.1 8B',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'meta-llama/llama-3.1-70b-instruct': {
        'name': 'Llama 3.1 70B',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'openai/gpt-4o-mini': {
        'name': 'GPT-4o Mini',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'openai/gpt-4o': {
        'name': 'GPT-4o',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'anthropic/claude-3-5-haiku': {
        'name': 'Claude 3.5 Haiku',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'anthropic/claude-3-opus': {
        'name': 'Claude 3 Opus',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'google/gemma-2-27b-it': {
        'name': 'Gemma 2 27B',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'meta-llama/llama-3.1-405b-instruct': {
        'name': 'Llama 3.1 405B',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'openai/gpt-4-turbo': {
        'name': 'GPT-4 Turbo',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'anthropic/claude-3-sonnet': {
        'name': 'Claude 3 Sonnet',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'meta-llama/llama-3.1-405b-instruct:free': {
        'name': 'Llama 3.1 405B (Free)',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'openai/gpt-4o-mini:free': {
        'name': 'GPT-4o Mini (Free)',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'anthropic/claude-3-5-sonnet:free': {
        'name': 'Claude 3.5 Sonnet (Free)',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'meta-llama/llama-3.1-8b-instruct:free': {
        'name': 'Llama 3.1 8B (Free)',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'openai/gpt-4o:free': {
        'name': 'GPT-4o (Free)',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'anthropic/claude-3-5-haiku:free': {
        'name': 'Claude 3.5 Haiku (Free)',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'anthropic/claude-3-opus:free': {
        'name': 'Claude 3 Opus (Free)',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'google/gemma-2-27b-it:free': {
        'name': 'Gemma 2 27B (Free)',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'openai/gpt-4-turbo:free': {
        'name': 'GPT-4 Turbo (Free)',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    },
    'anthropic/claude-3-sonnet:free': {
        'name': 'Claude 3 Sonnet (Free)',
        'provider': 'openrouter',
        'supports_deep_thinking': False
    }
}

# Deep thinking prompt
DEEP_THINKING_PROMPT = """You are an AI assistant with deep thinking capabilities. When the user enables deep thinking mode, you MUST follow these critical rules:

CRITICAL RULES:
1. MUST ALWAYS include BOTH breakdown AND final answer
2. MUST ALWAYS use exact headers: "**DEEP THINKING BREAKDOWN**" and "**FINAL ANSWER**" (NO EMOJIS)
3. MUST ALWAYS separate sections with "---"
4. MUST NEVER skip final answer
5. Response MUST end with final answer
6. Thought process must be natural and conversational
7. Use specific phrases like "Hmm, the user wants...", "Let me think...", "What if..."
8. Thinking process must be detailed and thorough
9. If incomplete, still include both sections
10. Always analyze user request first
11. DO NOT use emojis in headers

When deep thinking is enabled, structure your response like this:

[FIRST: Analyze the user's request]
Hmm, the user wants me to... Let me understand what they're asking for...

[SECOND: Think through the problem step by step]
Let me think about this systematically. First, I need to consider...
What if I approach this from a different angle?...

[THIRD: Consider different approaches]
I could try this approach... Or maybe that would work better...

[FOURTH: Plan the solution]
Based on my analysis, I think the best approach is...

[FIFTH: Synthesize the final answer]
Now let me put this all together...

**DEEP THINKING BREAKDOWN**
[Your detailed thought process here - be natural and conversational]

---

**FINAL ANSWER**
[Your final, complete answer here]

Remember: ALWAYS include both sections, use exact headers, separate with "---", and end with the final answer."""

def get_system_prompt(model_info, deep_thinking_mode=False):
    """Get the appropriate system prompt based on model and deep thinking mode"""
    base_prompt = f"""You are {model_info['name']}, a helpful AI assistant. You are part of MilkyAI, a comprehensive AI platform.

Key capabilities:
- You can help with coding, analysis, writing, and problem-solving
- You provide clear, accurate, and helpful responses
- You can handle complex tasks and break them down when needed
- You are knowledgeable about various topics and technologies

Guidelines:
- Be helpful, accurate, and concise
- If you're unsure about something, say so
- For coding tasks, provide clear explanations
- Use markdown formatting when appropriate
- Be conversational and engaging"""

    if deep_thinking_mode and model_info.get('supports_deep_thinking', False):
        return base_prompt + "\n\n" + DEEP_THINKING_PROMPT
    else:
        return base_prompt

def verify_token(token):
    """Verify Firebase ID token"""
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        print(f"Token verification error: {e}")
        return None

def save_message_to_chat(chat_id, message_data):
    """Save a message to Firestore"""
    try:
        if db:
            chat_ref = db.collection('chats').document(chat_id)
            chat_ref.collection('messages').add(message_data)
            print(f"Message saved to chat {chat_id}")
        else:
            print("Firestore not available, skipping message save")
    except Exception as e:
        print(f"Error saving message: {e}")

def create_chat_session(user_id, title="New Chat"):
    """Create a new chat session in Firestore"""
    try:
        if db:
            chat_data = {
                'userId': user_id,
                'title': title,
                'createdAt': firestore.FieldValue.serverTimestamp(),
                'updatedAt': firestore.FieldValue.serverTimestamp()
            }
            chat_ref = db.collection('chats').add(chat_data)
            return chat_ref[1].id
        else:
            print("Firestore not available, skipping chat creation")
            return None
    except Exception as e:
        print(f"Error creating chat session: {e}")
        return None

def get_chat_messages(chat_id):
    """Get all messages for a chat from Firestore"""
    try:
        if db:
            messages = []
            chat_ref = db.collection('chats').document(chat_id)
            messages_ref = chat_ref.collection('messages').order_by('timestamp')
            
            for doc in messages_ref.stream():
                messages.append({
                    'id': doc.id,
                    'role': doc.get('role'),
                    'content': doc.get('content'),
                    'timestamp': doc.get('timestamp')
                })
            return messages
        else:
            print("Firestore not available, returning empty messages")
            return []
    except Exception as e:
        print(f"Error getting chat messages: {e}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        model = data.get('model', 'deepseek/deepseek-chat-v3-0324:free')
        chat_history = data.get('chatHistory', [])
        deep_thinking_mode = data.get('deepThinkingMode', False)
        
        # Get user ID from Authorization header
        user_id = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
            user_id = verify_token(token)
        
        # Get model info
        model_info = MODEL_OPTIONS.get(model, MODEL_OPTIONS['deepseek/deepseek-chat-v3-0324:free'])
        
        # Get system prompt
        system_prompt = get_system_prompt(model_info, deep_thinking_mode)
        
        # Prepare messages for API
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add chat history
        for msg in chat_history:
            if msg.get('role') and msg.get('content'):
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Choose API based on model provider
        provider = model_info.get('provider', 'openrouter')
        
        if provider == 'groq':
            # Use Groq API
            groq_api_key = os.getenv('GROQ_API_KEY')
            if not groq_api_key:
                return jsonify({'error': 'Groq API key not configured'}), 500
            
            headers = {
                'Authorization': f'Bearer {groq_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': model,
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': 4000
            }
            
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=60
            )
        else:
            # Use OpenRouter API
            openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
            if not openrouter_api_key:
                return jsonify({'error': 'OpenRouter API key not configured'}), 500
            
            headers = {
                'Authorization': f'Bearer {openrouter_api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://milkyai.com',
                'X-Title': 'MilkyAI'
            }
            
            payload = {
                'model': model,
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': 4000
            }
            
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=60
            )
        
        if response.status_code == 200:
            response_data = response.json()
            ai_response = response_data['choices'][0]['message']['content']
            
            # Save message to Firestore if user is authenticated
            if user_id:
                # Get or create chat session
                chat_id = data.get('chatId')
                if not chat_id:
                    chat_id = create_chat_session(user_id)
                
                if chat_id:
                    # Save user message
                    user_message_data = {
                        'role': 'user',
                        'content': message,
                        'timestamp': firestore.FieldValue.serverTimestamp()
                    }
                    save_message_to_chat(chat_id, user_message_data)
                    
                    # Save AI response
                    ai_message_data = {
                        'role': 'assistant',
                        'content': ai_response,
                        'timestamp': firestore.FieldValue.serverTimestamp()
                    }
                    save_message_to_chat(chat_id, ai_message_data)
            
            return jsonify({
                'response': ai_response,
                'chatId': chat_id if user_id else None
            })
        else:
            error_msg = f"API Error: {response.status_code}"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_msg = f"API Error: {error_data['error'].get('message', 'Unknown error')}"
            except:
                pass
            return jsonify({'error': error_msg}), response.status_code
            
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available models"""
    return jsonify(MODEL_OPTIONS)

@app.route('/api/chats', methods=['GET'])
def get_user_chats():
    """Get all chats for the authenticated user"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No valid authorization token'}), 401
        
        token = auth_header[7:]
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        chats = []
        chats_ref = db.collection('chats').where('userId', '==', user_id).order_by('updatedAt', direction=firestore.Query.DESCENDING)
        
        for doc in chats_ref.stream():
            chat_data = doc.to_dict()
            chats.append({
                'id': doc.id,
                'title': chat_data.get('title', 'New Chat'),
                'createdAt': chat_data.get('createdAt'),
                'updatedAt': chat_data.get('updatedAt')
            })
        
        return jsonify(chats)
        
    except Exception as e:
        print(f"Error getting user chats: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/chats/<chat_id>/messages', methods=['GET'])
def get_chat_messages_endpoint(chat_id):
    """Get all messages for a specific chat"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No valid authorization token'}), 401
        
        token = auth_header[7:]
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        
        messages = get_chat_messages(chat_id)
        return jsonify(messages)
        
    except Exception as e:
        print(f"Error getting chat messages: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/chats/<chat_id>', methods=['PUT'])
def update_chat_title(chat_id):
    """Update chat title"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No valid authorization token'}), 401
        
        token = auth_header[7:]
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        
        data = request.json
        new_title = data.get('title', 'New Chat')
        
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        chat_ref = db.collection('chats').document(chat_id)
        chat_ref.update({
            'title': new_title,
            'updatedAt': firestore.FieldValue.serverTimestamp()
        })
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error updating chat title: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/chats/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """Delete a chat and all its messages"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No valid authorization token'}), 401
        
        token = auth_header[7:]
        user_id = verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        
        if not db:
            return jsonify({'error': 'Database not available'}), 500
        
        # Delete all messages in the chat
        chat_ref = db.collection('chats').document(chat_id)
        messages_ref = chat_ref.collection('messages')
        
        for doc in messages_ref.stream():
            doc.reference.delete()
        
        # Delete the chat document
        chat_ref.delete()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error deleting chat: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 