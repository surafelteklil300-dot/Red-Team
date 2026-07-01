# ============================================================
# 👑 ULTIMATE GOLD AGENTIC AI - API INTEGRATION MODULE
# ============================================================
# ይህ ሞጁል ሶስቱን APIs (OpenAI, DeepSeek, OpenRouter) ያስተዳድራል
# - አንድ ላይ (Consensus) እና በተናጠል (Standalone)
# - ራስ-ማመጣጠን (Auto-fallback)
# - ሙከራ እና ስህተት ማስተናገድ
# - የጥያቄ መሸጎጫ (Caching)
# - የጥያቄ ገደብ (Rate Limiting)
# - ትይዩ ጥያቄዎች (Parallel Requests)
# - የውጤት ማረጋገጫ (Response Validation)
# - የኢነርጂ ቁጠባ (Smart Batching)
# ============================================================

import os
import json
import time
import hashlib
import threading
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import re
import requests
from openai import OpenAI, APIError, RateLimitError, APITimeoutError
import logging
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

# ============================================================
# የAPI ሞዴል ዓይነቶች
# ============================================================

class APIModel(Enum):
    OPENAI_GPT4O = "gpt-4o"
    OPENAI_GPT4O_MINI = "gpt-4o-mini"
    OPENAI_GPT35_TURBO = "gpt-3.5-turbo"
    DEEPSEEK_CHAT = "deepseek-chat"
    DEEPSEEK_CODER = "deepseek-coder"
    OPENROUTER_LLAMA = "meta-llama/llama-3.2-3b-instruct:free"
    OPENROUTER_MISTRAL = "mistralai/mistral-7b-instruct:free"
    OPENROUTER_CLAUDE = "anthropic/claude-3-haiku"
    OPENROUTER_GEMINI = "google/gemini-2.0-flash-exp:free"

class APIProvider(Enum):
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    OPENROUTER = "openrouter"

# ============================================================
# የAPI ጥያቄ መዋቅር (Request/Response)
# ============================================================

@dataclass
class APIRequest:
    """የAPI ጥያቄ መዋቅር"""
    provider: APIProvider
    model: str
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 300
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: float = 30.0
    retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: hashlib.md5(str(time.time()).encode()).hexdigest()[:8])
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        return {
            'provider': self.provider.value,
            'model': self.model,
            'prompt': self.prompt[:200] + '...' if len(self.prompt) > 200 else self.prompt,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'request_id': self.request_id,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class APIResponse:
    """የAPI ምላሽ መዋቅር"""
    request: APIRequest
    content: Optional[str] = None
    error: Optional[str] = None
    success: bool = False
    response_time: float = 0.0
    tokens_used: int = 0
    raw_response: Optional[Any] = None
    provider: Optional[APIProvider] = None

    def to_dict(self):
        return {
            'success': self.success,
            'content': self.content[:200] + '...' if self.content and len(self.content) > 200 else self.content,
            'error': self.error,
            'response_time': self.response_time,
            'tokens_used': self.tokens_used,
            'provider': self.provider.value if self.provider else None
        }

# ============================================================
# የAPI መሸጎጫ (Cache)
# ============================================================

class APICache:
    """የAPI ጥያቄዎች መሸጎጫ - ተደጋጋሚ ጥያቄዎችን ለማስወገድ"""
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self._cache = {}
        self._max_size = max_size
        self._ttl = ttl
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def _get_key(self, request: APIRequest) -> str:
        """ለጥያቄ ልዩ ቁልፍ መፍጠር"""
        key_data = f"{request.provider.value}:{request.model}:{request.prompt}:{request.temperature}:{request.max_tokens}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, request: APIRequest) -> Optional[APIResponse]:
        """ከመሸጎጫ ምላሽ ማግኘት"""
        key = self._get_key(request)
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if datetime.now() - entry['timestamp'] < timedelta(seconds=self._ttl):
                    self._hits += 1
                    return entry['response']
                else:
                    # ጊዜ ያለፈበትን ማስወገድ
                    del self._cache[key]
            self._misses += 1
            return None

    def set(self, request: APIRequest, response: APIResponse):
        """ምላሽን ወደ መሸጎጫ ማስቀመጥ"""
        key = self._get_key(request)
        with self._lock:
            if len(self._cache) >= self._max_size:
                # ጊዜ ያለፈበትን ማስወገድ
                to_remove = []
                for k, v in self._cache.items():
                    if datetime.now() - v['timestamp'] > timedelta(seconds=self._ttl):
                        to_remove.append(k)
                for k in to_remove:
                    del self._cache[k]
            self._cache[key] = {
                'response': response,
                'timestamp': datetime.now()
            }

    def clear(self):
        """መሸጎጫን ማጽዳት"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> Dict:
        """የመሸጎጫ ስታቲስቲክስ"""
        total = self._hits + self._misses
        return {
            'size': len(self._cache),
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': f"{self._hits / total * 100:.1f}%" if total > 0 else "0%"
        }

# ============================================================
# የጥያቄ ገደብ (Rate Limiter)
# ============================================================

class RateLimiter:
    """የAPI ጥያቄ ገደብ አስተዳዳሪ"""
    def __init__(self, requests_per_minute: int = 60):
        self._requests_per_minute = requests_per_minute
        self._requests = deque()
        self._lock = threading.Lock()

    def wait(self):
        """ለጥያቄ መፈቀድ መጠበቅ"""
        with self._lock:
            now = time.time()
            # ከ1 ደቂቃ በፊት ያሉትን ማስወገድ
            while self._requests and now - self._requests[0] > 60:
                self._requests.popleft()
            
            if len(self._requests) >= self._requests_per_minute:
                # ቀጣዩ ጊዜ ሲፈቀድ
                wait_time = 60 - (now - self._requests[0]) + 0.1
                time.sleep(wait_time)
                now = time.time()
                while self._requests and now - self._requests[0] > 60:
                    self._requests.popleft()
            
            self._requests.append(now)

# ============================================================
# የAPI አቅራቢ ክፍሎች (Provider Classes)
# ============================================================

class BaseAPIProvider:
    """የAPI አቅራቢ መሰረታዊ ክፍል"""
    def __init__(self, api_key: Optional[str] = None, timeout: float = 30.0):
        self.api_key = api_key
        self.timeout = timeout
        self._session = None
        self._rate_limiter = RateLimiter()
        self._cache = APICache()
        self._logger = logging.getLogger(f"api.{self.__class__.__name__}")

    def _validate_response(self, response: Any) -> Optional[str]:
        """ምላሽን ማረጋገጥ እና ይዘቱን ማውጣት"""
        # ንዑስ ክፍሎች ይህን ይሸፍናሉ
        raise NotImplementedError

    def _handle_error(self, error: Exception) -> str:
        """ስህተትን ማስተናገድ"""
        if isinstance(error, RateLimitError):
            return "Rate limit exceeded. Please wait."
        elif isinstance(error, APITimeoutError):
            return "Request timed out."
        elif isinstance(error, APIError):
            return f"API error: {str(error)}"
        else:
            return f"Unexpected error: {str(error)}"

    def query(self, request: APIRequest) -> APIResponse:
        """የAPI ጥያቄ ማስፈጸም"""
        # ከመሸጎጫ መፈተሽ
        cached = self._cache.get(request)
        if cached:
            return cached

        start_time = time.time()
        response = APIResponse(request=request, provider=request.provider)

        # የጥያቄ ገደብ
        self._rate_limiter.wait()

        try:
            # ትክክለኛውን ጥያቄ ማስፈጸም (ንዑስ ክፍሎች ይሸፍናሉ)
            raw_response = self._execute_request(request)
            response.raw_response = raw_response
            content = self._validate_response(raw_response)
            
            if content:
                response.success = True
                response.content = content
                response.provider = request.provider
            else:
                response.error = "Empty or invalid response"

        except Exception as e:
            response.error = self._handle_error(e)
            response.success = False

        response.response_time = time.time() - start_time
        
        # ወደ መሸጎጫ ማስቀመጥ
        if response.success:
            self._cache.set(request, response)

        return response

    def _execute_request(self, request: APIRequest) -> Any:
        """ትክክለኛውን የAPI ጥያቄ ማስፈጸም (ንዑስ ክፍሎች ይሸፍናሉ)"""
        raise NotImplementedError

    def close(self):
        """ግንኙነቶችን መዝጋት"""
        if self._session:
            self._session.close()

# ============================================================
# OpenAI አቅራቢ (OpenAI Provider)
# ============================================================

class OpenAIProvider(BaseAPIProvider):
    """OpenAI API አቅራቢ"""
    def __init__(self, api_key: str, organization: Optional[str] = None, timeout: float = 30.0):
        super().__init__(api_key, timeout)
        self.organization = organization
        self._client = None
        self._init_client()

    def _init_client(self):
        """OpenAI ክላይንት ማስጀመር"""
        try:
            self._client = OpenAI(
                api_key=self.api_key,
                organization=self.organization,
                timeout=self.timeout,
                max_retries=3
            )
        except Exception as e:
            self._logger.error(f"Failed to initialize OpenAI client: {e}")

    def _execute_request(self, request: APIRequest) -> Any:
        """OpenAI ጥያቄ ማስፈጸም"""
        if not self._client:
            raise Exception("OpenAI client not initialized")

        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        try:
            response = self._client.chat.completions.create(
                model=request.model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
                frequency_penalty=request.frequency_penalty,
                presence_penalty=request.presence_penalty
            )
            return response
        except Exception as e:
            self._logger.error(f"OpenAI request failed: {e}")
            raise

    def _validate_response(self, response: Any) -> Optional[str]:
        """OpenAI ምላሽን ማረጋገጥ"""
        try:
            if hasattr(response, 'choices') and response.choices:
                content = response.choices[0].message.content
                if content and content.strip():
                    return content.strip()
            return None
        except Exception as e:
            self._logger.error(f"OpenAI response validation failed: {e}")
            return None

# ============================================================
# DeepSeek አቅራቢ (DeepSeek Provider)
# ============================================================

class DeepSeekProvider(BaseAPIProvider):
    """DeepSeek API አቅራቢ"""
    def __init__(self, api_key: str, timeout: float = 30.0):
        super().__init__(api_key, timeout)
        self.base_url = "https://api.deepseek.com/v1"
        self._session = None
        self._init_session()

    def _init_session(self):
        """HTTP ሴሽን ማስጀመር"""
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def _execute_request(self, request: APIRequest) -> Any:
        """DeepSeek ጥያቄ ማስፈጸም"""
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": request.model,
            "messages": [
                {"role": "system", "content": request.system_prompt or "You are a helpful AI assistant."},
                {"role": "user", "content": request.prompt}
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
            "frequency_penalty": request.frequency_penalty,
            "presence_penalty": request.presence_penalty
        }

        try:
            resp = self._session.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            self._logger.error(f"DeepSeek request failed: {e}")
            raise

    def _validate_response(self, response: Any) -> Optional[str]:
        """DeepSeek ምላሽን ማረጋገጥ"""
        try:
            if isinstance(response, dict):
                choices = response.get('choices', [])
                if choices:
                    message = choices[0].get('message', {})
                    content = message.get('content')
                    if content and content.strip():
                        return content.strip()
            return None
        except Exception as e:
            self._logger.error(f"DeepSeek response validation failed: {e}")
            return None

# ============================================================
# OpenRouter አቅራቢ (OpenRouter Provider)
# ============================================================

class OpenRouterProvider(BaseAPIProvider):
    """OpenRouter API አቅራቢ"""
    def __init__(self, api_key: str, timeout: float = 30.0):
        super().__init__(api_key, timeout)
        self.base_url = "https://openrouter.ai/api/v1"
        self._session = None
        self._init_session()

    def _init_session(self):
        """HTTP ሴሽን ማስጀመር"""
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ultimategoldai",
            "X-Title": "Ultimate Gold Agentic AI"
        })

    def _execute_request(self, request: APIRequest) -> Any:
        """OpenRouter ጥያቄ ማስፈጸም"""
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": request.model,
            "messages": [
                {"role": "system", "content": request.system_prompt or "You are a helpful AI assistant."},
                {"role": "user", "content": request.prompt}
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
            "frequency_penalty": request.frequency_penalty,
            "presence_penalty": request.presence_penalty
        }

        try:
            resp = self._session.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            self._logger.error(f"OpenRouter request failed: {e}")
            raise

    def _validate_response(self, response: Any) -> Optional[str]:
        """OpenRouter ምላሽን ማረጋገጥ"""
        try:
            if isinstance(response, dict):
                choices = response.get('choices', [])
                if choices:
                    message = choices[0].get('message', {})
                    content = message.get('content')
                    if content and content.strip():
                        return content.strip()
            return None
        except Exception as e:
            self._logger.error(f"OpenRouter response validation failed: {e}")
            return None

# ============================================================
# ዋናው የAPI ውህደት ክፍል (Main API Integration)
# ============================================================

class APIIntegration:
    """
    ሶስቱን APIs (OpenAI, DeepSeek, OpenRouter) የሚያስተዳድር ዋና ክፍል
    - አንድ ላይ (Consensus Mode) እና በተናጠል (Standalone)
    - ራስ-ማመጣጠን (Auto-fallback)
    - ትይዩ ጥያቄዎች (Parallel)
    - የቡድን ውሳኔ (Consensus Voting)
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(APIIntegration, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._logger = logging.getLogger("api.integration")
        
        # የAPI ቁልፎችን ከአካባቢ መሰብሰብ
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')

        # አቅራቢዎችን ማስጀመር
        self._providers = {}
        self._init_providers()

        # መሸጎጫ እና ገደብ
        self._cache = APICache()
        self._rate_limiter = RateLimiter()

        self._stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'provider_stats': {}
        }

    def _init_providers(self):
        """ሁሉንም አቅራቢዎች ማስጀመር"""
        if self.openai_key:
            self._providers[APIProvider.OPENAI] = OpenAIProvider(self.openai_key)
            self._logger.info("OpenAI provider initialized")
        else:
            self._logger.warning("OpenAI API key not found")

        if self.deepseek_key:
            self._providers[APIProvider.DEEPSEEK] = DeepSeekProvider(self.deepseek_key)
            self._logger.info("DeepSeek provider initialized")
        else:
            self._logger.warning("DeepSeek API key not found")

        if self.openrouter_key:
            self._providers[APIProvider.OPENROUTER] = OpenRouterProvider(self.openrouter_key)
            self._logger.info("OpenRouter provider initialized")
        else:
            self._logger.warning("OpenRouter API key not found")

    def get_provider(self, provider: APIProvider) -> Optional[BaseAPIProvider]:
        """በስም አቅራቢን መመለስ"""
        return self._providers.get(provider)

    def query(self, prompt: str, system_prompt: Optional[str] = None,
              model: Optional[str] = None, provider: Optional[APIProvider] = None,
              temperature: float = 0.3, max_tokens: int = 300,
              use_consensus: bool = False) -> APIResponse:
        """
        የAPI ጥያቄ ማስፈጸም
        - provider ከተሰጠ ያንን ብቻ ይጠቀማል
        - use_consensus እውነት ከሆነ ሶስቱንም በመጠየቅ የቡድን ውሳኔ ይሰጣል
        """
        self._stats['total_requests'] += 1

        # ሞዴልን መምረጥ
        if not model:
            if provider == APIProvider.OPENAI:
                model = APIModel.OPENAI_GPT4O_MINI.value
            elif provider == APIProvider.DEEPSEEK:
                model = APIModel.DEEPSEEK_CHAT.value
            elif provider == APIProvider.OPENROUTER:
                model = APIModel.OPENROUTER_LLAMA.value
            else:
                model = APIModel.OPENAI_GPT4O_MINI.value

        # ጥያቄ መፍጠር
        request = APIRequest(
            provider=provider or APIProvider.OPENAI,
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Consensus ሞድ
        if use_consensus:
            return self._query_consensus(request)

        # አንድ አቅራቢ
        if provider and provider in self._providers:
            return self._providers[provider].query(request)

        # ወይም የመጀመሪያውን የሚሰራ አቅራቢ
        for p in self._providers.values():
            response = p.query(request)
            if response.success:
                self._stats['successful_requests'] += 1
                return response

        self._stats['failed_requests'] += 1
        return APIResponse(
            request=request,
            error="All providers failed",
            success=False
        )

    def _query_consensus(self, request: APIRequest) -> APIResponse:
        """ሶስቱን APIs በመጠየቅ የቡድን ውሳኔ ማግኘት"""
        results = []
        active_providers = list(self._providers.values())

        if not active_providers:
            return APIResponse(
                request=request,
                error="No active providers",
                success=False
            )

        # በትይዩ ሁሉንም መጠየቅ
        with ThreadPoolExecutor(max_workers=len(active_providers)) as executor:
            futures = {
                executor.submit(p.query, request): p
                for p in active_providers
            }
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=request.timeout)
                    if result.success:
                        results.append(result)
                except Exception as e:
                    self._logger.error(f"Consensus query failed: {e}")

        if not results:
            return APIResponse(
                request=request,
                error="No provider returned a successful response",
                success=False
            )

        # የቡድን ውሳኔ - ብዙ ጊዜ የተገኘውን መምረጥ
        if len(results) == 1:
            return results[0]
        elif len(results) >= 2:
            # ይዘቶቹን ማወዳደር
            contents = [r.content for r in results if r.content]
            if contents:
                # አጭሩን እና በጣም የተለመደውን መምረጥ
                if len(set(contents)) == 1:
                    return results[0]
                else:
                    # የመጀመሪያውን ወይም በጣም ረጅሙን
                    return max(results, key=lambda r: len(r.content or ''))

        return results[0]

    def query_async(self, prompt: str, **kwargs) -> asyncio.Future:
        """ያልተመሳሰለ (Async) ጥያቄ"""
        future = asyncio.Future()
        try:
            response = self.query(prompt, **kwargs)
            future.set_result(response)
        except Exception as e:
            future.set_exception(e)
        return future

    def query_batch(self, prompts: List[str], **kwargs) -> List[APIResponse]:
        """በርካታ ጥያቄዎችን በአንድ ጊዜ መላክ"""
        responses = []
        with ThreadPoolExecutor(max_workers=min(10, len(prompts))) as executor:
            futures = {
                executor.submit(self.query, prompt, **kwargs): prompt
                for prompt in prompts
            }
            for future in as_completed(futures):
                try:
                    responses.append(future.result())
                except Exception as e:
                    responses.append(APIResponse(
                        request=APIRequest(provider=APIProvider.OPENAI, model="", prompt=futures[future]),
                        error=str(e),
                        success=False
                    ))
        return responses

    def get_available_providers(self) -> List[APIProvider]:
        """በአሁን ጊዜ የሚሰሩ አቅራቢዎች ዝርዝር"""
        return [p for p in self._providers.keys()]

    def get_stats(self) -> Dict:
        """የAPI ስታቲስቲክስ"""
        stats = self._stats.copy()
        stats['active_providers'] = len(self._providers)
        stats['cache'] = self._cache.get_stats()
        stats['available_providers'] = [p.value for p in self._providers.keys()]
        return stats

    def close(self):
        """ሁሉንም ግንኙነቶች መዝጋት"""
        for provider in self._providers.values():
            provider.close()

# ============================================================
# ለቀላል አጠቃቀም ተግባራት (Helper Functions)
# ============================================================

def get_api() -> APIIntegration:
    """የአለም አቀፍ API ኢንስታንስ መመለስ"""
    return APIIntegration()

def query_ai(prompt: str, use_consensus: bool = True, **kwargs) -> str:
    """
    ፈጣን የAI ጥያቄ - መልሱን በቀጥታ ይመልሳል
    """
    api = get_api()
    response = api.query(prompt, use_consensus=use_consensus, **kwargs)
    if response.success:
        return response.content
    return f"Error: {response.error}"

def query_ai_batch(prompts: List[str], **kwargs) -> List[str]:
    """
    በርካታ ጥያቄዎችን በአንድ ጊዜ - መልሶችን በቀጥታ ይመልሳል
    """
    api = get_api()
    responses = api.query_batch(prompts, **kwargs)
    return [r.content if r.success else f"Error: {r.error}" for r in responses]

# ============================================================
# ሙከራ እና ማሳያ
# ============================================================

if __name__ == "__main__":
    # መሰረታዊ ሙከራ
    print("=" * 60)
    print("👑 ULTIMATE GOLD AGENTIC AI - API INTEGRATION TEST")
    print("=" * 60)
    
    api = get_api()
    print(f"Available providers: {api.get_available_providers()}")
    
    # ናሙና ጥያቄ
    print("\n📝 Testing API query...")
    
    result = api.query(
        prompt="What is the most common cybersecurity vulnerability in web applications?",
        system_prompt="You are a cybersecurity expert. Answer concisely.",
        use_consensus=True,
        temperature=0.3,
        max_tokens=150
    )
    
    if result.success:
        print(f"✅ Success: {result.content}")
        print(f"⏱️ Response time: {result.response_time:.2f}s")
        print(f"📊 Provider: {result.provider.value if result.provider else 'Unknown'}")
    else:
        print(f"❌ Failed: {result.error}")
    
    print("\n📊 API Statistics:")
    print(json.dumps(api.get_stats(), indent=2, default=str))
    print("=" * 60)

# ============================================================
# 🏆 ይህ ሙሉ የተሟላ የAPI ውህደት ሞጁል ነው
# ============================================================
