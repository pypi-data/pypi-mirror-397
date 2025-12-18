"""
Job submission and monitoring utilities for integration tests
"""
import time
import subprocess
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class JobResult:
    success: bool
    job_id: str
    execution_time: float
    output_location: Optional[str] = None
    error_message: Optional[str] = None


class JobRunner(ABC):
    """Abstract base class for job runners"""

    @abstractmethod
    def submit_job(self, script_path: str, module_name: str, job_args: Dict[str, Any],
                   script_args: Optional[List[str]] = None) -> str:
        """Submit a job and return job ID"""
        pass

    @abstractmethod
    def wait_for_completion(self, job_id: str, timeout: int = 300) -> JobResult:
        """Wait for job completion and return result"""
        pass


class DockerSparkRunner(JobRunner):
    """Run Spark jobs in Docker container"""

    def __init__(self, docker_dir: str = None):
        self.docker_dir = docker_dir or os.path.join(os.getcwd(), "docker")
        self.job_counter = 0

    def submit_job(self, script_path: str, module_name: str, job_args: Dict[str, Any],
                   script_args: Optional[List[str]] = None) -> str:
        """Submit job to Docker Spark"""
        self.job_counter += 1
        job_id = f"job_{int(time.time())}_{self.job_counter}"

        # Prepare arguments for the generic entry script
        args_list = []

        # Add script args if provided
        if script_args:
            args_list.extend(script_args)

        # Add module name if provided
        if module_name:
            args_list.extend(["--module_name", module_name])

        # Add job arguments
        for k, v in job_args.items():
            args_list.extend([f"--{k}", str(v)])

        # Store job details for wait_for_completion
        self.current_job = {
            "id": job_id,
            "script_path": script_path,
            "args": args_list
        }

        return job_id

    def wait_for_completion(self, job_id: str, timeout: int = 300) -> JobResult:
        """Run the job in Docker Spark and wait for completion"""
        if not hasattr(self, "current_job") or self.current_job["id"] != job_id:
            return JobResult(
                success=False,
                job_id=job_id,
                execution_time=0,
                error_message="Job not found or already completed"
            )

        start_time = time.time()
        script_path = self.current_job["script_path"]
        args = self.current_job["args"]

        # Build the docker-compose command
        cmd = [
                  "docker-compose", "-f", "docker-compose.yml", "run", "--rm",
                  "--entrypoint", script_path,
                  "spark-submit"
              ] + args

        try:
            # Run the command
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.docker_dir,
                timeout=timeout
            )

            execution_time = time.time() - start_time

            if process.returncode == 0:
                return JobResult(
                    success=True,
                    job_id=job_id,
                    execution_time=execution_time
                )
            else:
                return JobResult(
                    success=False,
                    job_id=job_id,
                    execution_time=execution_time,
                    error_message=f"Job failed with exit code {process.returncode}\n{process.stderr}"
                )

        except subprocess.TimeoutExpired:
            return JobResult(
                success=False,
                job_id=job_id,
                execution_time=timeout,
                error_message="Job timed out"
            )
        except Exception as e:
            return JobResult(
                success=False,
                job_id=job_id,
                execution_time=time.time() - start_time,
                error_message=f"Error running job: {str(e)}"
            )
