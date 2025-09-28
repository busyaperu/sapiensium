modelos = {
    # ===== GOOGLE GEMINI =====
    'gemini-1-5-pro': {
        'api': 'google',
        'model_id': 'gemini-1.5-pro',
        'api_key_env': 'GOOGLE_GEMINI_PRO_API_KEY'
    },
    'gemini-2-5-pro': {
        'api': 'google',
        'model_id': 'gemini-2.5-pro-preview-05-06',
        'api_key_env': 'GOOGLE_GEMINI_PRO_API_KEY'
    },
    'gemini-2-5-flash': {
        'api': 'google',
        'model_id': 'gemini-2.5-flash-preview-04-17',
        'api_key_env': 'GOOGLE_GEMINI_PRO_API_KEY'
    },
    'gemini-2-0-flash': {
        'api': 'google',
        'model_id': 'gemini-2.0-flash',
        'api_key_env': 'GOOGLE_GEMINI_PRO_API_KEY'
    },
    'gemini-1-5-flash': {
        'api': 'google',
        'model_id': 'gemini-1.5-flash',
        'api_key_env': 'GOOGLE_GEMINI_PRO_API_KEY'
    },

    # ===== ANTHROPIC CLAUDE =====
    'claude-3-7': {
        'api': 'anthropic',
        'model_id': 'claude-3-sonnet-20240229',
        'api_key_env': 'ANTHROPIC_API_KEY'
    },
    'claude-4-sonnet': {
        'api': 'anthropic',
        'model_id': 'claude-4-sonnet-20250514',
        'api_key_env': 'ANTHROPIC_API_KEY'
    },
    'claude-4-opus': {
        'api': 'anthropic',
        'model_id': 'claude-4-opus-20250320',
        'api_key_env': 'ANTHROPIC_API_KEY'
    },
    'claude-sonnet-4': {
        'api': 'anthropic',
        'model_id': 'claude-4-sonnet-20250514',
        'api_key_env': 'ANTHROPIC_API_KEY'
    },
    'claude-3-5-sonnet': {
        'api': 'anthropic',
        'model_id': 'claude-3-5-sonnet-20241022',
        'api_key_env': 'ANTHROPIC_API_KEY'
    },

    # ===== OPENAI =====
    'gpt-4-1': {
        'api': 'openai',
        'model_id': 'gpt-4-turbo-preview',
        'api_key_env': 'OPENAI_API_KEY'
    },
    'gpt-4o': {
        'api': 'openai',
        'model_id': 'gpt-4o',
        'api_key_env': 'OPENAI_API_KEY'
    },
    'gpt-4o-mini': {
        'api': 'openai',
        'model_id': 'gpt-4o-mini',
        'api_key_env': 'OPENAI_API_KEY'
    },
    'openai/gpt-oss-20b': {
        'api': 'together',
        'model_id': 'openai/gpt-oss-20b',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'openai/gpt-oss-120b': {
        'api': 'together',
        'model_id': 'openai/gpt-oss-120b',
        'api_key_env': 'TOGETHER_API_KEY'
    },

    # ===== TOGETHER AI - DEEPSEEK =====
    'deepseek-ai/DeepSeek-V3': {
        'api': 'together',
        'model_id': 'deepseek-ai/DeepSeek-V3',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'deepseek-ai/DeepSeek-V3.1': {
        'api': 'together',
        'model_id': 'deepseek-ai/DeepSeek-V3.1',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'deepseek-ai/DeepSeek-R1': {
        'api': 'together',
        'model_id': 'deepseek-ai/DeepSeek-R1',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'deepseek-ai/DeepSeek-R1-0528-tput': {
        'api': 'together',
        'model_id': 'deepseek-ai/DeepSeek-R1-0528-tput',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'deepseek-ai/DeepSeek-R1-Distill-Llama-70B': {
        'api': 'together',
        'model_id': 'deepseek-ai/DeepSeek-R1-Distill-Llama-70B',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free': {
        'api': 'together',
        'model_id': 'deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'deepseek-ai/DeepSeek-R1-Distill-Qwen-14B': {
        'api': 'together',
        'model_id': 'deepseek-ai/DeepSeek-R1-Distill-Qwen-14B',
        'api_key_env': 'TOGETHER_API_KEY'
    },

    # ===== TOGETHER AI - QWEN =====
    'Qwen/Qwen3-Next-80B-A3B-Instruct': {
        'api': 'together',
        'model_id': 'Qwen/Qwen3-Next-80B-A3B-Instruct',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'Qwen/Qwen3-Next-80B-A3B-Thinking': {
        'api': 'together',
        'model_id': 'Qwen/Qwen3-Next-80B-A3B-Thinking',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'Qwen/Qwen3-235B-A22B-Thinking-2507': {
        'api': 'together',
        'model_id': 'Qwen/Qwen3-235B-A22B-Thinking-2507',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'Qwen/Qwen3-235B-A22B-Instruct-2507-tput': {
        'api': 'together',
        'model_id': 'Qwen/Qwen3-235B-A22B-Instruct-2507-tput',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'Qwen/Qwen3-235B-A22B-fp8-tput': {
        'api': 'together',
        'model_id': 'Qwen/Qwen3-235B-A22B-fp8-tput',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8': {
        'api': 'together',
        'model_id': 'Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'Qwen/Qwen2.5-VL-72B-Instruct': {
        'api': 'together',
        'model_id': 'Qwen/Qwen2.5-VL-72B-Instruct',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'Qwen/Qwen2.5-72B-Instruct-Turbo': {
        'api': 'together',
        'model_id': 'Qwen/Qwen2.5-72B-Instruct-Turbo',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'Qwen/Qwen2.5-Coder-32B-Instruct': {
        'api': 'together',
        'model_id': 'Qwen/Qwen2.5-Coder-32B-Instruct',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'Qwen/QwQ-32B': {
        'api': 'together',
        'model_id': 'Qwen/QwQ-32B',
        'api_key_env': 'TOGETHER_API_KEY'
    },

    # ===== TOGETHER AI - META LLAMA =====
    'meta-llama/Llama-4-Maverick-Instruct': {
        'api': 'together',
        'model_id': 'meta-llama/Llama-4-Maverick-Instruct',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8': {
        'api': 'together',
        'model_id': 'meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'meta-llama/Llama-4-Scout-Instruct': {
        'api': 'together',
        'model_id': 'meta-llama/Llama-4-Scout-Instruct',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'meta-llama/Llama-4-Scout-17B-16E-Instruct': {
        'api': 'together',
        'model_id': 'meta-llama/Llama-4-Scout-17B-16E-Instruct',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'meta-llama/Llama-3.3-70B-Instruct-Turbo': {
        'api': 'together',
        'model_id': 'meta-llama/Llama-3.3-70B-Instruct-Turbo',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free': {
        'api': 'together',
        'model_id': 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo': {
        'api': 'together',
        'model_id': 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo': {
        'api': 'together',
        'model_id': 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo': {
        'api': 'together',
        'model_id': 'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'meta-llama/Meta-Llama-3-70B-Instruct-Turbo': {
        'api': 'together',
        'model_id': 'meta-llama/Meta-Llama-3-70B-Instruct-Turbo',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'meta-llama/Meta-Llama-3-8B-Instruct-Lite': {
        'api': 'together',
        'model_id': 'meta-llama/Meta-Llama-3-8B-Instruct-Lite',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'meta-llama/Llama-3.2-3B-Instruct-Turbo': {
        'api': 'together',
        'model_id': 'meta-llama/Llama-3.2-3B-Instruct-Turbo',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'meta-llama/Llama-3-70b-chat-hf': {
        'api': 'together',
        'model_id': 'meta-llama/Llama-3-70b-chat-hf',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'meta-llama/Llama-2-70b-hf': {
        'api': 'together',
        'model_id': 'meta-llama/Llama-2-70b-hf',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'meta-llama/Llama-Guard-4-12B': {
        'api': 'together',
        'model_id': 'meta-llama/Llama-Guard-4-12B',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'meta-llama/Llama-Guard-3-11B-Vision-Turbo': {
        'api': 'together',
        'model_id': 'meta-llama/Llama-Guard-3-11B-Vision-Turbo',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'meta-llama/Meta-Llama-Guard-3-8B': {
        'api': 'together',
        'model_id': 'meta-llama/Meta-Llama-Guard-3-8B',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'meta-llama/LlamaGuard-2-8b': {
        'api': 'together',
        'model_id': 'meta-llama/LlamaGuard-2-8b',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo': {
        'api': 'together',
        'model_id': 'meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo',
        'api_key_env': 'TOGETHER_API_KEY'
    },

    # ===== TOGETHER AI - MISTRAL =====
    'mistralai/Mistral-Small-24B-Instruct-2501': {
        'api': 'together',
        'model_id': 'mistralai/Mistral-Small-24B-Instruct-2501',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'mistralai/Mixtral-8x7B-Instruct-v0.1': {
        'api': 'together',
        'model_id': 'mistralai/Mixtral-8x7B-Instruct-v0.1',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'mistralai/Mistral-7B-Instruct-v0.3': {
        'api': 'together',
        'model_id': 'mistralai/Mistral-7B-Instruct-v0.3',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'mistralai/Mistral-7B-Instruct-v0.2': {
        'api': 'together',
        'model_id': 'mistralai/Mistral-7B-Instruct-v0.2',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'mistralai/Mistral-7B-Instruct-v0.1': {
        'api': 'together',
        'model_id': 'mistralai/Mistral-7B-Instruct-v0.1',
        'api_key_env': 'TOGETHER_API_KEY'
    },

    # ===== TOGETHER AI - OTROS MODELOS =====
    'moonshotai/Kimi-K2-Instruct-0905': {
        'api': 'together',
        'model_id': 'moonshotai/Kimi-K2-Instruct-0905',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'moonshotai/Kimi-K2-Instruct': {
        'api': 'together',
        'model_id': 'moonshotai/Kimi-K2-Instruct',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'google/gemma-3n-E4B-it': {
        'api': 'together',
        'model_id': 'google/gemma-3n-E4B-it',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'zai-org/GLM-4.5-Air-FP8': {
        'api': 'together',
        'model_id': 'zai-org/GLM-4.5-Air-FP8',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'lgai/exaone-3-5-32b-instruct': {
        'api': 'together',
        'model_id': 'lgai/exaone-3-5-32b-instruct',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'lgai/exaone-deep-32b': {
        'api': 'together',
        'model_id': 'lgai/exaone-deep-32b',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'SCB10X/Typhoon-2-70B-Instruct': {
        'api': 'together',
        'model_id': 'SCB10X/Typhoon-2-70B-Instruct',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'scb10x/scb10x-typhoon-2-1-gemma3-12b': {
        'api': 'together',
        'model_id': 'scb10x/scb10x-typhoon-2-1-gemma3-12b',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'upstage/SOLAR-10.7B-Instruct-v1.0': {
        'api': 'together',
        'model_id': 'upstage/SOLAR-10.7B-Instruct-v1.0',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'marin-community/marin-8b-instruct': {
        'api': 'together',
        'model_id': 'marin-community/marin-8b-instruct',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'arcee-ai/AFM-4.5B': {
        'api': 'together',
        'model_id': 'arcee-ai/AFM-4.5B',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'arcee_ai/arcee-spotlight': {
        'api': 'together',
        'model_id': 'arcee_ai/arcee-spotlight',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'arcee-ai/virtuoso-large': {
        'api': 'together',
        'model_id': 'arcee-ai/virtuoso-large',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'arcee-ai/coder-large': {
        'api': 'together',
        'model_id': 'arcee-ai/coder-large',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'arcee-ai/maestro-reasoning': {
        'api': 'together',
        'model_id': 'arcee-ai/maestro-reasoning',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'deepcogito/cogito-v2-preview-deepseek-671b': {
        'api': 'together',
        'model_id': 'deepcogito/cogito-v2-preview-deepseek-671b',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'deepcogito/cogito-v2-preview-llama-405B': {
        'api': 'together',
        'model_id': 'deepcogito/cogito-v2-preview-llama-405B',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'togethercomputer/Refuel-Llm-V2-Small': {
        'api': 'together',
        'model_id': 'togethercomputer/Refuel-Llm-V2-Small',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'togethercomputer/Refuel-Llm-V2': {
        'api': 'together',
        'model_id': 'togethercomputer/Refuel-Llm-V2',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'intfloat/multilingual-e5-large-instruct': {
        'api': 'together',
        'model_id': 'intfloat/multilingual-e5-large-instruct',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'Alibaba-NLP/gte-modernbert-base': {
        'api': 'together',
        'model_id': 'Alibaba-NLP/gte-modernbert-base',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'BAAI/bge-large-en-v1.5': {
        'api': 'together',
        'model_id': 'BAAI/bge-large-en-v1.5',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'BAAI/bge-base-en-v1.5': {
        'api': 'together',
        'model_id': 'BAAI/bge-base-en-v1.5',
        'api_key_env': 'TOGETHER_API_KEY'
    },

    # ===== MODELOS DE IMAGEN =====
    'deepseek-v3': {
        'api': 'together',
        'model_id': 'deepseek-ai/DeepSeek-V3',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'deepseek-chat': {
        'api': 'together',
        'model_id': 'deepseek-ai/DeepSeek-Chat',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'flux-1-pro': {
        'api': 'together',
        'model_id': 'black-forest-labs/FLUX.1-pro',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'kling-ai': {
        'api': 'together',
        'model_id': 'kling-ai/kling-video',
        'api_key_env': 'TOGETHER_API_KEY'
    },
    'ideogram': {
        'api': 'ideogram',
        'model_id': 'ideogram-ai/ideogram-v2',
        'api_key_env': 'IDEOGRAM_API_KEY'
    },
    'dall-e-3': {
        'api': 'openai',
        'model_id': 'dall-e-3',
        'api_key_env': 'OPENAI_API_KEY'
    },
    'leonardo-ai': {
        'api': 'leonardo',
        'model_id': 'leonardo-ai/leonardo-vision-xl',
        'api_key_env': 'LEONARDO_API_KEY'
    }
}