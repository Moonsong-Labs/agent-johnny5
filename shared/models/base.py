from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class GitCommit(BaseModel):
    """Git commit model."""
    
    commit_hash: str = Field(..., description="The commit hash")
    author: str = Field(..., description="Commit author name")
    author_email: str = Field(..., description="Commit author email")
    date: datetime = Field(..., description="Commit date")
    message: str = Field(..., description="Commit message")
    files_changed: List[str] = Field(default_factory=list, description="Files changed in this commit")
    insertions: int = Field(0, description="Number of insertions")
    deletions: int = Field(0, description="Number of deletions")


class PullRequest(BaseModel):
    """Pull request model."""
    
    pr_id: int = Field(..., description="Pull request ID")
    title: str = Field(..., description="PR title")
    description: Optional[str] = Field(None, description="PR description")
    author: str = Field(..., description="PR author")
    created_at: datetime = Field(..., description="Creation date")
    updated_at: Optional[datetime] = Field(None, description="Last update date")
    merged_at: Optional[datetime] = Field(None, description="Merge date if merged")
    state: str = Field(..., description="PR state (open, closed, merged)")
    commits: List[GitCommit] = Field(default_factory=list, description="Commits in the PR")
    comments: List[Dict] = Field(default_factory=list, description="Comments on the PR")


class CodeSymbol(BaseModel):
    """Code symbol for indexing (function, class, variable, etc)."""
    
    name: str = Field(..., description="Symbol name")
    type: str = Field(..., description="Symbol type (function, class, variable, etc)")
    file_path: str = Field(..., description="Path to the file containing the symbol")
    line_start: int = Field(..., description="Starting line in the file")
    line_end: Optional[int] = Field(None, description="Ending line in the file")
    docstring: Optional[str] = Field(None, description="Symbol documentation string")
    code: str = Field(..., description="Source code of the symbol")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding of the symbol")


class AgentTask(BaseModel):
    """Task for an agent to process."""
    
    task_id: str = Field(..., description="Unique task ID")
    agent: str = Field(..., description="Target agent name")
    action: str = Field(..., description="Action to perform")
    params: Dict = Field(default_factory=dict, description="Parameters for the action")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation time")
    priority: int = Field(1, description="Task priority (higher is more important)")
    status: str = Field("pending", description="Task status")
    result: Optional[Dict] = Field(None, description="Task result if completed")


class AgentResponse(BaseModel):
    """Standard response format from agents."""
    
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Dict] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(None, description="List of errors if any") 