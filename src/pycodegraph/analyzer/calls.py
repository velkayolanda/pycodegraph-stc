"""Call sequence extractor - generates calls.json from Python AST."""

# TODO: Implement calls.json extraction
# - Custom ast.NodeVisitor for evaluation-order traversal
# - Extract call sequences per function/method
# - Track control-flow stack (if/elif/else, for, while, try/except/finally, with)
# - Handle nested calls, chained calls
# - Generate block_id for control-flow grouping
