from pydantic import BaseModel, Field, model_validator
from typing import Any, Generic, TypeVar
from .._schemas import ResponseBase



class Tag(ResponseBase):
    at: str
    creator_id: int
    deleted_at: str
    id: int
    integration_ext_id: str
    integration_ext_type: str
    integration_provider: str
    name: str
    permissions: list[str]
    workspace_id: int
    
class SharedWith(ResponseBase):
    accepted: bool
    user_id: int
    user_name: str | None = Field(default=None)
    
class TimeEntry(ResponseBase):
    at: str
    billable: bool
    client_name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    duration: int
    duronly: bool
    expense_ids: list[int] | None = Field(default=None)
    id: int
    permissions: list[str] | None = Field(default=None)
    pid: int | None = Field(default=None)
    project_active: bool | None = Field(default=None)
    project_billable: bool | None = Field(default=None)
    project_color: str | None = Field(default=None)
    project_id: int | None = Field(default=None)
    project_name: str | None = Field(default=None)
    shared_with: list[SharedWith] | None = Field(default=None)
    start: str
    stop: str | None = Field(default=None)
    tag_ids: list[int]
    tags: list[Tag]
    task_id: int | None = Field(default=None)
    task_name: str | None = Field(default=None)
    tid: int | None = Field(default=None)
    uid: int
    user_avatar_url: str | None = Field(default=None)
    user_id: int
    user_name: str | None = Field(default=None)
    wid: int
    workspace_id: int
    

class Workspace(ResponseBase):
    admin: bool | None = Field(default=None) # Deprecated
    api_token: str | None = Field(default=None) # deprecated
    at: str
    business_ws: bool # Workspace on Premium subscription
    csv_upload: Any # CSV upload data
    default_currency: str # Default currency, premium feature, optional, only for existing WS, will be 'USD' initially
    default_hourly_rate: int | None = Field(default=None) # The default hourly rate, premium feature, optional, only for existing WS, will be 0.0 initially
    disable_approvals: bool # Disable approvals in the workspace
    disable_expenses: bool # Disable expenses in the workspace
    disable_timesheet_view: bool # Disable timesheet view in the workspace
    hide_start_end_times: bool # -
    ical_enabled: bool # Calendar integration enabled
    ical_url: str # URL of calendar
    id: int
    last_modified: str # Last modification of data in the workspace
    limit_public_project_data: bool # Limit public projects data in reports to admins.
    logo_url: str # URL of workspace logo
    max_data_retention_days: Any | None = Field(default=None) # How far back free workspaces can access data.
    name: str # Name of the workspace
    only_admins_may_create_projects: bool # Only admins will be able to create projects, optional, only for existing WS, will be false initially
    only_admins_may_create_tags: bool # Only admins will be able to create tags, optional, only for existing WS, will be false initially
    only_admins_see_team_dashboard: bool # Only admins will be able to see the team dashboard, optional, only for existing WS, will be false initially
    organization_id: int # Identifier of the organization
    permissions: list[str] | None = Field(default=None) # Permissions list
    premium: bool # Workspace on Starter subscription
    projects_billable_by_default: bool # New projects billable by default
    projects_enforce_billable: bool # Whether tracking time to projects will enforce billable setting to be respected.
    projects_private_by_default: bool # Workspace setting for default project visbility.
    rate_last_updated: str | None = Field(default=None) # Timestamp of last workspace rate update
    reports_collapse: bool | None = Field(default=None) # Whether reports should be collapsed by default, optional, only for existing WS, will be true initially
    role: str | None = Field(default=None) # Role of the current user in the workspace
    rounding: int | None = Field(default=None) # Default rounding, premium feature, optional, only for existing WS. 0 - nearest, 1 - round up, -1 - round down
    rounding_minutes: int | None = Field(default=None) # Default rounding in minutes, premium feature, optional, only for existing WS
    subscription: Any | None = Field(default=None) # deprecated
    suspended_at: str | None = Field(default=None) # Timestamp of suspension
    te_constraints: Any | None = Field(default=None) # Time entry constraints setting
    working_hours_in_minutes: int | None = Field(default=None) # Working hours in minutes

class Project(ResponseBase):
    active: bool
    actual_hours: int | None = Field(default=None)
    actual_seconds: int | None = Field(default=None)
    at: str
    auto_estimates: bool | None = Field(default=None)
    billable: bool | None = Field(default=None)
    can_track_time: bool | None = Field(default=None)
    cid: int | None = Field(default=None)
    client_id: int | None = Field(default=None)
    client_name: str | None = Field(default=None)
    color: str | None = Field(default=None)
    created_at: str
    currency: str | None = Field(default=None)
    current_period: Any | None = Field(default=None) # TODO: define current_period model
    end_date: str | None = Field(default=None)
    estimated_hours: int | None = Field(default=None)
    estimated_seconds: int | None = Field(default=None)
    external_reference: str | None = Field(default=None)
    fixed_fee: int | None = Field(default=None)
    id: int
    integration_ext_id: str | None = Field(default=None)
    integration_ext_type: str | None = Field(default=None)
    integration_provider: str | None = Field(default=None)
    is_private: bool
    name: str
    permissions: list[str] | None = Field(default=None)
    pinned: bool | None = Field(default=None)
    project_id: int | None = Field(default=None, description="Deprecated alias for id")


class TrialInfo(ResponseBase):
    can_have_trial: bool = Field(description="CanHaveInitialTrial is true if neither the organization nor the owner has never had a trial before")
    last_pricing_plan_id: int | None = Field(default=None)
    next_payment_date: str | None = Field(default=None)
    trial: bool = Field(description="Whether the organization's subscription is currently on trial")
    trial_available: bool = Field(description="When a trial is available for this organization Deprecated: TrialAvailable - use CanHaveInitialTrial instead. Retained for front-end compatibility.")
    trial_end_date: str | None = Field(default=None)
    trial_plan_id: int | None = Field(default=None)

class Organization(ResponseBase):
    admin: bool = Field(description="Whether the requester is an admin of the organization")
    at: str = Field(description="Organization's last modification date")
    created_at: str = Field(description="Organization's creation date")
    id: int = Field(description="Organization ID")
    is_multi_workspace_enabled: bool = Field(description="Is true when the organization option is_multi_workspace_enabled is set")
    is_unified: bool
    max_data_retention_days: Any | None = Field(default=None, description="How far back free workspaces in this org can access data.")
    max_workspaces: int = Field(description="Maximum number of workspaces allowed for the organization")
    name: str = Field(description="Organization Name")
    owner: bool = Field(description="Whether the requester is a the owner of the organization")
    permissions: list[str] | None = Field(default=None, description="Array of string")
    pricing_plan_enterprise: bool = Field(description="The subscription plan is an enterprise plan")
    pricing_plan_id: int = Field(description="Organization plan ID")
    pricing_plan_name: str = Field(description="The subscription plan name the org is currently on. Free or any plan name coming from payment provider")
    suspended_at: str | None = Field(default=None, description="Whether the organization is currently suspended")
    trial_info: TrialInfo | None = Field(default=None, description="Trial information")
    user_count: int = Field(description="Number of organization users")


