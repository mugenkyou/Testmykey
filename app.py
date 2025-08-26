from flask import Flask, render_template, request, jsonify, url_for
import requests
from openai import OpenAI
from requests.exceptions import ConnectionError, Timeout, RequestException
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from base64 import b64encode

# Load environment variables
load_dotenv()

app = Flask(__name__)

def handle_request_error(e: Exception) -> dict:
    """Handle common request errors with user-friendly messages"""
    error_str = str(e).lower()
    
    if "proxy" in error_str or "proxies" in error_str:
        return {"status": "invalid", "message": "API Key Invalid"}
    elif "invalid" in error_str or "incorrect" in error_str:
        return {"status": "invalid", "message": "API Key Invalid"}
    elif "expired" in error_str:
        return {"status": "invalid", "message": "API Key Inactive"}
    elif isinstance(e, ConnectionError):
        return {"status": "error", "message": "Connection Error"}
    elif isinstance(e, Timeout):
        return {"status": "error", "message": "Timeout Error"}
    return {"status": "invalid", "message": "API Key Invalid"}

def check_gemini(api_key: str) -> dict:
    """Validate Google Gemini API key"""
    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Try a simple generation to verify the key
        model = genai.GenerativeModel('gemini-1.5-flash')  # Updated to current model
        response = model.generate_content("Test", generation_config=genai.types.GenerationConfig(
            max_output_tokens=10,
            temperature=0.1,
        ))
        
        if response and hasattr(response, 'text') and response.text:
            return {"status": "valid", "message": "✅ API Key Active"}
        else:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
            
    except Exception as e:
        return handle_request_error(e)

def check_openai(api_key: str) -> dict:
    """Validate OpenAI API key"""
    try:
        client = OpenAI(api_key=api_key)
        models = client.models.list()
        if models and models.data:
            return {"status": "valid", "message": "API Key Active"}
        else:
            return {"status": "invalid", "message": "API Key Inactive"}
    except Exception as e:
        return handle_request_error(e)

def check_anthropic(api_key: str) -> dict:
    """Validate Anthropic Claude API key"""
    try:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        json_data = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 5,
            "messages": [{"role": "user", "content": "Hi"}]
        }
        response = requests.post(url, headers=headers, json=json_data, timeout=15)
        
        if response.status_code == 200:
            return {"status": "valid", "message": "✅ API Key Active"}
        elif response.status_code == 401:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
        elif response.status_code == 429:
            return {"status": "invalid", "message": "❌ API Key Rate Limited"}
        else:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
    except Exception as e:
        return handle_request_error(e)

def check_cohere(api_key: str) -> dict:
    """Validate Cohere API key"""
    try:
        url = "https://api.cohere.ai/v1/models"
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return {"status": "valid", "message": "✅ API Key Active"}
        elif response.status_code in [401, 403]:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
        elif response.status_code == 429:
            return {"status": "invalid", "message": "❌ API Key Rate Limited"}
        else:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
    except Exception as e:
        return handle_request_error(e)

def check_stripe(secret_key: str) -> dict:
    """Validate Stripe API key"""
    try:
        url = "https://api.stripe.com/v1/customers"
        params = {"limit": 1}  # Limit to 1 to minimize API usage
        response = requests.get(url, auth=(secret_key, ''), params=params, timeout=15)
        
        if response.status_code == 200:
            return {"status": "valid", "message": "✅ API Key Active"}
        elif response.status_code == 401:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
        elif response.status_code == 429:
            return {"status": "invalid", "message": "❌ API Key Rate Limited"}
        else:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
    except Exception as e:
        return handle_request_error(e)

def check_github(token: str) -> dict:
    """Validate GitHub API token"""
    try:
        url = "https://api.github.com/user"
        headers = {"Authorization": f"Bearer {token}"}  # Updated to Bearer token
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return {"status": "valid", "message": "✅ API Key Active"}
        elif response.status_code in [401, 403]:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
        elif response.status_code == 429:
            return {"status": "invalid", "message": "❌ API Key Rate Limited"}
        else:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
    except Exception as e:
        return handle_request_error(e)

def check_notion(token: str) -> dict:
    """Validate Notion API token"""
    try:
        url = "https://api.notion.com/v1/users/me"
        headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28"
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return {"status": "valid", "message": "✅ API Key Active"}
        elif response.status_code in [401, 403]:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
        elif response.status_code == 429:
            return {"status": "invalid", "message": "❌ API Key Rate Limited"}
        else:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
    except Exception as e:
        return handle_request_error(e)

def check_firebase(api_key: str) -> dict:
    """Validate Firebase API key"""
    try:
        # Using Firebase Auth REST API to verify the API key
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
        headers = {"Content-Type": "application/json"}
        data = {"returnSecureToken": True}
        
        response = requests.post(url, headers=headers, json=data, timeout=15)
        
        if response.status_code == 400:  # Expected error for invalid signup but valid key
            error_data = response.json()
            if "INVALID_API_KEY" in str(error_data):
                return {"status": "invalid", "message": "❌ API Key Invalid"}
            return {"status": "valid", "message": "✅ API Key Active"}
        elif response.status_code == 403:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
        else:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
    except Exception as e:
        return handle_request_error(e)

def check_twitter(api_key: str, api_secret: str = None) -> dict:
    """Validate Twitter API credentials"""
    try:
        if not api_secret:
            return {"status": "invalid", "message": "❌ API Key Invalid - Twitter Secret Required"}
            
        # Get OAuth 2.0 Bearer Token
        auth_url = "https://api.twitter.com/oauth2/token"
        auth_headers = {
            "Authorization": f"Basic {b64encode(f'{api_key}:{api_secret}'.encode()).decode()}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        auth_data = "grant_type=client_credentials"
        
        response = requests.post(auth_url, headers=auth_headers, data=auth_data, timeout=15)
        
        if response.status_code == 200:
            return {"status": "valid", "message": "✅ API Key Active"}
        elif response.status_code in [401, 403]:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
        elif response.status_code == 429:
            return {"status": "invalid", "message": "❌ API Key Rate Limited"}
        else:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
    except Exception as e:
        return handle_request_error(e)

def check_spotify(client_id: str, client_secret: str = None) -> dict:
    """Validate Spotify API credentials"""
    try:
        if not client_secret:
            return {"status": "invalid", "message": "❌ API Key Invalid - Spotify Secret Required"}
            
        # Get OAuth 2.0 access token
        auth_url = "https://accounts.spotify.com/api/token"
        auth_headers = {
            "Authorization": f"Basic {b64encode(f'{client_id}:{client_secret}'.encode()).decode()}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        auth_data = "grant_type=client_credentials"
        
        response = requests.post(auth_url, headers=auth_headers, data=auth_data, timeout=15)
        
        if response.status_code == 200:
            return {"status": "valid", "message": "✅ API Key Active"}
        elif response.status_code in [401, 403]:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
        elif response.status_code == 429:
            return {"status": "invalid", "message": "❌ API Key Rate Limited"}
        else:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
    except Exception as e:
        return handle_request_error(e)

def check_azure(client_id: str, client_secret: str = None, tenant_id: str = None) -> dict:
    """Validate Azure API credentials"""
    try:
        if not client_secret or not tenant_id:
            return {"status": "invalid", "message": "❌ API Key Invalid - Azure Client Secret and Tenant ID Required"}
            
        # Get OAuth 2.0 access token
        auth_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://management.azure.com/.default"
        }
        
        response = requests.post(auth_url, data=auth_data, timeout=15)
        
        if response.status_code == 200:
            return {"status": "valid", "message": "✅ API Key Active"}
        elif response.status_code in [401, 403]:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
        elif response.status_code == 429:
            return {"status": "invalid", "message": "❌ API Key Rate Limited"}
        else:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
    except Exception as e:
        return handle_request_error(e)

def check_supabase(url: str, anon_key: str) -> dict:
    """Validate Supabase API credentials"""
    try:
        if not url:
            return {"status": "invalid", "message": "❌ API Key Invalid - Supabase URL Required"}
            
        # Try to access Supabase health check endpoint
        headers = {
            "apikey": anon_key,
            "Authorization": f"Bearer {anon_key}"
        }
        
        # Remove trailing slash if present
        base_url = url.rstrip('/')
        health_url = f"{base_url}/rest/v1/"
        
        response = requests.get(health_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return {"status": "valid", "message": "✅ API Key Active"}
        elif response.status_code in [401, 403]:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
        elif response.status_code == 429:
            return {"status": "invalid", "message": "❌ API Key Rate Limited"}
        else:
            return {"status": "invalid", "message": "❌ API Key Invalid"}
    except Exception as e:
        return handle_request_error(e)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify():
    """Verify API key for selected service"""
    try:
        if request.is_json:
            data = request.get_json()
            api_key = data.get('api_key')
            service = data.get('service')
            api_secret = data.get('api_secret')
            client_secret = data.get('client_secret')
            tenant_id = data.get('tenant_id')
            supabase_url = data.get('supabase_url')
        else:
            api_key = request.form.get('api_key')
            service = request.form.get('service')
            api_secret = request.form.get('api_secret')
            client_secret = request.form.get('client_secret')
            tenant_id = request.form.get('tenant_id')
            supabase_url = request.form.get('supabase_url')
        
        if not api_key or not service:
            return jsonify({
                "status": "error", 
                "message": "API Key Required"
            })
        
        # Strip whitespace from credentials
        api_key = api_key.strip()
        api_secret = api_secret.strip() if api_secret else None
        client_secret = client_secret.strip() if client_secret else None
        tenant_id = tenant_id.strip() if tenant_id else None
        supabase_url = supabase_url.strip() if supabase_url else None
        
        verification_functions = {
            'openai': check_openai,
            'anthropic': check_anthropic,
            'cohere': check_cohere,
            'stripe': check_stripe,
            'github': check_github,
            'notion': check_notion,
            'gemini': check_gemini,
            'firebase': check_firebase,
            'twitter': lambda k: check_twitter(k, api_secret),
            'spotify': lambda k: check_spotify(k, client_secret),
            'azure': lambda k: check_azure(k, client_secret, tenant_id),
            'supabase': lambda k: check_supabase(supabase_url, k)
        }
        
        verify_function = verification_functions.get(service.lower())
        if not verify_function:
            return jsonify({
                "status": "error", 
                "message": "Invalid Service"
            })
        
        result = verify_function(api_key)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Server Error"
        })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "API Key Validator is running"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)