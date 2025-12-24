"""
Webscout Unified Client Interface

A unified client for webscout that provides a simple interface
to interact with multiple AI providers for chat completions and image generation.

Features:
- Automatic provider failover
- Support for specifying exact provider
- Intelligent model resolution (auto, provider/model, or model name)
- Caching of provider instances
- Full streaming support

Usage:
    # Chat completions
    from webscout.client import Client
    
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}],
    )
    print(response.choices[0].message.content)

    # Image generation
    from webscout.client import Client
    
    client = Client()
    response = client.images.generate(
        model="flux",
        prompt="a white siamese cat playing with a red ball",
        response_format="url"
    )
    print(response.data[0].url)
"""

import time
import uuid
import random
import inspect
import importlib
import pkgutil
import difflib
from typing import List, Dict, Optional, Union, Generator, Any, Type, Tuple, Set

# Import OPENAI providers and utilities
from webscout.Provider.OPENAI import *
from webscout.Provider.OPENAI.base import OpenAICompatibleProvider, BaseCompletions, BaseChat
from webscout.Provider.OPENAI.utils import (
    ChatCompletion, 
    ChatCompletionChunk, 
    Choice, 
    ChoiceDelta,
    ChatCompletionMessage, 
    CompletionUsage
)

# Import TTI providers and utilities
from webscout.Provider.TTI import *
from webscout.Provider.TTI.base import TTICompatibleProvider, BaseImages
from webscout.Provider.TTI.utils import ImageData, ImageResponse

def load_openai_providers() -> Tuple[Dict[str, Type[OpenAICompatibleProvider]], Set[str]]:
    """Dynamically loads all OpenAI-compatible provider classes."""
    provider_map = {}
    auth_required_providers = set()
    
    try:
        provider_package = importlib.import_module("webscout.Provider.OPENAI")
        for _, module_name, _ in pkgutil.iter_modules(provider_package.__path__):
            if module_name.startswith(('base', 'utils', 'pydantic', '__')):
                continue
            try:
                module = importlib.import_module(f"webscout.Provider.OPENAI.{module_name}")
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, OpenAICompatibleProvider) and 
                        attr != OpenAICompatibleProvider and
                        not attr_name.startswith(('Base', '_'))):
                        
                        provider_map[attr_name] = attr
                        # Authentication is determined solely by required_auth attribute
                        if hasattr(attr, 'required_auth') and attr.required_auth:
                            auth_required_providers.add(attr_name)
            except Exception: pass
    except Exception: pass
    return provider_map, auth_required_providers

def load_tti_providers() -> Tuple[Dict[str, Type[TTICompatibleProvider]], Set[str]]:
    """Dynamically loads all TTI provider classes."""
    provider_map = {}
    auth_required_providers = set()
    
    try:
        provider_package = importlib.import_module("webscout.Provider.TTI")
        for _, module_name, _ in pkgutil.iter_modules(provider_package.__path__):
            if module_name.startswith(('base', 'utils', '__')):
                continue
            try:
                module = importlib.import_module(f"webscout.Provider.TTI.{module_name}")
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, TTICompatibleProvider) and 
                        attr != TTICompatibleProvider and
                        not attr_name.startswith(('Base', '_'))):
                        
                        provider_map[attr_name] = attr
                        if hasattr(attr, 'required_auth') and attr.required_auth:
                            auth_required_providers.add(attr_name)
            except Exception: pass
    except Exception: pass
    return provider_map, auth_required_providers

OPENAI_PROVIDERS, OPENAI_AUTH_REQUIRED = load_openai_providers()
TTI_PROVIDERS, TTI_AUTH_REQUIRED = load_tti_providers()

def _get_models_safely(provider_cls: type, instance: Any = None) -> List[str]:
    """Safely get the list of available models from a provider using models.list().
    
    Always uses the standardized models.list() interface which providers implement.
    This ensures we get the most up-to-date model list, including dynamically fetched models.
    
    Args:
        provider_cls: The provider class
        instance: Optional pre-created instance. If None, will try to create one.
    
    Returns:
        List of model names as strings, or empty list if not available.
    """
    models = []
    
    # Get or create an instance to call models.list()
    try:
        if instance is None:
            # Try to create an instance
            try:
                instance = provider_cls()
            except Exception:
                # Some providers may require arguments
                return []
        
        # Use the standardized models.list() interface
        if hasattr(instance, "models") and hasattr(instance.models, "list"):
            res = instance.models.list()
            if isinstance(res, list):
                for m in res:
                    if isinstance(m, str):
                        models.append(m)
                    elif isinstance(m, dict) and "id" in m:
                        models.append(m["id"])
    except Exception:
        pass
    
    return models

class ClientCompletions(BaseCompletions):
    """Unified completions interface with automatic provider and model resolution."""
    
    def __init__(self, client: 'Client'):
        self._client = client
        self._last_provider: Optional[str] = None
    
    @property
    def last_provider(self) -> Optional[str]:
        return self._last_provider
    
    def _get_provider_instance(self, provider_class: Type[OpenAICompatibleProvider], **kwargs) -> OpenAICompatibleProvider:
        init_kwargs = {}
        if self._client.proxies: init_kwargs['proxies'] = self._client.proxies
        if self._client.api_key: init_kwargs['api_key'] = self._client.api_key
        init_kwargs.update(kwargs)
        
        try: return provider_class(**init_kwargs)
        except Exception:
            try: return provider_class()
            except Exception as e: raise RuntimeError(f"Failed to initialize provider {provider_class.__name__}: {e}")
    
    def _fuzzy_resolve_provider_and_model(self, model: str) -> Optional[Tuple[Type[OpenAICompatibleProvider], str]]:
        """Performs fuzzy search to find the closest model match across all providers."""
        available = self._get_available_providers()
        model_to_provider = {}
        
        for p_name, p_cls in available:
            # Try to get models from class first (fast path)
            p_models = _get_models_safely(p_cls)
            
            # If empty, try instantiating the provider to get models
            if not p_models:
                try:
                    instance = self._get_provider_instance(p_cls)
                    p_models = _get_models_safely(p_cls, instance)
                except Exception:
                    pass
            
            # Add all valid model names to our mapping
            for m in p_models:
                if m not in model_to_provider:
                    model_to_provider[m] = p_cls
        
        if not model_to_provider:
            return None
            
        matches = difflib.get_close_matches(model, model_to_provider.keys(), n=1, cutoff=0.6)
        if matches:
            matched_model = matches[0]
            if self._client.print_provider_info:
                print(f"\033[1;33mFuzzy match: '{model}' -> '{matched_model}'\033[0m")
            return model_to_provider[matched_model], matched_model
        return None

    def _resolve_provider_and_model(self, model: str, provider: Optional[Type[OpenAICompatibleProvider]]) -> Tuple[Type[OpenAICompatibleProvider], str]:
        """Resolves the best provider and model name based on input."""
        
        # 1. Handle Provider/model_name format
        if "/" in model:
            p_name, m_name = model.split("/", 1)
            found_p = next((cls for name, cls in OPENAI_PROVIDERS.items() if name.lower() == p_name.lower()), None)
            if found_p:
                return found_p, m_name

        # 2. If provider is explicitly given
        if provider:
            resolved_model = model
            if model == "auto":
                p_models = _get_models_safely(provider)
                if p_models:
                    resolved_model = random.choice(p_models)
                else:
                    resolved_model = "gpt-3.5-turbo"
            return provider, resolved_model

        # 3. If model is "auto", select a random available provider
        if model == "auto":
            available = self._get_available_providers()
            if not available:
                raise RuntimeError("No available chat providers found.")
            random.shuffle(available)
            p_name, p_cls = available[0]
            p_models = _get_models_safely(p_cls)
            m_name = random.choice(p_models) if p_models else "gpt-3.5-turbo"
            return p_cls, m_name

        # 4. Find provider that supports the given model name
        available = self._get_available_providers()
        for p_name, p_cls in available:
            p_models = _get_models_safely(p_cls)
            if p_models and model in p_models:
                return p_cls, model
        
        # 5. Fuzzy match
        fuzzy_result = self._fuzzy_resolve_provider_and_model(model)
        if fuzzy_result:
            return fuzzy_result

        # 6. Last resort: use a random available provider with the given model name
        if available:
            random.shuffle(available)
            return available[0][1], model
            
        raise RuntimeError(f"No providers found for model '{model}'")

    def _get_available_providers(self) -> List[Tuple[str, Type[OpenAICompatibleProvider]]]:
        exclude = set(self._client.exclude or [])
        if self._client.api_key:
            return [(name, cls) for name, cls in OPENAI_PROVIDERS.items() if name not in exclude]
        return [(name, cls) for name, cls in OPENAI_PROVIDERS.items() if name not in OPENAI_AUTH_REQUIRED and name not in exclude]

    def create(
        self,
        *,
        model: str = "auto",
        messages: List[Dict[str, Any]],
        max_tokens: Optional[int] = None,
        stream: bool = False,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        timeout: Optional[int] = None,
        proxies: Optional[dict] = None,
        provider: Optional[Type[OpenAICompatibleProvider]] = None,
        **kwargs: Any
    ) -> Union[ChatCompletion, Generator[ChatCompletionChunk, None, None]]:
        
        try:
            resolved_provider, resolved_model = self._resolve_provider_and_model(model, provider)
        except Exception:
            resolved_provider, resolved_model = None, model

        call_kwargs = {
            "model": resolved_model,
            "messages": messages,
            "stream": stream,
        }
        if max_tokens is not None: call_kwargs["max_tokens"] = max_tokens
        if temperature is not None: call_kwargs["temperature"] = temperature
        if top_p is not None: call_kwargs["top_p"] = top_p
        if tools is not None: call_kwargs["tools"] = tools
        if tool_choice is not None: call_kwargs["tool_choice"] = tool_choice
        if timeout is not None: call_kwargs["timeout"] = timeout
        if proxies is not None: call_kwargs["proxies"] = proxies
        call_kwargs.update(kwargs)

        if resolved_provider:
            try:
                provider_instance = self._get_provider_instance(resolved_provider)
                response = provider_instance.chat.completions.create(**call_kwargs)
                
                if stream and inspect.isgenerator(response):
                    try:
                        first_chunk = next(response)
                        self._last_provider = resolved_provider.__name__
                        def chained_gen(first, rest, pname):
                            if self._client.print_provider_info:
                                print(f"\033[1;34m{pname}:{resolved_model}\033[0m\n")
                            yield first
                            yield from rest
                        return chained_gen(first_chunk, response, resolved_provider.__name__)
                    except StopIteration: pass
                    except Exception: pass
                else:
                    # Check if response is valid and has non-empty content
                    if (response and hasattr(response, "choices") and response.choices and 
                        response.choices[0].message and response.choices[0].message.content and 
                        response.choices[0].message.content.strip()):
                        
                        self._last_provider = resolved_provider.__name__
                        if self._client.print_provider_info:
                            print(f"\033[1;34m{resolved_provider.__name__}:{resolved_model}\033[0m\n")
                        return response
                    else:
                        # Raise exception to trigger failover loop
                        raise ValueError(f"Provider {resolved_provider.__name__} returned empty content")
            except Exception: pass

        # Failover to other providers
        available_providers = self._get_available_providers()
        random.shuffle(available_providers)
        
        errors = []
        for p_name, p_cls in available_providers:
            if p_cls == resolved_provider: continue
            try:
                provider_instance = self._get_provider_instance(p_cls)
                p_models = _get_models_safely(p_cls)
                p_model = resolved_model if (p_models and resolved_model in p_models) else (random.choice(p_models) if p_models else resolved_model)
                
                failover_kwargs = call_kwargs.copy()
                failover_kwargs["model"] = p_model
                
                response = provider_instance.chat.completions.create(**failover_kwargs)
                
                if stream and inspect.isgenerator(response):
                    try:
                        first_chunk = next(response)
                        self._last_provider = p_name
                        def chained_gen(first, rest, pname, mname):
                            if self._client.print_provider_info:
                                print(f"\033[1;34m{pname}:{mname}\033[0m\n")
                            yield first
                            yield from rest
                        return chained_gen(first_chunk, response, p_name, p_model)
                    except (StopIteration, Exception): continue
                
                # Check if response is valid and has non-empty content
                if (response and hasattr(response, "choices") and response.choices and 
                    response.choices[0].message and response.choices[0].message.content and 
                    response.choices[0].message.content.strip()):
                    
                    self._last_provider = p_name
                    if self._client.print_provider_info:
                        print(f"\033[1;34m{p_name}:{p_model}\033[0m\n")
                    return response
                else:
                    errors.append(f"{p_name}: Returned empty response.")
                    continue
            except Exception as e:
                errors.append(f"{p_name}: {str(e)}")
                continue
        
        raise RuntimeError(f"All chat providers failed. Errors: {'; '.join(errors[:3])}")

class ClientChat(BaseChat):
    def __init__(self, client: 'Client'):
        self.completions = ClientCompletions(client)

class ClientImages(BaseImages):
    def __init__(self, client: 'Client'):
        self._client = client
        self._last_provider: Optional[str] = None
    
    @property
    def last_provider(self) -> Optional[str]:
        return self._last_provider
    
    def _get_provider_instance(self, provider_class: Type[TTICompatibleProvider], **kwargs) -> TTICompatibleProvider:
        try: return provider_class(**kwargs)
        except Exception:
            try: return provider_class()
            except Exception as e: raise RuntimeError(f"Failed to initialize TTI provider {provider_class.__name__}: {e}")
    
    def _fuzzy_resolve_provider_and_model(self, model: str) -> Optional[Tuple[Type[TTICompatibleProvider], str]]:
        """Performs fuzzy search to find the closest model match across all providers."""
        available = self._get_available_providers()
        model_to_provider = {}
        
        for p_name, p_cls in available:
            # Try to get models from class first (fast path)
            p_models = _get_models_safely(p_cls)
            
            # If empty, try instantiating the provider to get models
            if not p_models:
                try:
                    instance = self._get_provider_instance(p_cls)
                    p_models = _get_models_safely(p_cls, instance)
                except Exception:
                    pass
            
            # Add all valid model names to our mapping
            for m in p_models:
                if m not in model_to_provider:
                    model_to_provider[m] = p_cls
        
        if not model_to_provider:
            return None
            
        matches = difflib.get_close_matches(model, model_to_provider.keys(), n=1, cutoff=0.6)
        if matches:
            matched_model = matches[0]
            if self._client.print_provider_info:
                print(f"\033[1;33mFuzzy match: '{model}' -> '{matched_model}'\033[0m")
            return model_to_provider[matched_model], matched_model
        return None

    def _resolve_provider_and_model(self, model: str, provider: Optional[Type[TTICompatibleProvider]]) -> Tuple[Type[TTICompatibleProvider], str]:
        if "/" in model:
            p_name, m_name = model.split("/", 1)
            found_p = next((cls for name, cls in TTI_PROVIDERS.items() if name.lower() == p_name.lower()), None)
            if found_p: return found_p, m_name
        
        if provider:
            resolved_model = model
            if model == "auto":
                p_models = _get_models_safely(provider)
                resolved_model = random.choice(p_models) if p_models else "flux"
            return provider, resolved_model

        if model == "auto":
            available = self._get_available_providers()
            if not available:
                raise RuntimeError("No available image providers found.")
            random.shuffle(available)
            p_name, p_cls = available[0]
            p_models = _get_models_safely(p_cls)
            return p_cls, random.choice(p_models) if p_models else "flux"

        available = self._get_available_providers()
        for p_name, p_cls in available:
            p_models = _get_models_safely(p_cls)
            if p_models and model in p_models: return p_cls, model
        
        # Fuzzy match
        fuzzy_result = self._fuzzy_resolve_provider_and_model(model)
        if fuzzy_result:
            return fuzzy_result

        if available:
            random.shuffle(available)
            return available[0][1], model
        raise RuntimeError(f"No image providers found for model '{model}'")

    def _get_available_providers(self) -> List[Tuple[str, Type[TTICompatibleProvider]]]:
        exclude = set(self._client.exclude_images or [])
        return [(name, cls) for name, cls in TTI_PROVIDERS.items() if name not in TTI_AUTH_REQUIRED and name not in exclude]

    def generate(
        self,
        *,
        prompt: str,
        model: str = "auto",
        n: int = 1,
        size: str = "1024x1024",
        response_format: str = "url",
        provider: Optional[Type[TTICompatibleProvider]] = None,
        **kwargs: Any
    ) -> ImageResponse:
        
        try: resolved_provider, resolved_model = self._resolve_provider_and_model(model, provider)
        except Exception: resolved_provider, resolved_model = None, model

        call_kwargs = {"prompt": prompt, "model": resolved_model, "n": n, "size": size, "response_format": response_format}
        call_kwargs.update(kwargs)
        
        if resolved_provider:
            try:
                provider_instance = self._get_provider_instance(resolved_provider)
                response = provider_instance.images.create(**call_kwargs)
                self._last_provider = resolved_provider.__name__
                if self._client.print_provider_info:
                    print(f"\033[1;34m{resolved_provider.__name__}:{resolved_model}\033[0m\n")
                return response
            except Exception: pass
        
        available_providers = self._get_available_providers()
        random.shuffle(available_providers)
        for p_name, p_cls in available_providers:
            if p_cls == resolved_provider: continue
            try:
                provider_instance = self._get_provider_instance(p_cls)
                p_models = _get_models_safely(p_cls)
                p_model = resolved_model if (p_models and resolved_model in p_models) else (random.choice(p_models) if p_models else resolved_model)
                failover_kwargs = call_kwargs.copy()
                failover_kwargs["model"] = p_model
                
                response = provider_instance.images.create(**failover_kwargs)
                self._last_provider = p_name
                if self._client.print_provider_info:
                    print(f"\033[1;34m{p_name}:{p_model}\033[0m\n")
                return response
            except Exception: continue
        raise RuntimeError(f"All image providers failed.")

    def create(self, **kwargs) -> ImageResponse:
        return self.generate(**kwargs)

class Client:
    """Unified Webscout Client for AI providers."""
    
    def __init__(
        self,
        provider: Optional[Type[OpenAICompatibleProvider]] = None,
        image_provider: Optional[Type[TTICompatibleProvider]] = None,
        api_key: Optional[str] = None,
        proxies: Optional[dict] = None,
        exclude: Optional[List[str]] = None,
        exclude_images: Optional[List[str]] = None,
        print_provider_info: bool = False,
        **kwargs: Any
    ):
        self.provider = provider
        self.image_provider = image_provider
        self.api_key = api_key
        self.proxies = proxies or {}
        self.exclude = [e.upper() if e else e for e in (exclude or [])]
        self.exclude_images = [e.upper() if e else e for e in (exclude_images or [])]
        self.print_provider_info = print_provider_info
        self.kwargs = kwargs
        
        self.chat = ClientChat(self)
        self.images = ClientImages(self)
    
    @staticmethod
    def get_chat_providers() -> List[str]: return list(OPENAI_PROVIDERS.keys())
    
    @staticmethod
    def get_image_providers() -> List[str]: return list(TTI_PROVIDERS.keys())
    
    @staticmethod
    def get_free_chat_providers() -> List[str]: return [name for name in OPENAI_PROVIDERS.keys() if name not in OPENAI_AUTH_REQUIRED]
    
    @staticmethod
    def get_free_image_providers() -> List[str]: return [name for name in TTI_PROVIDERS.keys() if name not in TTI_AUTH_REQUIRED]

try:
    def run_api(*args, **kwargs):
        from webscout.server.server import run_api as _run_api
        return _run_api(*args, **kwargs)
    def start_server(**kwargs):
        from webscout.server.server import run_api as _run_api
        return _run_api(**kwargs)
except ImportError:
    def run_api(*args, **kwargs): raise ImportError("webscout.server.server.run_api is not available.")
    def start_server(*args, **kwargs): raise ImportError("webscout.server.server.start_server is not available.")

if __name__ == "__main__":
    client = Client(print_provider_info=True)
    print("Testing auto resolution...")
    try:
        response = client.chat.completions.create(model="auto", messages=[{"role": "user", "content": "Hi"}])
        print(f"Auto Result: {response.choices[0].message.content[:50]}...")
    except Exception as e: print(f"Error: {e}")