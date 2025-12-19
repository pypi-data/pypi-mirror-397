# Changelog

All notable changes to this project will be documented in this file.


## [2025.12.18] - 2025-12-18

### ✨ Added
- **feat**: webscout/Provider/OPENAI/typliai.py - New OpenAI-compatible TypliAI provider with streaming and non-streaming support for GPT-4.1, GPT-5, Gemini 2.5, Claude 4.5, and Grok 4 models.

### 🚮 Removed
- **removed**: webscout/Provider/Perplexitylabs.py - Removed PerplexityLabs provider file.
- **removed**: PerplexityLabs entry from Provider.md documentation and statistics.
- **removed**: References to PerplexityLabs from webscout/Provider/__init__.py.
- **removed**: webscout/Provider/TeachAnything.py - Removed TeachAnything provider file.
- **removed**: TeachAnything entry from Provider.md documentation and statistics.
- **removed**: References to TeachAnything from webscout/Provider/__init__.py.

### 🛠️ Fixed
- **fix**: webscout/Provider/turboseek.py - Updated provider to handle new HTML-based raw stream response format and improved HTML-to-Markdown conversion.

## [2025.12.17] - 2025-12-17

### ✨ Added

### 🚮 Removed
- **removed**: webscout/Provider/Nemotron.py - Removed Nemotron provider as the file doesn't exist and was causing import errors
- **removed**: References to NEMOTRON from webscout/Provider/__init__.py
- **removed**: Nemotron entry from Provider.md documentation

- **feat**: webscout/Provider/OPENAI/gradient.py - New OpenAI-compatible Gradient Network provider for accessing distributed GPU clusters with models GPT OSS 120B and Qwen3 235B
- **feat**: webscout/Provider/OPENAI/gradient.py - Supports both streaming and non-streaming modes with thinking/reasoning capability
- **feat**: webscout/Provider/OPENAI/gradient.py - Auto-detection of cluster mode per model (nvidia for GPT OSS 120B, hybrid for Qwen3 235B)
- **feat**: webscout/Provider/freeassist.py - New OpenAI-compatible FreeAssist provider using FreeAssist.ai API with access to multiple AI models including gemini 2.5 flash and flash lite and GPT-5-nano and GPT-5-mini
- **feat**: webscout/Provider/OPENAI/sambanova.py - New OpenAI-compatible Sambanova provider supporting Llama 3.1/3.3, Qwen, and DeepSeek models with streaming capabilities
- **feat**: webscout/Provider/OPENAI/meta.py - New OpenAI-compatible Meta AI provider with web authentication, optional Facebook login, and streaming support

### 🔧 Improved

- **refactor**: webscout/Provider/Gradient.py - Major rewrite with correct headers matching actual API, proper SSE response parsing for content/reasoningContent
- **refactor**: webscout/Provider/Gradient.py - Now uses sanitize_stream with custom _gradient_extractor following the pattern of other providers
- **refactor**: webscout/Provider/Gradient.py - Added MODEL_CLUSTERS mapping for auto-detection of cluster mode (nvidia for GPT, hybrid for Qwen3)
- **refactor**: webscout/Provider/Gradient.py - Updated model names to use spaces (GPT OSS 120B, Qwen3 235B) matching API format
- **feat**: webscout/Provider/OPENAI/freeassist.py - Supports both streaming and non-streaming modes with proper SSE parsing
- **feat**: webscout/Provider/OPENAI/zenmux.py - Implemented dynamic model list fetching from `https://zenmux.ai/api/v1/models` API endpoint, making it fully compatible with Groq provider pattern
- **refactor**: webscout/Provider/TextPollinationsAI.py - Switched to requests library and implemented proper non-streaming support via `stream=False` to match API behavior
- **fix**: webscout/Provider/OPENAI/textpollinations.py - Fixed duplicate code blocks and syntax errors, ensuring proper class structure and dynamic model fetching

### 🚮 Removed
- **removed**: webscout/Provider/OPENAI/FreeGemini.py - Removed FreeGemini provider due to service deprecation
- **removed**: webscout/Provider/OpenGPT.py - Removed OpenGPT provider from the project

### 🔧 Maintenance
- **refactor**: webscout/Provider/OPENAI/DeepAI.py - Implemented dynamic model fetching using `get_models()` and `update_available_models()` class methods following Cerebras provider pattern
- **refactor**: webscout/Provider/OPENAI/textpollinations.py - Implemented dynamic model fetching using `get_models()` and `update_available_models()` class methods following Cerebras provider pattern
- **refactor**: webscout/Provider/TTI/together.py - Implemented dynamic model fetching using `get_models()` and `update_available_models()` class methods following Cerebras provider pattern
- **docs**: Updated provider documentation to reflect consistent dynamic model fetching implementation across providers

## [2025.12.16] - 2025-12-16

### ✨ Added

- **feat**: webscout/Provider/OPENAI/zenmux.py - Added `get_models()` and `update_available_models()` class methods for automatic model discovery and updating AVAILABLE_MODELS on initialization

#### GGUF Converter v2.0 Major Update
- **feat**: webscout/Extra/gguf.py - Upgraded to version 2.0.0 with latest llama.cpp features
- **feat**: Added new output types (`--outtype`): `f32`, `f16`, `bf16`, `q8_0`, `tq1_0`, `tq2_0`, `auto`
- **feat**: Added remote mode (`--remote`) for experimental tensor streaming without full model download
- **feat**: Added dry run mode (`--dry-run`) to preview split plans without writing files
- **feat**: Added vocab-only mode (`--vocab-only`) to extract just vocabulary without model weights
- **feat**: Added no-lazy mode (`--no-lazy`) to disable lazy evaluation for debugging
- **feat**: Added model name override (`--model-name`) for custom output naming
- **feat**: Added small first shard (`--small-first-shard`) for metadata-only first split file
- **feat**: Added new K-quant types: `q2_k_s`, `q4_k_l`, `q5_k_l`
- **feat**: Added ternary quantization: `tq1_0` (1-bit), `tq2_0` (2-bit) experimental
- **feat**: Added comprehensive IQ (importance-based) quantization methods:
  - 1-bit: `iq1_s`, `iq1_m`
  - 2-bit: `iq2_xxs`, `iq2_xs`, `iq2_s`, `iq2_m`
  - 3-bit: `iq3_xxs`, `iq3_xs`, `iq3_s`, `iq3_m`
  - 4-bit: `iq4_nl`, `iq4_xs`

#### GitToolkit Enhancements
- **feat**: webscout/Extra/GitToolkit/gitapi/search.py - New `GitSearch` class with methods for GitHub Search API: `search_repositories()`, `search_users()`, `search_topics()`, `search_commits()`, `search_issues()`, `search_labels()`
- **feat**: webscout/Extra/GitToolkit/gitapi/gist.py - New `Gist` class for public gist operations: `get()`, `list_public()`, `list_for_user()`, `get_commits()`, `get_forks()`, `get_revision()`, `get_comments()`
- **feat**: webscout/Extra/GitToolkit/gitapi/organization.py - New `Organization` class for org data: `get_info()`, `get_repos()`, `get_public_members()`, `get_events()`
- **feat**: webscout/Extra/GitToolkit/gitapi/trending.py - New `Trending` class for GitHub trending: `get_repositories()`, `get_developers()`
- **feat**: webscout/Extra/GitToolkit/gitapi/repository.py - Added 9 new methods: `get_readme()`, `get_license()`, `get_topics()`, `get_forks()`, `get_stargazers()`, `get_watchers()`, `compare()`, `get_events()`
- **feat**: webscout/Extra/GitToolkit/gitapi/user.py - Added 2 new methods: `get_social_accounts()`, `get_packages()`

#### YTToolkit Enhancements
- **feat**: webscout/Extra/YTToolkit/ytapi/suggestions.py - New `Suggestions` class for YouTube autocomplete: `autocomplete()`, `trending_searches()`
- **feat**: webscout/Extra/YTToolkit/ytapi/shorts.py - New `Shorts` class for YouTube Shorts: `is_short()`, `get_trending()`, `search()`
- **feat**: webscout/Extra/YTToolkit/ytapi/hashtag.py - New `Hashtag` class for hashtag videos: `get_videos()`, `get_metadata()`, `extract_from_text()`
- **feat**: webscout/Extra/YTToolkit/ytapi/captions.py - New `Captions` class for video transcripts: `get_available_languages()`, `get_transcript()`, `get_timed_transcript()`, `search_transcript()`
- **feat**: webscout/Extra/YTToolkit/ytapi/video.py - Added new properties/methods: `is_live`, `is_short`, `hashtags`, `get_related_videos()`, `get_chapters()`, `stream_comments()`
- **feat**: webscout/Extra/YTToolkit/ytapi/query.py - Added new search methods: `shorts()`, `live_streams()`, `videos_by_duration()`, `videos_by_upload_date()`
- **feat**: webscout/Extra/YTToolkit/ytapi/extras.py - Added new trending methods: `shorts_videos()`, `movies()`, `podcasts()`

### 🔧 Improved
- **refactor**: webscout/Extra/YTToolkit/transcriber.py - Rewrote YTTranscriber to use YouTube's InnerTube API for more reliable transcript fetching, replacing brittle HTML parsing with direct API calls
  - Uses `/youtubei/v1/player` endpoint for stable data extraction
  - Added better error handling for IP blocks, bot detection, and age-restricted videos
  - Fixed caption name parsing for new YouTube format (runs vs simpleText)
  - Removed problematic `&fmt=srv3` from caption URLs
  - Added fallback XML parsing for edge cases

### 🔧 Maintenance
- **refactor**: webscout/Extra/GitToolkit/gitapi/__init__.py - Updated exports to include new classes
- **refactor**: webscout/Extra/YTToolkit/ytapi/__init__.py - Updated exports to include new classes
- **docs**: webscout/Extra/GitToolkit/gitapi/README.md - Updated documentation with all new features and examples
- **docs**: webscout/Extra/YTToolkit/README.md - Updated documentation with all new features and examples
- **refactor**: webscout/Extra/gguf.py - Updated conversion logic to use dynamic outtype instead of hardcoded f16
- **refactor**: webscout/Extra/gguf.py - Improved split size validation to support K, M, G units matching llama.cpp
- **refactor**: webscout/Extra/gguf.py - Added outtype validation against VALID_OUTTYPES set
- **docs**: Moved webscout/Extra/gguf.md → docs/gguf.md for better documentation organization
- **docs**: docs/gguf.md - Complete rewrite for v2.0 with all new features, examples, and troubleshooting

### 🚮 Removed
- **removed**: webscout/Extra/autocoder/ - Completely removed AutoCoder package directory and all its files.
- **refactor**: webscout/AIutel.py - Removed AutoCoder import.
- **refactor**: webscout/Extra/__init__.py - Removed AutoCoder import.


## [2025.12.09] - 2025-12-09

### ✨ Added
- **feat**: pyproject.toml - Added `litprinter` dependency for improved logging functionality
- **feat**: webscout/Provider/OPENAI/utils.py - Added dict-like access methods (`__getitem__`, `__setitem__`, `keys`, `values`, `items`) to `ChatCompletionMessage` class for better compatibility
- **feat**: webscout/Provider/OPENAI/PI.py - Added missing `count_tokens` import for proper token counting functionality

### 🐛 Fixed
- **fix**: webscout/server/providers.py - Added `required_auth = False` filtering to only initialize OpenAI-compatible providers that don't require authentication, improving server startup and reducing provider count to 28 no-auth providers

### 🔧 Maintenance
- **refactor**: Replaced Litlogger with litprinter across entire codebase for consistent logging:
  - **refactor**: webscout/Extra/autocoder/autocoder.py - Updated logger initialization comment
  - **refactor**: webscout/Extra/tempmail/async_utils.py - Replaced standard logging with litprinter
  - **refactor**: webscout/Provider/OPENAI/K2Think.py - Replaced Litlogger imports with litprinter
  - **refactor**: webscout/Provider/OPENAI/base.py - Replaced Litlogger with litprinter for error logging
  - **refactor**: webscout/Provider/TTS/speechma.py - Replaced Litlogger with litprinter
  - **refactor**: webscout/Provider/meta.py - Removed unused logging import
  - **refactor**: webscout/__init__.py - Removed Litlogger import
  - **refactor**: webscout/conversation.py - Replaced logging with litprinter
  - **refactor**: webscout/search/base.py - Replaced logging with litprinter
  - **refactor**: webscout/search/engines/wikipedia.py - Replaced logging with litprinter
  - **refactor**: webscout/search/http_client.py - Replaced logging with litprinter
  - **refactor**: webscout/server/config.py - Replaced Litlogger with litprinter
  - **refactor**: webscout/server/providers.py - Replaced Litlogger with litprinter
  - **refactor**: webscout/server/request_processing.py - Replaced Litlogger with litprinter and added inline utility functions
  - **refactor**: webscout/server/routes.py - Replaced Litlogger with litprinter
  - **refactor**: webscout/server/server.py - Replaced Litlogger with litprinter
- **refactor**: webscout/search/engines/__init__.py - Changed from auto-discovery to static imports for better performance and reliability
- **refactor**: webscout/Provider/AISEARCH/__init__.py - Cleaned up import comments
- **refactor**: webscout/server/request_processing.py - Added inline implementations of `get_client_ip()`, `generate_request_id()`, and `log_api_request()` functions to replace dependency on simple_logger.py
- **refactor**: README.md - Removed reference to deprecated LitLogger
- **refactor**: lol.py - Updated example to use ChatGPT provider and added cprint import

### 🚮 Removed
- **removed**: AGENTS.md - Deleted unused documentation file
- **removed**: webscout/Litlogger/ - Completely removed Litlogger package directory and all its files (README.md, __init__.py, formats.py, handlers.py, levels.py, logger.py)
- **removed**: webscout/litprinter/__init__.py - Removed redundant wrapper file
- **removed**: webscout/server/simple_logger.py - Deleted file as functionality moved inline to request_processing.py

## [2025.12.03] - 2025-12-03

### ✨ Added
- **feat**: webscout/search/engines/__init__.py - Updated auto-discovery logic to register all search engine classes with `name` and `category` attributes, not just BaseSearchEngine subclasses
- **feat**: webscout/server/routes.py - Added new `/search/provider` endpoint that returns details about each search provider including name, supported categories, and parameters
- **feat**: webscout/models.py - Enhanced LLM models class with `providers()` and `provider()` methods that return detailed provider information including models, parameters, and metadata
- **feat**: webscout/models.py - Added TTI (Text-to-Image) models support with `_TTIModels` class including detailed provider information methods
- **feat**: added all engines to cli.py
- **feat**: cli.py - Added CLI commands for Bing search (text, images, news, suggestions)
- **feat**: cli.py - Added CLI commands for Yahoo search (text, images, videos, news, answers, maps, translate, suggestions, weather)
- **feat**: Algion.py - Implemented dynamic model loading from API without hardcoded defaults, ensuring AVAILABLE_MODELS is only populated if API fetch succeeds
- **feat**: Cerebras.py - Modified AVAILABLE_MODELS to use dynamic loading without defaults, requiring API key for model fetching
- **feat**: OPENAI/algion.py - Added OpenAI-compatible Algion provider with dynamic model loading
- **feat**: OPENAI/cerebras.py - Added OpenAI-compatible Cerebras provider with dynamic model loading
- **feat**: OPENAI/elmo.py - Added OpenAI-compatible Elmo provider
- **feat**: conversation.py - Added logging import for debug messages in file operations
- **feat**: conversation.py - Added __trim_chat_history private method for history length management

### 🐛 Fixed
- **fix**: webscout/server/routes.py - Fixed search engine method checking bug where it was looking for `hasattr(searcher, type)` instead of `hasattr(searcher, "run")`, preventing DuckDuckGo and other engines from working
- **fix**: webscout/server/routes.py - Fixed FastAPI UI documentation issue where search engines were listed multiple times by using `set()` to get unique engine names
- **fix**: webscout/search/engines/brave.py - Added `run` method to Brave search engine class for compatibility with search endpoint
- **fix**: webscout/search/engines/mojeek.py - Added `run` method to Mojeek search engine class for compatibility with search endpoint
- **fix**: webscout/search/engines/yandex.py - Added `run` method to Yandex search engine class for compatibility with search endpoint
- **fix**: webscout/search/engines/wikipedia.py - Added `run` method to Wikipedia search engine class for compatibility with search endpoint
- **fix**: webscout/models.py - Fixed `_LLMModels.summary()` method which was missing its return statement, causing it to return `None` instead of the expected dictionary with provider and model counts

### 🔧 Maintenance
- **refactor**: Added dynamic model fetching to OPENAI and GEMINIAPI providers similar to Algion provider, with get_models() classmethod that fetches available models from API
- **refactor**: Updated models.py to prioritize get_models() method over AVAILABLE_MODELS for dynamic model loading in provider discovery
- **refactor**: Added `name` and `category` attributes to all DuckDuckGo search engine classes (text, images, videos, news, suggestions, answers, maps, translate, weather)
- **refactor**: Added `name` and `category` attributes to Bing search engine classes (text, images, news, suggestions)
- **refactor**: Added `name` and `category` attributes to Yep search engine classes (text, images, suggestions)
- **refactor**: Updated webscout/search/engines/bing/__init__.py to import and expose Bing search engine classes
- **refactor**: Updated `/search` endpoint description to reflect support for all available search engines and search types
- **refactor**: prompt_manager.py - Removed unused imports, redundant code, and cleaned up class for clarity and minimalism
- **chore**: prompt_manager.py - Minor optimizations and code style improvements
- **refactor**: cli.py - Cleaned up incomplete command stubs and fixed inconsistencies in option decorators
- **removed**: cli.py - Removed unused imports and broken command implementations
- **cleanup**: Removed unused `schemas.py` file from server.
- **refactor**: Removed all imports and references to `HealthCheckResponse` and `ErrorResponse` from `routes.py` and `__init__.py`.
- **refactor**: Cleaned up unused imports (secrets, etc.) in `routes.py`.
- **refactor**: Updated `__init__.py` to only export actively used symbols and remove legacy schema references.
- **refactor**: Ensured all server modules only contain necessary code and imports, improving maintainability and clarity.
- **refactor**: conversation.py - Simplified Conversation class to use string-based chat history instead of message objects, removing tool handling, metadata, timestamps, and complex validation
- **refactor**: conversation.py - Updated history format to use "User : %(user)s\nLLM :%(llm)s" pattern for consistency
- **refactor**: conversation.py - Removed all tool-related methods (handle_tool_response, _parse_function_call, execute_function, get_tools_description, update_chat_history_with_tool)
- **refactor**: conversation.py - Streamlined file loading and history management to use simple string concatenation
- **refactor**: yep.py - Removed tool parameter and tool handling logic from YEPCHAT provider
- **refactor**: yep.py - Simplified ask method to directly update chat history without tool processing
- **refactor**: TeachAnything.py - No changes needed as it didn't use tool functionality

### 🚮 Removed
- **removed**: conversation.py - Removed Fn class, Message dataclass, FunctionCall, ToolDefinition, FunctionCallData TypedDicts
- **removed**: conversation.py - Removed add_message, validate_message, _append_to_file, _compress_history methods
- **removed**: conversation.py - Removed tool_history_format and related attributes
- **removed**: yep.py - Removed tool-related imports and examples from docstrings
- **removed**: AsyncProvider - Completely removed AsyncProvider class and all imports from provider files (Cohere.py, Groq.py, Koboldai.py, julius.py, HeckAI.py, ChatHub.py)
- **removed**: AsyncGROQ - Removed AsyncGROQ class from Groq.py that inherited from AsyncProvider
- **removed**: webscout/server/routes.py - Removed monitoring endpoints (`/monitor/requests`, `/monitor/stats`, `/monitor/health`) and related code from server
- **removed**: webscout/server/simple_logger.py - Removed unused monitoring methods (`get_recent_requests`, `get_stats`) from SimpleRequestLogger class


## [2025.12.01] - 2025-12-01
### ✨ Added
 - **feat**: sanitize.py - Added `output_formatter` parameter to `sanitize_stream()` for custom output transformation
 - **feat**: sanitize.py - Users can now define custom formatter functions to transform each output item into any desired structure before yielding

### 🚮 Removed
 - **removed**: sanitize.py - Removed built-in response formatters (`ResponseFormatter`, `OutputFormat`, `create_openai_response`, `create_openai_stream_chunk`, `create_anthropic_response`, `create_anthropic_stream_chunk`, `format_output`) in favor of user-defined `output_formatter` functions
 - **removed**: sanitize.py - Removed `output_format` and `format_options` parameters from `sanitize_stream()` - use `output_formatter` instead

### 📝 Documentation
 - **docs**: sanitize.md - Updated documentation with `output_formatter` parameter and usage examples
 - **docs**: sanitize.md - Removed references to removed built-in formatters

## [2025.11.30] - 2025-11-30

### 🔧 Maintenance
 - **refactor**: Added missing `# type: ignore` to imports for optional dependencies (trio, numpy, tiktoken, pandas) in multiple modules for better compatibility and linting
 - **refactor**: Improved type hints and error handling in `scout/core/crawler.py` and `scout/core/scout.py`
 - **refactor**: Updated `oivscode.py` to generate and use a unique ClientId (UUID) in headers
 - **refactor**: Updated CLI group import in `swiftcli/core/cli.py` to avoid circular dependency
 - **refactor**: Minor docstring and comment cleanups in AISEARCH providers
 - **chore**: Removed unfinished providers: `Aitopia.py`, `VercelAIGateway.py`, `puterjs.py`, `scira_search.py`, `hika_search.py` from Provider/UNFINISHED and Provider/AISEARCH

### 🐛 Fixed
 - **fix**: Fixed error handling in `sanitize.py` async stream processing (removed logger usage in extractor error branch)
 - **fix**: Fixed import and type hint issues in `duckduckgo/base.py`, `search/http_client.py`, `Provider/cerebras.py`, and others
 - **fix**: Fixed streaming output and test code in `genspark_search.py`, `PERPLEXED_search.py`, and `iask_search.py` for more robust CLI testing
 - **fix**: Fixed YahooSearch import for Dict type in `search/yahoo_main.py`

### 🚮 Removed
 - **removed**: Deleted unfinished provider files: `Aitopia.py`, `VercelAIGateway.py`, `puterjs.py`, `scira_search.py`, `hika_search.py` for codebase cleanup

### 🐛 Fixed
 - **fix**: TogetherAI.py - Updated API endpoint from `https://chat.together.ai/api/chat-completion` to `https://api.together.xyz/v1/chat/completions` for compatibility with the public Together API
 - **fix**: TogetherAI.py - Fixed payload parameters to use OpenAI-compatible format (`model`, `max_tokens`, `top_p` instead of `modelId`, `maxTokens`, `topP`)
 - **fix**: OPENAI/TogetherAI.py - Removed self-activation endpoint logic that auto-fetched API keys from external service

### ✨ Added
 - **feat**: TogetherAI.py - Implemented dynamic model loading from `https://api.together.xyz/v1/models` API, similar to Groq provider
 - **feat**: TogetherAI.py - Added `get_models()` and `update_available_models()` class methods for automatic model discovery
 - **feat**: OPENAI/TogetherAI.py - Added dynamic model loading support with automatic model list updates on initialization
 - **feat**: OPENAI/TogetherAI.py - Now requires user-provided API key via `api_key` parameter, following Groq provider pattern

### 🔧 Maintenance
 - **refactor**: TogetherAI.py - Changed `AVAILABLE_MODELS` from hardcoded dictionary to dynamically populated list
 - **refactor**: TogetherAI.py - Updated model validation to handle empty model lists gracefully when API fetch fails
 - **refactor**: OPENAI/TogetherAI.py - Removed `activation_endpoint` and `get_activation_key()` method for better security practices
 - **refactor**: OPENAI/TogetherAI.py - Updated `__init__` to accept `api_key` parameter and conditionally update models if key is provided

## [2025.11.21] - 2025-11-21

### 🐛 Fixed
 - **fix**: IBM.py - Fixed typo in `refresh_identity` method where `s-elf.headers` was incorrectly used instead of `self.headers`
 - **fix**: AIauto.py - Fixed critical bug where `chat` method could return a generator when `stream=False`, causing `AssertionError` in providers like AI4Chat
 - **fix**: AIauto.py - Added proper handling for providers that return generators even in non-streaming mode by consuming the generator to extract the return value

### ✨ Added
 - **feat**: AIauto.py - Enhanced provider failover mechanism to "peek" at the first chunk of streaming responses, allowing automatic failover to next provider if current one fails immediately
 - **feat**: AIauto.py - Split `chat` method into `_chat_stream` and `_chat_non_stream` helper methods for clearer separation of streaming vs non-streaming logic
 - **feat**: OPENAI/ibm.py - Added OpenAI-compatible IBM Granite provider in `webscout/Provider/OPENAI/` with support for `granite-chat` and `granite-search` models
 - **feat**: OPENAI/ibm.py - Implemented using `format_prompt()` and `count_tokens()` utilities from utils.py for proper message formatting and accurate token counting
 - **feat**: OPENAI/ibm.py - Manual SSE (Server-Sent Events) stream parsing without sanitize_stream dependency, consistent with other OPENAI providers

### 🔧 Maintenance
 - **refactor**: AIauto.py - Improved robustness of AUTO provider to work seamlessly with all providers in webscout.Provider package
 - **refactor**: AIauto.py - Added generator type checking and handling to prevent type mismatches between streaming and non-streaming responses

## [2025.11.20] - 2025-11-20

### 🐛 Fixed
 - **fix**: sanitize.py - Fixed critical async stream processing logic error where variable `idx` was used outside its conditional scope, causing potential `UnboundLocalError`
 - **fix**: sanitize.py - Fixed Python 3.9+ compatibility issue by replacing `Pattern` from typing with `re.Pattern` for proper isinstance() checks

### 🔧 Maintenance
 - **refactor**: sanitize.py - Reorganized imports for better structure (moved chain, functools, asyncio to top level)
 - **chore**: sanitize.py - Added `__all__` export list for explicit public API definition
 - **docs**: sanitize.py - Added comprehensive module docstring
 - **refactor**: sanitize.py - Updated all type hints to use modern syntax with `re.Pattern[str]`
 - **refactor**: Apriel.py - Simplified raw mode streaming logic for better performance

## [2025.11.19] - 2025-11-19

### 🔧 Maintenance
 - **chore**: Bard - added `gemini-3-pro` model with appropriate headers to `BardModel` enum
 - **GEMINI** - added `gemini-3-pro` model support in `GEMINI` class
 - **feat**: Updated search engines to use dataclass objects from results.py for better type safety and consistency
 - **refactor**: Updated all Providers to use `raw` flag of sanatize_stream for easy debugging
 - **removed**: Removed Cloudflare Provider

### 🐛 Fixed
 - **fix**: ChatGPT provider - Fixed OpenAI compatibility issues in `webscout/Provider/OPENAI/chatgpt.py` by updating streaming and non-streaming implementations to properly handle Server-Sent Events format and match OpenAI's response structure exactly
 - **fix**: ChatGPT provider - Enhanced error handling and parameter validation to follow OpenAI conventions
 - **fix**: AkashGPT provider - Fixed authentication issue in `webscout/Provider/akashgpt.py` by updating API key handling to use cookies for authentication

### ✨ Added
 - **feat**: ChatGPT provider - Added new models to AVAILABLE_MODELS including `gpt-5-1`, `gpt-5-1-instant`, `gpt-5-1-thinking`, `gpt-5`, `gpt-5-instant`, `gpt-5-thinking`
 - **feat**: New Provider: Algion with `gpt-5.1`and other models
## [2025.11.17] - 2025-11-17

### 🔧 Maintenance
 - **fix**: swiftcli - improved argument parsing: support `--key=value` and `-k=value` syntax; handle repeated flags/options (collected into lists)
 - **fix**: swiftcli - `convert_type` now handles boolean inputs and list-typed values robustly
 - **feat**: swiftcli - added support for option attributes: `count`, `multiple`, and `is_flag`; option callbacks supported; `choices` validation extended to multiple options
 - **fix**: swiftcli - option decorator uses a sentinel for unspecified defaults to avoid overriding function defaults with `None`
 - **feat**: swiftcli - CLI and `Group` now support the `@pass_context` decorator to inject `Context` and can run `async` coroutine commands
 - **fix**: swiftcli - help output deduplicates commands and displays aliases clearly; group help deduplicated and improved formatting
 - **test**: swiftcli - added comprehensive unit tests covering parsing, option handling (count/multiple/choices), `pass_context`, async behavior, group commands, and plugin manager lifecycle
 - **chore**: swiftcli - updated README with changelog, improved examples, and removed temporary debug/test helper files
 - **testing**: All swiftcli tests added in this change pass locally (14 tests total)

## [2025.11.16] - 2025-11-16
- **feat**: added `moonshotai/Kimi-K2-Thinking` and `MiniMaxAI/MiniMax-M2` models to DeepInfra provider AVAILABLE_MODELS in both `webscout/Provider/Deepinfra.py` and `webscout/Provider/OPENAI/deepinfra.py`
- **feat**: 

###  Maintenance
- **feat**: fixed formating issue in HeckAI replaced `strip_chars=" \n\r\t",`  with `strip_chars=""`
- **chore**: updated CHANGELOG.md to changelog.md in MANIFEST.in for consistency
- **chore**: updated release-with-changelog.yml to handle multiple version formats in changelog parsing
- **feat**: Updated changelog parsing to recognize multiple version formats (e.g., "vX.Y.Z", "X.Y.Z") for improved release automation.
- **feat**: updated `sanitize_stream` to support both `extract_regexes` and `content_extractor` at same time
- **chore**: updated `release-with-changelog.yml` to normalize version strings by stripping leading 'v' or 'V'
- **chore**: updated `sanitize_stream` docstring to clarify usage of `extract_regexes` and `content_extractor`
- **chore**: removed deprected models from venice provider
- **chore**: updated venice provider model list in AVAILABLE_MODELS
- **chore**: updated models list in textpollionations provider
- **chore**: replaced `anthropic:claude-3-5-haiku-20241022` with `anthropic:claude-haiku-4-5-20251001` in typefully provider 

### Added
- **feat**: added `anthropic:claude-haiku-4-5-20251001` to typefully provider AVAILABLE_MODELS
- **feat**: New IBM provider with `granite-search` and `granite-chat` models 

## [2025.11.06] - 2025-11-06

### 🔧 Maintenance
- **chore**: Remove GMI provider (a8928a0) — Cleaned up provider roster by removing GMI to simplify maintenance and reduce duplicate or deprecated provider support.

## [2025.10.22] - 2025-10-22

### ✨ Added
- **feat**: Add `claude-haiku-4.5` model to Flowith provider (3a80249) — Flowith now supports additional Claude variants for creative text generation.
- **feat**: Add `openai/gpt-oss-20b` and `openai/gpt-oss-120b` models to GMI provider (3a80249) — Added support for larger OSS GPT models via GMI.

### 🔧 Maintenance
- **refactor**: Change `DeepAI` `required_auth` to `True` (3a80249) — Ensure DeepAI provider requires authentication for API access.
- **chore**: Add import error handling for `OLLAMA` provider (3a80249) — Graceful degradation when optional dependencies are missing.
- **chore**: Remove deprecated `FalconH1` and `deepseek_assistant` providers (3a80249) — Reduced clutter and removed unsupported providers.
- **chore**: Update `OPENAI`, `flowith`, and `gmi` providers with new model lists and aliases (3a80249) — Keep model availability up-to-date and consistent.

## [2025.10.18] - 2025-10-18

### 🚀 Major Enhancements
- **🤖 AI Provider Expansion**: Integrated SciRA-AI and SciRA-Chat providers, adding robust model mapping and aliasing to unify behavior across providers.

### 📦 Package Structure
- **🛠️ Model Mapping System**: Introduced `MODEL_MAPPING` and `SCI_RA_TO_MODEL` dictionaries and updated `AVAILABLE_MODELS` lists to keep model names consistent and avoid duplication.

### ⚡ Improvements
- **🔄 Enhanced Model Resolution**: Improved `convert_model_name` and `_resolve_model` logic to better handle aliases, fallbacks, and unsupported names with clearer error messages.
- **🧪 Test and Example Updates**: Updated provider `__main__` blocks to list available models and print streaming behavior for easier local testing.
- **📝 Documentation**: Improved docstrings and comments clarifying model resolution and provider behavior.

### 🔧 Refactoring
- **⚙️ Provider Interface Standardization**: Refactored provider base classes and initialization logic to standardize how models are selected and aliases are resolved.

## [2025.10.17] - 2025-10-17

### ✨ Added
- **feat**: Add `sciRA-Coding` and `sciRA-Vision` providers (7e8f2a1)
- **feat**: Add `sciRA-Reasoning` and `sciRA-Analyze` providers (7e8f2a1)

### 🔧 Maintenance
- **chore**: Update provider initialization logic to more robustly support new sciRA families (7e8f2a1)
- **chore**: Add comprehensive model listings for newly added providers (7e8f2a1)

## [2025.10.16] - 2025-10-16

### ✨ Added
- **feat**: Add `sciRA-General` and `sciRA-Assistant` providers (9c4d1b3)
- **feat**: Add `sciRA-Research` and `sciRA-Learn` providers (9c4d1b3)

### 🔧 Maintenance
- **chore**: Refactor provider base classes for improved extensibility (9c4d1b3)
- **chore**: Add model validation logic to avoid exposing unsupported names (9c4d1b3)

## [2025.10.15] - 2025-10-15

### ✨ Added
- **feat**: Introduce SciRA provider framework and initial model mappings (5a2f8c7)

### 🔧 Maintenance
- **chore**: Set up SciRA provider infrastructure and basic authentication handling (5a2f8c7)

## [2025.10.10] - 2025-10-10

### ✨ Added
- **feat**: Add Flowith provider with multiple model support (b3d8a21)
- **feat**: Add GMI provider with advanced model options (b3d8a21)

### 🔧 Maintenance
- **chore**: Update provider documentation and add installation instructions for new providers (b3d8a21)

## [2025.10.05] - 2025-10-05

### ✨ Added
- **feat**: Initial release with core Webscout functionality (1a2b3c4) — Added web scraping, AI provider integration, and base CLI tooling.

### 🔧 Maintenance
- **chore**: Set up project structure, initial docs, and example workflows (1a2b3c4)

---

For more details, see the [documentation](docs/) or [GitHub repository](https://github.com/pyscout/Webscout).

For more details, see the [documentation](docs/) or [GitHub repository](https://github.com/pyscout/Webscout).



For more details, see the [documentation](docs/) or [GitHub repository](https://github.com/pyscout/Webscout).



