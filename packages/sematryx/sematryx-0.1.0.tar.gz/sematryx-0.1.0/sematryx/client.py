"""
Sematryx SDK Client
"""

from typing import Any, Callable, Dict, List, Optional, Union
import httpx

from .models import (
    OptimizationRequest,
    OptimizationResult,
    Variable,
    Constraint,
    LearningConfig,
    UsageInfo,
    HealthStatus,
)
from .exceptions import (
    SematryxError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    OptimizationError,
    ConnectionError,
)


DEFAULT_BASE_URL = "https://api.sematryx.com"
DEFAULT_TIMEOUT = 300.0  # 5 minutes for optimization


class Sematryx:
    """
    Sematryx Python SDK Client
    
    Example:
        client = Sematryx(api_key="sk-...")
        
        result = client.optimize(
            objective="minimize",
            variables=[
                {"name": "x", "bounds": (-5, 5)},
                {"name": "y", "bounds": (-5, 5)},
            ],
            objective_function="x**2 + y**2",
        )
        
        print(result.solution)  # {'x': 0.0, 'y': 0.0}
        print(result.explanation)  # "Converged to global minimum..."
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Initialize Sematryx client.
        
        Args:
            api_key: Your Sematryx API key (starts with 'sk-')
            base_url: API base URL (default: https://api.sematryx.com)
            timeout: Request timeout in seconds (default: 300)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "sematryx-python/0.1.0",
            },
            timeout=timeout,
        )
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
    
    def close(self):
        """Close the HTTP client"""
        self._client.close()
    
    def _handle_response(self, response: httpx.Response) -> dict:
        """Handle API response and raise appropriate exceptions"""
        if response.status_code == 200:
            return response.json()
        
        try:
            error_data = response.json()
            message = error_data.get("detail", error_data.get("message", "Unknown error"))
        except Exception:
            message = response.text or "Unknown error"
        
        if response.status_code == 401:
            raise AuthenticationError(message, status_code=401)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message, 
                status_code=429, 
                retry_after=int(retry_after) if retry_after else None
            )
        elif response.status_code == 422:
            errors = error_data.get("errors", []) if isinstance(error_data, dict) else []
            raise ValidationError(message, status_code=422, errors=errors)
        elif response.status_code >= 500:
            raise SematryxError(f"Server error: {message}", status_code=response.status_code)
        else:
            raise SematryxError(message, status_code=response.status_code)
    
    def optimize(
        self,
        objective: str = "minimize",
        variables: List[Union[Variable, Dict[str, Any]]] = None,
        objective_function: Optional[str] = None,
        constraints: List[Union[Constraint, Dict[str, Any]]] = None,
        max_evaluations: int = 1000,
        strategy: str = "auto",
        explanation_level: int = 2,
        learning: Optional[Union[LearningConfig, Dict[str, Any]]] = None,
        domain: Optional[str] = None,
        **kwargs,
    ) -> OptimizationResult:
        """
        Run an optimization.
        
        Args:
            objective: "minimize" or "maximize"
            variables: List of variable definitions with names and bounds
            objective_function: String expression for the objective (e.g., "x**2 + y**2")
            constraints: List of constraint definitions
            max_evaluations: Maximum function evaluations
            strategy: Optimization strategy ("auto", "bayesian", "evolutionary", "gradient")
            explanation_level: 0-4, higher = more detailed explanations
            learning: Private Learning Store configuration
            domain: Domain hint (financial, healthcare, supply_chain, etc.)
            **kwargs: Additional parameters
            
        Returns:
            OptimizationResult with solution, explanation, and audit trail
            
        Example:
            result = client.optimize(
                objective="minimize",
                variables=[
                    {"name": "x", "bounds": (-5, 5)},
                    {"name": "y", "bounds": (-5, 5)},
                ],
                objective_function="x**2 + y**2",
                explanation_level=3,
            )
        """
        # Convert dicts to models
        if variables:
            variables = [
                Variable(**v) if isinstance(v, dict) else v 
                for v in variables
            ]
        
        if constraints:
            constraints = [
                Constraint(**c) if isinstance(c, dict) else c
                for c in constraints
            ]
        
        if learning and isinstance(learning, dict):
            learning = LearningConfig(**learning)
        
        request = OptimizationRequest(
            objective=objective,
            variables=variables or [],
            objective_function=objective_function,
            constraints=constraints or [],
            max_evaluations=max_evaluations,
            strategy=strategy,
            explanation_level=explanation_level,
            learning=learning,
            domain=domain,
            metadata=kwargs,
        )
        
        try:
            response = self._client.post(
                "/v1/optimize",
                json=request.model_dump(exclude_none=True),
            )
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to Sematryx API: {e}")
        except httpx.TimeoutException:
            raise SematryxError("Request timed out. Try increasing the timeout or reducing max_evaluations.")
        
        data = self._handle_response(response)
        
        return OptimizationResult(
            success=data.get("success", True),
            solution=data.get("solution", {}),
            objective_value=data.get("objective_value", 0.0),
            constraints_satisfied=data.get("constraints_satisfied", True),
            evaluations_used=data.get("evaluations_used", 0),
            duration_seconds=data.get("duration_seconds", 0.0),
            strategy_used=data.get("strategy_used", "unknown"),
            explanation=data.get("explanation"),
            explanation_detail=data.get("explanation_detail"),
            audit_id=data.get("audit_id"),
            learning_operations=data.get("learning_operations"),
            raw_response=data,
        )
    
    def get_usage(self) -> UsageInfo:
        """Get current usage information for your account"""
        response = self._client.get("/v1/usage")
        data = self._handle_response(response)
        return UsageInfo(**data)
    
    def health(self) -> HealthStatus:
        """Check API health status"""
        response = self._client.get("/health")
        data = self._handle_response(response)
        return HealthStatus(**data)
    
    # Convenience methods for common domains
    
    def optimize_portfolio(
        self,
        assets: List[str],
        returns: List[float],
        covariance: List[List[float]],
        target_return: Optional[float] = None,
        max_position: float = 1.0,
        **kwargs,
    ) -> OptimizationResult:
        """
        Portfolio optimization with financial constraints.
        
        Args:
            assets: List of asset names
            returns: Expected returns for each asset
            covariance: Covariance matrix
            target_return: Minimum target return (optional)
            max_position: Maximum weight per asset
            **kwargs: Additional optimization parameters
        """
        return self.optimize(
            domain="financial",
            variables=[
                {"name": asset, "bounds": (0, max_position)} 
                for asset in assets
            ],
            constraints=[
                {"expression": f"sum([{', '.join(assets)}]) == 1", "type": "equality"},
            ] + ([
                {"expression": f"sum([r * w for r, w in zip({returns}, [{', '.join(assets)}])]) >= {target_return}", "type": "inequality"}
            ] if target_return else []),
            metadata={
                "problem_type": "portfolio",
                "returns": returns,
                "covariance": covariance,
            },
            **kwargs,
        )
    
    def optimize_supply_chain(
        self,
        nodes: List[str],
        demands: Dict[str, float],
        capacities: Dict[str, float],
        costs: Dict[str, Dict[str, float]],
        **kwargs,
    ) -> OptimizationResult:
        """
        Supply chain routing optimization.
        
        Args:
            nodes: List of node names (warehouses, customers, etc.)
            demands: Demand at each node
            capacities: Capacity at each node  
            costs: Cost matrix between nodes
            **kwargs: Additional optimization parameters
        """
        return self.optimize(
            domain="supply_chain",
            metadata={
                "problem_type": "routing",
                "nodes": nodes,
                "demands": demands,
                "capacities": capacities,
                "costs": costs,
            },
            **kwargs,
        )


class AsyncSematryx:
    """
    Async Sematryx Python SDK Client
    
    Example:
        async with AsyncSematryx(api_key="sk-...") as client:
            result = await client.optimize(
                objective="minimize",
                variables=[{"name": "x", "bounds": (-5, 5)}],
                objective_function="x**2",
            )
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "sematryx-python/0.1.0",
            },
            timeout=timeout,
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        await self.close()
    
    async def close(self):
        await self._client.aclose()
    
    async def _handle_response(self, response: httpx.Response) -> dict:
        """Handle API response and raise appropriate exceptions"""
        if response.status_code == 200:
            return response.json()
        
        try:
            error_data = response.json()
            message = error_data.get("detail", error_data.get("message", "Unknown error"))
        except Exception:
            message = response.text or "Unknown error"
        
        if response.status_code == 401:
            raise AuthenticationError(message, status_code=401)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message,
                status_code=429,
                retry_after=int(retry_after) if retry_after else None
            )
        elif response.status_code == 422:
            errors = error_data.get("errors", []) if isinstance(error_data, dict) else []
            raise ValidationError(message, status_code=422, errors=errors)
        elif response.status_code >= 500:
            raise SematryxError(f"Server error: {message}", status_code=response.status_code)
        else:
            raise SematryxError(message, status_code=response.status_code)
    
    async def optimize(
        self,
        objective: str = "minimize",
        variables: List[Union[Variable, Dict[str, Any]]] = None,
        objective_function: Optional[str] = None,
        constraints: List[Union[Constraint, Dict[str, Any]]] = None,
        max_evaluations: int = 1000,
        strategy: str = "auto",
        explanation_level: int = 2,
        learning: Optional[Union[LearningConfig, Dict[str, Any]]] = None,
        domain: Optional[str] = None,
        **kwargs,
    ) -> OptimizationResult:
        """Async version of optimize. See Sematryx.optimize for documentation."""
        # Convert dicts to models
        if variables:
            variables = [
                Variable(**v) if isinstance(v, dict) else v
                for v in variables
            ]
        
        if constraints:
            constraints = [
                Constraint(**c) if isinstance(c, dict) else c
                for c in constraints
            ]
        
        if learning and isinstance(learning, dict):
            learning = LearningConfig(**learning)
        
        request = OptimizationRequest(
            objective=objective,
            variables=variables or [],
            objective_function=objective_function,
            constraints=constraints or [],
            max_evaluations=max_evaluations,
            strategy=strategy,
            explanation_level=explanation_level,
            learning=learning,
            domain=domain,
            metadata=kwargs,
        )
        
        try:
            response = await self._client.post(
                "/v1/optimize",
                json=request.model_dump(exclude_none=True),
            )
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to Sematryx API: {e}")
        except httpx.TimeoutException:
            raise SematryxError("Request timed out. Try increasing the timeout or reducing max_evaluations.")
        
        data = await self._handle_response(response)
        
        return OptimizationResult(
            success=data.get("success", True),
            solution=data.get("solution", {}),
            objective_value=data.get("objective_value", 0.0),
            constraints_satisfied=data.get("constraints_satisfied", True),
            evaluations_used=data.get("evaluations_used", 0),
            duration_seconds=data.get("duration_seconds", 0.0),
            strategy_used=data.get("strategy_used", "unknown"),
            explanation=data.get("explanation"),
            explanation_detail=data.get("explanation_detail"),
            audit_id=data.get("audit_id"),
            learning_operations=data.get("learning_operations"),
            raw_response=data,
        )
    
    async def get_usage(self) -> UsageInfo:
        response = await self._client.get("/v1/usage")
        data = await self._handle_response(response)
        return UsageInfo(**data)
    
    async def health(self) -> HealthStatus:
        response = await self._client.get("/health")
        data = await self._handle_response(response)
        return HealthStatus(**data)

