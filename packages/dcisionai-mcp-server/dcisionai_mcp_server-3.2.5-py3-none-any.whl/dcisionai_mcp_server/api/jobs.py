"""
REST API Endpoints for Async Job Queue

This module provides FastAPI endpoints for:
- Job submission (POST /api/jobs/optimize)
- Job status polling (GET /api/jobs/{job_id}/status)
- Job result retrieval (GET /api/jobs/{job_id}/result)
- Job listing (GET /api/jobs)
- Job cancellation (POST /api/jobs/{job_id}/cancel)

Following MCP Protocol:
- HATEOAS links for navigation
- Job resources exposed via job:// URIs
- Compatible with existing MCP tools

Following LangGraph Best Practices:
- Jobs execute Dame Workflow with TypedDict state
- Progress callbacks update JobState
- Checkpointing supports resumable workflows
"""

import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from dcisionai_mcp_server.jobs import (
    # Schemas
    JobStatus,
    JobPriority,
    # Tasks
    run_optimization_job,
    cancel_job,
    get_task_status,
    # Storage
    create_job_record,
    get_job,
    get_all_jobs,
    get_jobs_by_session,
    get_jobs_by_status,
    get_job_statistics,
)

from dcisionai_mcp_server.resources.jobs import (
    read_job_resource,
    list_job_resources,
)

logger = logging.getLogger(__name__)

# Create FastAPI router
router = APIRouter(prefix="/api/jobs", tags=["jobs"])


# ========== REQUEST/RESPONSE MODELS ==========

class JobSubmitRequest(BaseModel):
    """Request body for job submission"""
    user_query: str = Field(..., description="Natural language optimization query")
    session_id: str = Field(..., description="Session identifier for context")
    priority: str = Field(default="normal", description="Job priority: low, normal, high, urgent")
    use_case: Optional[str] = Field(None, description="Optional use case hint (e.g., 'VRP', 'client_advisor_matching')")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Optional additional parameters")


class JobSubmitResponse(BaseModel):
    """Response for job submission"""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Current job status")
    priority: str = Field(..., description="Job priority")
    created_at: str = Field(..., description="Job creation timestamp (ISO 8601)")
    links: Dict[str, str] = Field(..., description="HATEOAS navigation links")


class JobStatusResponse(BaseModel):
    """Response for job status polling"""
    job_id: str
    session_id: str
    status: str
    priority: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    user_query: str
    use_case: Optional[str] = None
    progress: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    links: Dict[str, str]


class JobResultResponse(BaseModel):
    """Response for job result retrieval"""
    job_id: str
    status: str
    completed_at: str
    result: Dict[str, Any]
    links: Dict[str, str]


class JobListResponse(BaseModel):
    """Response for job listing"""
    jobs: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    links: Dict[str, str]


class JobCancelResponse(BaseModel):
    """Response for job cancellation"""
    job_id: str
    status: str
    cancelled_at: str
    message: str


# ========== ENDPOINTS ==========

@router.post("/submit", response_model=JobSubmitResponse, status_code=202)
async def submit_workflow_job(request: Request):
    """
    Submit a new optimization job (simplified endpoint for React client).

    This endpoint accepts workflow parameters from the React MCP client and dispatches
    them to the async job queue for background processing.

    **Expected Request Body from React Client:**
    ```json
    {
        "problem_description": "Optimize delivery routes...",
        "enabled_features": ["vagueness_detection", "template_matching"],
        "enabled_tools": ["intent_discovery", "data_preparation", "solver"],
        "reasoning_model": "claude-3-5-haiku-20241022",
        "code_model": "claude-3-5-sonnet-20241022",
        "enable_validation": false,
        "enable_templates": true,
        "use_claude_sdk_for_pyomo": true,
        "use_parallel_execution": false,
        "template_hint": null,
        "priority": "normal",
        "use_case": null
    }
    ```

    **Response (202 Accepted):**
    ```json
    {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "queued",
        "priority": "normal",
        "created_at": "2025-12-08T12:00:00Z",
        "links": {
            "self": "/api/jobs/550e8400-e29b-41d4-a716-446655440000",
            "status": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/status",
            "progress": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/progress",
            "result": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/result"
        }
    }
    ```
    """
    import json
    body = await request.json()

    logger.info(f"Received workflow job submission: {body.get('problem_description', '')[:100]}...")

    # Extract fields from request body
    problem_description = body.get("problem_description", "")
    if not problem_description:
        raise HTTPException(status_code=400, detail="problem_description is required")

    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Use a default session ID if not provided (React client doesn't send this)
    # Format: session_{job_id} so we can extract full job_id later
    session_id = body.get("session_id", f"session_{job_id}")

    # Validate priority
    priority_str = body.get("priority", "normal")
    try:
        priority = JobPriority[priority_str.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority: {priority_str}. Must be one of: low, normal, high, urgent"
        )

    # Prepare workflow parameters
    parameters = {
        "enabled_features": body.get("enabled_features", []),
        "enabled_tools": body.get("enabled_tools", []),
        "reasoning_model": body.get("reasoning_model", "claude-3-5-haiku-20241022"),
        "code_model": body.get("code_model", "claude-3-5-sonnet-20241022"),
        "enable_validation": body.get("enable_validation", False),
        "enable_templates": body.get("enable_templates", True),
        "use_claude_sdk_for_pyomo": body.get("use_claude_sdk_for_pyomo", True),
        "use_parallel_execution": body.get("use_parallel_execution", False),
        "template_hint": body.get("template_hint"),
    }

    use_case = body.get("use_case")

    # Create job record in database
    try:
        job_record = create_job_record(
            job_id=job_id,
            session_id=session_id,
            user_query=problem_description,
            priority=priority,
            use_case=use_case,
            parameters=parameters,
        )
        logger.info(f"Job record created: {job_id}")
    except Exception as e:
        logger.error(f"Failed to create job record: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create job record: {str(e)}")

    # Dispatch to Celery (use job_id as task_id for consistency)
    try:
        task = run_optimization_job.apply_async(
            args=(job_id, problem_description, session_id),
            kwargs={
                "use_case": use_case,
                "parameters": parameters,
            },
            task_id=job_id,  # Use job_id as Celery task_id
            priority=priority.value,
        )
        logger.info(f"Job dispatched to Celery: {job_id} (task_id: {task.id})")
    except Exception as e:
        logger.error(f"Failed to dispatch job to Celery: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to dispatch job: {str(e)}")

    # Build HATEOAS links
    base_url = str(request.base_url).rstrip("/")
    links = {
        "self": f"{base_url}/api/jobs/{job_id}",
        "status": f"{base_url}/api/jobs/{job_id}/status",
        "progress": f"{base_url}/api/jobs/{job_id}/progress",
        "result": f"{base_url}/api/jobs/{job_id}/result",
    }

    return JobSubmitResponse(
        job_id=job_id,
        status=JobStatus.QUEUED.value,
        priority=priority.value,
        created_at=job_record["created_at"],
        links=links,
    )


@router.post("/optimize", response_model=JobSubmitResponse, status_code=202)
async def submit_optimization_job(request: JobSubmitRequest, http_request: Request):
    """
    Submit a new optimization job to the async queue.

    This endpoint accepts a natural language query and dispatches it to Celery
    for background processing. The job executes the Dame Workflow asynchronously,
    allowing the client to poll for status or subscribe to WebSocket updates.

    **Request Body:**
    ```json
    {
        "user_query": "Optimize delivery routes for 150 packages",
        "session_id": "user_session_123",
        "priority": "normal",
        "use_case": "VRP",
        "parameters": {}
    }
    ```

    **Response (202 Accepted):**
    ```json
    {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "queued",
        "priority": "normal",
        "created_at": "2025-12-08T12:00:00Z",
        "links": {
            "self": "/api/jobs/550e8400-e29b-41d4-a716-446655440000",
            "status": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/status",
            "stream": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/stream",
            "cancel": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/cancel"
        }
    }
    ```

    **HATEOAS Links:**
    - `self`: Job details endpoint
    - `status`: Job status polling endpoint
    - `stream`: WebSocket streaming endpoint
    - `cancel`: Job cancellation endpoint
    """
    logger.info(f"Received job submission: {request.user_query[:100]}...")

    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Validate priority
    try:
        priority = JobPriority[request.priority.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority: {request.priority}. Must be one of: low, normal, high, urgent"
        )

    # Create job record in database
    try:
        job_record = create_job_record(
            job_id=job_id,
            session_id=request.session_id,
            user_query=request.user_query,
            priority=priority,
            use_case=request.use_case,
            parameters=request.parameters,
        )
        logger.info(f"Job record created: {job_id}")
    except Exception as e:
        logger.error(f"Failed to create job record: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create job record: {str(e)}")

    # Dispatch to Celery (use job_id as task_id for consistency)
    try:
        task = run_optimization_job.apply_async(
            args=(job_id, request.user_query, request.session_id),
            kwargs={
                "use_case": request.use_case,
                "parameters": request.parameters,
            },
            task_id=job_id,  # Use job_id as Celery task_id
            priority=priority.value,
        )
        logger.info(f"Job dispatched to Celery: {job_id} (task_id: {task.id})")
    except Exception as e:
        logger.error(f"Failed to dispatch job to Celery: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to dispatch job: {str(e)}")

    # Build HATEOAS links
    base_url = str(http_request.base_url).rstrip("/")
    links = {
        "self": f"{base_url}/api/jobs/{job_id}",
        "status": f"{base_url}/api/jobs/{job_id}/status",
        "stream": f"{base_url}/api/jobs/{job_id}/stream",
        "cancel": f"{base_url}/api/jobs/{job_id}/cancel",
    }

    return JobSubmitResponse(
        job_id=job_id,
        status=JobStatus.QUEUED.value,
        priority=priority.value,
        created_at=job_record["created_at"],
        links=links,
    )


@router.get("", response_model=JobListResponse)
async def list_jobs(
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of jobs per page"),
    http_request: Request = None,
):
    """
    List jobs with optional filtering and pagination.

    **Query Parameters:**
    - `session_id`: Filter jobs by session ID
    - `status`: Filter jobs by status (queued, running, completed, failed, cancelled)
    - `page`: Page number (1-indexed)
    - `page_size`: Number of jobs per page (max 100)

    **Example Request:**
    ```
    GET /api/jobs?session_id=user_session_123&status=completed&page=1&page_size=20
    ```

    **Response:**
    ```json
    {
        "jobs": [
            {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "priority": "normal",
                "created_at": "2025-12-08T12:00:00Z",
                "completed_at": "2025-12-08T12:05:00Z",
                "user_query": "Optimize delivery routes..."
            },
            ...
        ],
        "total": 45,
        "page": 1,
        "page_size": 20,
        "links": {
            "self": "/api/jobs?session_id=user_session_123&page=1&page_size=20",
            "next": "/api/jobs?session_id=user_session_123&page=2&page_size=20"
        }
    }
    ```
    """
    logger.info(f"Listing jobs: session_id={session_id}, status={status}, page={page}, page_size={page_size}")

    # Get jobs based on filters
    if session_id and status:
        # Filter by both session and status
        all_jobs = get_jobs_by_session(session_id, limit=1000)
        jobs = [j for j in all_jobs if j["status"] == status]
    elif session_id:
        # Filter by session only
        jobs = get_jobs_by_session(session_id, limit=1000)
    elif status:
        # Filter by status only
        try:
            status_enum = JobStatus[status.upper()]
            jobs = get_jobs_by_status(status_enum, limit=1000)
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status: {status}. Must be one of: queued, running, completed, failed, cancelled"
            )
    else:
        # No filters - get all jobs
        jobs = get_all_jobs(limit=1000)

    # Pagination
    total = len(jobs)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_jobs = jobs[start_idx:end_idx]

    # Simplify job records for list response
    simplified_jobs = []
    for job in page_jobs:
        simplified_jobs.append({
            "job_id": job["job_id"],
            "status": job["status"],
            "priority": job["priority"],
            "created_at": job["created_at"],
            "started_at": job["started_at"],
            "completed_at": job["completed_at"],
            "user_query": job["user_query"],
            "use_case": job["use_case"],
        })

    # Build HATEOAS links
    base_url = str(http_request.base_url).rstrip("/")
    query_params = []
    if session_id:
        query_params.append(f"session_id={session_id}")
    if status:
        query_params.append(f"status={status}")

    query_string = "&".join(query_params)
    links = {
        "self": f"{base_url}/api/jobs?{query_string}&page={page}&page_size={page_size}",
    }

    # Add next/prev links
    if end_idx < total:
        links["next"] = f"{base_url}/api/jobs?{query_string}&page={page + 1}&page_size={page_size}"
    if page > 1:
        links["prev"] = f"{base_url}/api/jobs?{query_string}&page={page - 1}&page_size={page_size}"

    return JobListResponse(
        jobs=simplified_jobs,
        total=total,
        page=page,
        page_size=page_size,
        links=links,
    )


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str, http_request: Request):
    """
    Get current job status (polling endpoint).

    This endpoint returns the current status, progress, and metadata for a job.
    Clients can poll this endpoint periodically to check job progress, or use
    the WebSocket endpoint for real-time updates.

    **Response:**
    ```json
    {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "session_id": "user_session_123",
        "status": "running",
        "priority": "normal",
        "created_at": "2025-12-08T12:00:00Z",
        "started_at": "2025-12-08T12:00:05Z",
        "completed_at": null,
        "user_query": "Optimize delivery routes...",
        "progress": {
            "current_step": "data_generation",
            "progress_percentage": 45,
            "step_details": {"tables": 3},
            "updated_at": "2025-12-08T12:00:30Z"
        },
        "error": null,
        "links": {
            "self": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/status",
            "stream": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/stream",
            "cancel": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/cancel"
        }
    }
    ```

    **Status Values:**
    - `queued`: Job is waiting to be processed
    - `running`: Job is currently executing
    - `completed`: Job finished successfully
    - `failed`: Job encountered an error
    - `cancelled`: Job was cancelled by user
    """
    logger.info(f"Getting status for job: {job_id}")

    # Get job from storage
    job_record = get_job(job_id)
    if not job_record:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    # Parse progress if available
    import json
    progress = None
    if job_record["progress"]:
        progress = json.loads(job_record["progress"])

    # Build HATEOAS links
    base_url = str(http_request.base_url).rstrip("/")
    links = {
        "self": f"{base_url}/api/jobs/{job_id}/status",
        "stream": f"{base_url}/api/jobs/{job_id}/stream",
    }

    # Add result link if completed
    if job_record["status"] == JobStatus.COMPLETED.value:
        links["result"] = f"{base_url}/api/jobs/{job_id}/result"
    elif job_record["status"] in [JobStatus.QUEUED.value, JobStatus.RUNNING.value]:
        links["cancel"] = f"{base_url}/api/jobs/{job_id}/cancel"

    return JobStatusResponse(
        job_id=job_id,
        session_id=job_record["session_id"],
        status=job_record["status"],
        priority=job_record["priority"],
        created_at=job_record["created_at"],
        started_at=job_record["started_at"],
        completed_at=job_record["completed_at"],
        user_query=job_record["user_query"],
        use_case=job_record["use_case"],
        progress=progress,
        error=job_record["error"],
        links=links,
    )


@router.get("/{job_id}/progress")
async def get_job_progress(job_id: str):
    """
    Get job progress for real-time updates (simplified endpoint for React client).

    Returns the progress field from the job record, if available.

    **Response:**
    ```json
    {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "progress_percentage": 45,
        "current_step": "data_generation",
        "step_details": {"tables": 3},
        "updated_at": "2025-12-08T12:00:30Z"
    }
    ```
    """
    logger.info(f"Getting progress for job: {job_id}")

    # Get job from storage
    job_record = get_job(job_id)
    if not job_record:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    # Parse progress if available
    import json
    progress = None
    if job_record["progress"]:
        progress = json.loads(job_record["progress"])

    if not progress:
        # Return minimal progress if none available
        return {
            "job_id": job_id,
            "progress_percentage": 0,
            "current_step": None,
            "step_details": None,
            "updated_at": job_record["created_at"]
        }

    # Add job_id to progress response
    progress["job_id"] = job_id
    return progress


@router.get("/{job_id}/result", response_model=JobResultResponse)
async def get_job_result(job_id: str, http_request: Request):
    """
    Get final job result (only available for completed jobs).

    This endpoint returns the complete workflow result including intent discovery,
    data generation, solver optimization, and business explanation.

    **Response:**
    ```json
    {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "completed",
        "completed_at": "2025-12-08T12:05:00Z",
        "result": {
            "status": "completed",
            "workflow_state": {
                "intent": {...},
                "data_pack": {...},
                "solver_output": {...},
                "explanation": {...}
            },
            "mcp_resources": {
                "status": "job://550e8400-e29b-41d4-a716-446655440000/status",
                "result": "job://550e8400-e29b-41d4-a716-446655440000/result",
                "intent": "job://550e8400-e29b-41d4-a716-446655440000/intent",
                "data": "job://550e8400-e29b-41d4-a716-446655440000/data",
                "solver": "job://550e8400-e29b-41d4-a716-446655440000/solver",
                "explanation": "job://550e8400-e29b-41d4-a716-446655440000/explanation"
            }
        },
        "links": {
            "self": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/result",
            "status": "/api/jobs/550e8400-e29b-41d4-a716-446655440000/status"
        }
    }
    ```

    **MCP Resources:**
    All job artifacts are exposed as MCP resources using the `job://` URI scheme.
    """
    logger.info(f"Getting result for job: {job_id}")

    # Get job from storage
    job_record = get_job(job_id)
    if not job_record:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    # Check if job is completed
    if job_record["status"] != JobStatus.COMPLETED.value:
        raise HTTPException(
            status_code=409,
            detail=f"Job not completed (status: {job_record['status']}). Result not available."
        )

    # Parse result
    import json
    if not job_record["result"]:
        raise HTTPException(
            status_code=500,
            detail=f"Job marked as completed but has no result"
        )

    result = json.loads(job_record["result"])
    
    # CRITICAL: Include thinking_history from progress if not already in workflow_state
    # This ensures CoT is restored on page reload (same logic as MCP resource handler)
    workflow_state = result.get("workflow_state", {})
    if not workflow_state.get("thinking_history"):
        # Try to get thinking_history from progress field
        progress_data = job_record.get("progress")
        if progress_data:
            # Progress might be stored as JSON string or dict
            if isinstance(progress_data, str):
                try:
                    progress = json.loads(progress_data)
                except (json.JSONDecodeError, TypeError):
                    progress = None
            else:
                progress = progress_data
            
            if progress and isinstance(progress, dict):
                thinking_history = progress.get("thinking_history", {})
                if thinking_history:
                    # Add thinking_history to workflow_state
                    workflow_state["thinking_history"] = thinking_history
                    result["workflow_state"] = workflow_state
                    logger.debug(f"✅ Added thinking_history to REST API result for job {job_id} ({len(thinking_history)} steps)")
    
    # CRITICAL: Include llm_metrics from database if not already in result
    # Metrics are stored separately in llm_metrics column
    if not result.get("llm_metrics") and job_record.get("llm_metrics"):
        try:
            llm_metrics_data = job_record.get("llm_metrics")
            if isinstance(llm_metrics_data, str):
                llm_metrics = json.loads(llm_metrics_data)
            else:
                llm_metrics = llm_metrics_data
            if llm_metrics:
                result["llm_metrics"] = llm_metrics
                logger.debug(f"✅ Added llm_metrics to REST API result for job {job_id}: {llm_metrics.get('total_calls', 0)} calls")
        except (json.JSONDecodeError, TypeError) as metrics_error:
            logger.warning(f"⚠️ Failed to parse llm_metrics for job {job_id}: {metrics_error}")

    # Build HATEOAS links
    base_url = str(http_request.base_url).rstrip("/")
    links = {
        "self": f"{base_url}/api/jobs/{job_id}/result",
        "status": f"{base_url}/api/jobs/{job_id}/status",
    }

    return JobResultResponse(
        job_id=job_id,
        status=job_record["status"],
        completed_at=job_record["completed_at"],
        result=result,
        links=links,
    )


@router.post("/{job_id}/cancel", response_model=JobCancelResponse)
async def cancel_optimization_job(job_id: str):
    """
    Cancel a running or queued job.

    This endpoint terminates the Celery task and updates the job status to cancelled.
    Only jobs in `queued` or `running` status can be cancelled.

    **Response:**
    ```json
    {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "cancelled",
        "cancelled_at": "2025-12-08T12:02:30Z",
        "message": "Job cancelled successfully"
    }
    ```
    """
    logger.info(f"Cancelling job: {job_id}")

    # Get job from storage
    job_record = get_job(job_id)
    if not job_record:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    # Check if job can be cancelled
    if job_record["status"] not in [JobStatus.QUEUED.value, JobStatus.RUNNING.value]:
        raise HTTPException(
            status_code=409,
            detail=f"Job cannot be cancelled (status: {job_record['status']}). Only queued/running jobs can be cancelled."
        )

    # Cancel via Celery
    try:
        cancel_job.apply_async(args=(job_id,))
        logger.info(f"Job cancellation dispatched: {job_id}")
    except Exception as e:
        logger.error(f"Failed to cancel job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}")

    return JobCancelResponse(
        job_id=job_id,
        status=JobStatus.CANCELLED.value,
        cancelled_at=datetime.utcnow().isoformat(),
        message="Job cancellation requested. Job will be terminated shortly.",
    )


@router.get("/statistics")
async def get_statistics():
    """
    Get job queue statistics.

    Returns aggregated statistics about jobs across all statuses.

    **Response:**
    ```json
    {
        "total_jobs": 145,
        "by_status": {
            "queued": 5,
            "running": 3,
            "completed": 120,
            "failed": 15,
            "cancelled": 2
        },
        "avg_completion_time_seconds": 285.5
    }
    ```
    """
    logger.info("Getting job statistics")

    try:
        stats = get_job_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


# ========== MCP RESOURCE ENDPOINTS ==========

@router.get("/{job_id}/resources")
async def get_job_mcp_resources(job_id: str):
    """
    List all available MCP resources for a job.

    Returns a list of MCP resource URIs (`job://job_id/resource_type`) that
    can be used to access job artifacts.

    **Response:**
    ```json
    {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "completed",
        "resources": {
            "status": "job://550e8400-e29b-41d4-a716-446655440000/status",
            "progress": "job://550e8400-e29b-41d4-a716-446655440000/progress",
            "result": "job://550e8400-e29b-41d4-a716-446655440000/result",
            "intent": "job://550e8400-e29b-41d4-a716-446655440000/intent",
            "data": "job://550e8400-e29b-41d4-a716-446655440000/data",
            "solver": "job://550e8400-e29b-41d4-a716-446655440000/solver",
            "explanation": "job://550e8400-e29b-41d4-a716-446655440000/explanation"
        }
    }
    ```
    """
    logger.info(f"Getting MCP resources for job: {job_id}")

    try:
        resources = list_job_resources(job_id)
        return resources
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get resources: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get resources: {str(e)}")


if __name__ == "__main__":
    # For testing the router independently
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI(title="DcisionAI Job Queue API")
    app.include_router(router)

    logger.info("Starting job API test server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
