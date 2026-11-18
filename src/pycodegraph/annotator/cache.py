"""SHA-256 keyed local cache for LLM responses."""

# TODO: Implement cache
# - Cache key = SHA-256(entity source + prompt version + model name + callee list)
# - Disk-based storage in .pycodegraph_cache/
# - Cache hit/miss detection
# - Invalidation when prompt/model/code changes
# - --no-cache and --refresh flags support
