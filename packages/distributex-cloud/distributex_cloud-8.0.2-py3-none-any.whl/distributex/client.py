"""DistributeX client for Python."""

import time
from typing import Optional, List, Dict, Any
import requests

from .exceptions import (
    DistributeXError,
    AuthenticationError,
    JobError,
    RateLimitError,
)


class DistributeX:
    """
    DistributeX client for submitting and managing distributed computing jobs.
    
    Example:
        >>> import distributex
        >>> dx = distributex.DistributeX(api_key="your-api-key")
        >>> 
        >>> # Submit a Python job
        >>> job = dx.submit_python('''
        ... def fibonacci(n):
        ...     if n <= 1:
        ...         return n
        ...     return fibonacci(n-1) + fibonacci(n-2)
        ... 
        ... for i in range(10):
        ...     print(f"Fib({i}) = {fibonacci(i)}")
        ... ''')
        >>> 
        >>> # Wait for completion
        >>> result = job.wait()
        >>> print(result.output)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://distributex.cloud",
        timeout: int = 30,
    ):
        """
        Initialize DistributeX client.
        
        Args:
            api_key: Your DistributeX API key. Get one from distributex.cloud/dashboard
            base_url: API base URL (default: https://distributex.cloud)
            timeout: Request timeout in seconds
        """
        if not api_key:
            raise AuthenticationError(
                "API key required. Get one from https://distributex.cloud/dashboard"
            )
        
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })
    
    def submit_python(
        self,
        script: str,
        dependencies: Optional[List[str]] = None,
        priority: int = 0,
    ) -> "Job":
        """
        Submit a Python script for distributed execution.
        
        Args:
            script: Python code to execute
            dependencies: List of pip packages to install (e.g., ["numpy", "pandas"])
            priority: Job priority (0-10, higher = more important)
            
        Returns:
            Job object for tracking execution
            
        Example:
            >>> job = dx.submit_python('''
            ... import numpy as np
            ... data = np.random.rand(100)
            ... print(f"Mean: {data.mean()}")
            ... ''', dependencies=["numpy"])
        """
        return self._submit_job(script, "python", dependencies, priority)
    
    def submit_javascript(
        self,
        script: str,
        dependencies: Optional[List[str]] = None,
        priority: int = 0,
    ) -> "Job":
        """
        Submit a JavaScript/Node.js script for distributed execution.
        
        Args:
            script: JavaScript code to execute
            dependencies: List of npm packages to install (e.g., ["lodash", "axios"])
            priority: Job priority (0-10, higher = more important)
            
        Returns:
            Job object for tracking execution
        """
        return self._submit_job(script, "javascript", dependencies, priority)
    
    def _submit_job(
        self,
        script: str,
        language: str,
        dependencies: Optional[List[str]],
        priority: int,
    ) -> "Job":
        """Internal method to submit a job."""
        try:
            response = self._session.post(
                f"{self.base_url}/api/jobs",
                json={
                    "script": script,
                    "language": language,
                    "dependencies": dependencies,
                    "priority": priority,
                },
                timeout=self.timeout,
            )
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code >= 400:
                error_msg = response.json().get("error", "Unknown error")
                raise JobError(f"Failed to submit job: {error_msg}")
            
            job_data = response.json()
            return Job(self, job_data["id"], job_data)
            
        except requests.RequestException as e:
            raise DistributeXError(f"Network error: {str(e)}")
    
    def get_job(self, job_id: str) -> "Job":
        """
        Get a job by ID.
        
        Args:
            job_id: The job ID
            
        Returns:
            Job object
        """
        try:
            response = self._session.get(
                f"{self.base_url}/api/jobs/{job_id}",
                timeout=self.timeout,
            )
            
            if response.status_code == 404:
                raise JobError(f"Job not found: {job_id}")
            elif response.status_code >= 400:
                raise JobError(f"Failed to get job: {response.text}")
            
            job_data = response.json()
            return Job(self, job_id, job_data)
            
        except requests.RequestException as e:
            raise DistributeXError(f"Network error: {str(e)}")
    
    def list_jobs(self, limit: int = 100) -> List["Job"]:
        """
        List recent jobs.
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of Job objects
        """
        try:
            response = self._session.get(
                f"{self.base_url}/api/jobs",
                params={"limit": limit},
                timeout=self.timeout,
            )
            
            if response.status_code >= 400:
                raise JobError(f"Failed to list jobs: {response.text}")
            
            jobs_data = response.json()
            return [Job(self, job["id"], job) for job in jobs_data]
            
        except requests.RequestException as e:
            raise DistributeXError(f"Network error: {str(e)}")


class Job:
    """Represents a distributed computing job."""
    
    def __init__(self, client: DistributeX, job_id: str, data: Dict[str, Any]):
        self._client = client
        self.id = job_id
        self._data = data
    
    @property
    def status(self) -> str:
        """Get job status: pending, queued, running, completed, or failed."""
        return self._data.get("status", "unknown")
    
    @property
    def output(self) -> Optional[str]:
        """Get job output (stdout)."""
        return self._data.get("output")
    
    @property
    def error(self) -> Optional[str]:
        """Get job error output (stderr)."""
        return self._data.get("errorOutput")
    
    @property
    def language(self) -> str:
        """Get job language (python or javascript)."""
        return self._data.get("language", "unknown")
    
    @property
    def worker_id(self) -> Optional[str]:
        """Get ID of worker executing this job."""
        return self._data.get("workerId")
    
    def refresh(self) -> "Job":
        """Refresh job data from server."""
        job = self._client.get_job(self.id)
        self._data = job._data
        return self
    
    def wait(
        self,
        timeout: Optional[float] = None,
        poll_interval: float = 2.0,
    ) -> "Job":
        """
        Wait for job to complete.
        
        Args:
            timeout: Maximum time to wait in seconds (None = wait forever)
            poll_interval: How often to check status in seconds
            
        Returns:
            Self with updated data
            
        Raises:
            JobError: If job fails or timeout is reached
        """
        start_time = time.time()
        
        while True:
            self.refresh()
            
            if self.status in ("completed", "failed"):
                if self.status == "failed":
                    raise JobError(f"Job failed: {self.error}")
                return self
            
            if timeout and (time.time() - start_time) > timeout:
                raise JobError(f"Timeout waiting for job {self.id}")
            
            time.sleep(poll_interval)
    
    def __repr__(self) -> str:
        return f"Job(id='{self.id}', status='{self.status}', language='{self.language}')"
