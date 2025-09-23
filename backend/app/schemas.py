from datetime import datetime
from typing import Optional, Any, List
from pydantic import BaseModel, EmailStr
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class MyProductBase(BaseModel):
    asin: str
    title: str
    description: Optional[str] = None
    bullet_points: Optional[List[str]] = None
    sales_amount: float


class MyProductCreate(MyProductBase):
    pass


class MyProduct(MyProductBase):
    created_at: datetime
    
    class Config:
        from_attributes = True


class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None
    flow_data: dict


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    flow_data: Optional[dict] = None


class Workflow(WorkflowBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkflowRunBase(BaseModel):
    workflow_id: UUID


class WorkflowRunCreate(WorkflowRunBase):
    pass


class WorkflowRun(WorkflowRunBase):
    id: UUID
    user_id: UUID
    status: str
    results: Optional[dict] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str