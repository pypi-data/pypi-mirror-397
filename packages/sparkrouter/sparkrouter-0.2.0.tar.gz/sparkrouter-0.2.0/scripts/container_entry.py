#!/usr/bin/env python
"""
Container Entry Point Script
============================

Use this script as the entrypoint for Docker/Kubernetes jobs.

Usage:
    python container_entry.py \
        --module_name mypackage.jobs.my_job_factory \
        --my_job '{"config": "value"}'

In Dockerfile:
    FROM python:3.11-slim
    RUN pip install sparkrouter mypackage
    COPY container_entry.py /app/
    ENTRYPOINT ["python", "/app/container_entry.py"]
"""

from sparkrouter.entry_points.container import main

if __name__ == "__main__":
    main()
