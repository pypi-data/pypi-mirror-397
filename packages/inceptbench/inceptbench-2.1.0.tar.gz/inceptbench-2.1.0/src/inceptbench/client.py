"""Local evaluator client for Incept"""
from .orchestrator import universal_unified_benchmark, benchmark_parallel, UniversalEvaluationRequest, evaluate_with_routing

class InceptClient:
    def __init__(self, api_key=None, base_url=None, timeout=600):
        """
        Local evaluator client - runs universal_unified_benchmark directly.

        Args:
            api_key: Not used (kept for backward compatibility)
            base_url: Not used (kept for backward compatibility)
            timeout: Not used (kept for backward compatibility)
        """
        self.timeout = timeout

    def evaluate_dict(self, data):
        """
        Evaluate questions using routing function that handles both legacy and new evaluators.

        Args:
            data: Dictionary containing the evaluation request

        Returns:
            Dictionary with evaluation results
        """
        # Call routing function which handles both legacy and new evaluators
        # The routing function will check for 'use_new_evaluator' flag in data
        return evaluate_with_routing(data)

    def benchmark(self, data, max_workers=100):
        """
        Benchmark mode: Process many questions in parallel.

        Args:
            data: Dictionary containing the evaluation request
            max_workers: Number of parallel workers (default: 100)

        Returns:
            Dictionary with benchmark results including scores and failed IDs
        """
        # Ensure max_threads is set for routing function
        if 'max_threads' not in data:
            data['max_threads'] = max_workers
        
        # Use routing function for consistent behavior
        return evaluate_with_routing(data)
