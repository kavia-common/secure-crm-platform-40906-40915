from __future__ import annotations

import os
import uuid
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.core.settings import get_settings
from src.core.db import check_db_connection
from src.api.health import router as health_router

# =========================
# Common Models and Helpers
# =========================

API_PREFIX = "/api/v1"

openapi_tags = [
    {"name": "Health", "description": "Health and diagnostics"},
    {"name": "Auth", "description": "Authentication and session management"},
    {"name": "Users", "description": "User management"},
    {"name": "Roles", "description": "Role management"},
    {"name": "Permissions", "description": "Permission catalog"},
    {"name": "Customers", "description": "Customer management and 360"},
    {"name": "Contacts", "description": "Contact points for customers"},
    {"name": "Interactions", "description": "Customer interactions across channels"},
    {"name": "Service Requests", "description": "Service request lifecycle"},
    {"name": "Complaints", "description": "Complaint management and escalation"},
    {"name": "Inbox", "description": "Omni-channel inbox"},
    {"name": "Connectors", "description": "External connectors and webhooks"},
    {"name": "Reports", "description": "Reporting and analytics"},
    {"name": "Audit", "description": "Audit logs"},
    {"name": "Settings", "description": "Profile and preferences"},
    {"name": "WebSockets", "description": "Real-time notifications and inbox streams"},
]


class ErrorResponse(BaseModel):
    code: str = Field(..., description="Stable error code string, e.g., 'auth.invalid_credentials'")
    message: str = Field(..., description="Human-readable error summary")
    details: Optional[Dict[str, Any]] = Field(None, description="Structured details map")
    trace_id: str = Field(..., description="Correlation/trace ID for support")


class Pagination(BaseModel):
    items: List[Any] = Field(default_factory=list, description="List of items for this page")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number (1-based)")
    size: int = Field(..., description="Page size")


# ======================================
# Minimal In-Memory Stubs and Data Types
# ======================================

# PUBLIC_INTERFACE
class TokenPair(BaseModel):
    """OAuth2-like token pair with access and refresh tokens."""

    access_token: str = Field(..., description="JWT access token (mock)")
    refresh_token: str = Field(..., description="JWT refresh token (mock)")
    token_type: str = Field(default="bearer", description="Token type")


# PUBLIC_INTERFACE
class LoginRequest(BaseModel):
    """Login payload with username and password."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


# PUBLIC_INTERFACE
class User(BaseModel):
    """User DTO (read)."""

    id: str
    username: str
    email: Optional[str] = None
    status: str = "active"
    roles: List[str] = Field(default_factory=list)


# PUBLIC_INTERFACE
class UserCreate(BaseModel):
    """User create DTO."""

    username: str
    email: Optional[str] = None


# PUBLIC_INTERFACE
class UserUpdate(BaseModel):
    """User update DTO."""

    email: Optional[str] = None
    status: Optional[str] = None


# PUBLIC_INTERFACE
class Role(BaseModel):
    """Role DTO."""

    id: str
    name: str
    description: Optional[str] = None


# PUBLIC_INTERFACE
class RoleCreate(BaseModel):
    """Role create DTO."""

    name: str
    description: Optional[str] = None


# PUBLIC_INTERFACE
class Permission(BaseModel):
    """Permission DTO."""

    id: str
    resource: str
    action: str


# PUBLIC_INTERFACE
class PermissionCreate(BaseModel):
    """Permission create DTO."""

    resource: str
    action: str


# PUBLIC_INTERFACE
class Customer(BaseModel):
    """Customer DTO."""

    id: str
    name: str
    tags: List[str] = Field(default_factory=list)
    owner_id: Optional[str] = None


# PUBLIC_INTERFACE
class CustomerCreate(BaseModel):
    """Customer create DTO."""

    name: str
    tags: Optional[List[str]] = None
    owner_id: Optional[str] = None


# PUBLIC_INTERFACE
class CustomerUpdate(BaseModel):
    """Customer update DTO."""

    name: Optional[str] = None
    tags: Optional[List[str]] = None
    owner_id: Optional[str] = None


# PUBLIC_INTERFACE
class Contact(BaseModel):
    """Contact DTO."""

    id: str
    customer_id: str
    type: str
    value: str


# PUBLIC_INTERFACE
class ContactCreate(BaseModel):
    """Contact create DTO."""

    type: str
    value: str


# PUBLIC_INTERFACE
class Interaction(BaseModel):
    """Interaction DTO."""

    id: str
    customer_id: str
    channel: str
    subject: Optional[str] = None
    summary: Optional[str] = None


# PUBLIC_INTERFACE
class InteractionCreate(BaseModel):
    """Interaction create DTO."""

    customer_id: str
    channel: str
    subject: Optional[str] = None
    summary: Optional[str] = None


# PUBLIC_INTERFACE
class ServiceRequest(BaseModel):
    """Service Request DTO."""

    id: str
    customer_id: str
    type: str
    priority: str
    status: str = "New"


# PUBLIC_INTERFACE
class ServiceRequestCreate(BaseModel):
    """Service Request create DTO."""

    customer_id: str
    type: str
    priority: str


# PUBLIC_INTERFACE
class ServiceRequestUpdate(BaseModel):
    """Service Request update DTO."""

    type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


# PUBLIC_INTERFACE
class Comment(BaseModel):
    """Comment DTO."""

    id: str
    text: str


# PUBLIC_INTERFACE
class Complaint(BaseModel):
    """Complaint DTO."""

    id: str
    customer_id: str
    category: str
    severity: str
    status: str = "New"
    regulator_flag: bool = False


# PUBLIC_INTERFACE
class ComplaintCreate(BaseModel):
    """Complaint create DTO."""

    customer_id: str
    category: str
    severity: str
    regulator_flag: Optional[bool] = False


# PUBLIC_INTERFACE
class ComplaintUpdate(BaseModel):
    """Complaint update DTO."""

    category: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    regulator_flag: Optional[bool] = None


# PUBLIC_INTERFACE
class KPIResponse(BaseModel):
    """KPI summary DTO."""

    open_srs: int
    sla_risk: int
    open_complaints: int
    inbox_today: int


# PUBLIC_INTERFACE
class TimeSeriesPoint(BaseModel):
    """Timeseries point."""

    ts: str
    value: float


# PUBLIC_INTERFACE
class ProfileSettings(BaseModel):
    """Profile settings DTO."""

    full_name: Optional[str] = None
    phone: Optional[str] = None


# PUBLIC_INTERFACE
class Preferences(BaseModel):
    """User preferences DTO."""

    theme: Optional[str] = Field(default="system", description="light|dark|system")
    density: Optional[str] = Field(default="comfortable", description="comfortable|compact")


# ========================
# Auth and RBAC Stubs
# ========================

def _gen_id() -> str:
    return str(uuid.uuid4())


def _trace_id() -> str:
    return str(uuid.uuid4())


def _error(code: str, message: str, details: Optional[Dict[str, Any]] = None, status_code: int = 400) -> JSONResponse:
    payload = ErrorResponse(code=code, message=message, details=details, trace_id=_trace_id())
    return JSONResponse(status_code=status_code, content=payload.model_dump())


# Very small in-memory structures to simulate storage
DB: Dict[str, Dict[str, Dict[str, Any]]] = {
    "users": {},
    "roles": {},
    "permissions": {},
    "user_roles": {},  # user_id -> [role_ids]
    "role_permissions": {},  # role_id -> [permission_ids]
    "customers": {},
    "contacts": {},
    "interactions": {},
    "service_requests": {},
    "sr_comments": {},  # sr_id -> [Comment]
    "complaints": {},
    "audit": [],
}

# PUBLIC_INTERFACE
class AuthUser(BaseModel):
    """Authenticated user claims stub."""

    user_id: str
    roles: List[str] = Field(default_factory=list)


def get_env(name: str, default: Optional[str] = None) -> str:
    val = os.getenv(name, default)
    if val is None:
        # For bootstrap we tolerate missing in dev, but do not break app init.
        val = ""
    return val


# PUBLIC_INTERFACE
async def jwt_auth_dependency(authorization: Optional[str] = Header(default=None)) -> AuthUser:
    """Authenticate JWT token (mock). Validates presence and returns stub user."""
    if not authorization or not authorization.lower().startswith("bearer "):
        # 401 standardized
        raise HTTPException(status_code=401, detail=_error("auth.missing_token", "Missing or invalid Authorization header").body.decode() if isinstance(_error("x","x"), JSONResponse) else "Unauthorized")
    token = authorization.split(" ", 1)[1].strip()
    if token == "invalid":
        raise HTTPException(status_code=401, detail="Invalid token")
    # Mock decode
    # For demo: token 'admin' -> admin user, else 'user'
    if token == "admin":
        user_id = "00000000-0000-0000-0000-000000000001"
        roles = ["admin"]
    else:
        user_id = "00000000-0000-0000-0000-000000000002"
        roles = ["agent"]
    return AuthUser(user_id=user_id, roles=roles)


def require_roles(*required_roles: str):
    async def _dep(user: AuthUser = Depends(jwt_auth_dependency)) -> AuthUser:
        if not any(role in user.roles for role in required_roles):
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return _dep


# ================
# App Construction
# ================

app = FastAPI(
    title="Secure CRM Backend",
    description="REST and WebSocket APIs for the Secure CRM platform",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

# Load settings once
_settings = get_settings()

# Dynamic CORS based on settings
allowed_origins = _settings.cors_origins_list()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup probe for DB connectivity (non-fatal in dev)
@app.on_event("startup")
async def _startup_probe() -> None:
    ok = await check_db_connection()
    # Do not raise here to let app boot even if DB unavailable; readiness will reflect true state.
    # In production you might choose to log or raise based on policy.
    _ = ok


# ================
# Error Middleware
# ================

class ErrorEnvelopeMiddleware(BaseHTTPMiddleware):
    """Convert unhandled exceptions to standardized ErrorResponse."""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as he:
            # If detail is JSONResponse already, forward it
            if isinstance(he.detail, str):
                return _error("http.exception", he.detail, status_code=he.status_code)
            return JSONResponse(status_code=he.status_code, content=he.detail)
        except Exception as ex:  # pragma: no cover - generic catch to ensure envelope
            return _error("internal.error", "An unexpected error occurred", {"exception": str(ex)}, 500)


app.add_middleware(ErrorEnvelopeMiddleware)


# =========================
# Helpers: pagination/sort
# =========================

def paginate(items: List[Dict[str, Any]], page: int, page_size: int) -> Pagination:
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return Pagination(items=items[start:end], total=total, page=page, size=page_size)


def sort_items(items: List[Dict[str, Any]], sort: Optional[str]) -> List[Dict[str, Any]]:
    if not sort:
        return items
    field = sort
    reverse = False
    if sort.startswith("-"):
        reverse = True
        field = sort[1:]
    try:
        return sorted(items, key=lambda x: x.get(field), reverse=reverse)
    except Exception:
        return items


def filter_items(items: List[Dict[str, Any]], filters: Dict[str, str]) -> List[Dict[str, Any]]:
    result = items
    for k, v in filters.items():
        if v is None:
            continue
        result = [it for it in result if str(it.get(k, "")).lower() == str(v).lower()]
    return result


# =====================
# Health and WS Routers
# =====================

# Mount health routes at "/" and "/ready"
app.include_router(health_router, prefix="")


# Simple in-memory pubsub for notifications (per-connection scope)
class NotifierManager:
    def __init__(self) -> None:
        self.clients: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.clients.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.clients:
            self.clients.remove(ws)

    async def broadcast(self, message: Dict[str, Any]):
        for ws in list(self.clients):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(ws)


notifications_manager = NotifierManager()
inbox_manager = NotifierManager()


@app.get("/ws", include_in_schema=False)
def ws_docs_hint():
    """Return hints for using WebSocket endpoints."""
    return {
        "message": "Use WebSocket endpoints: /ws/notifications and /ws/inbox",
        "endpoints": ["/ws/notifications", "/ws/inbox"],
    }


@app.websocket("/ws/notifications")
async def ws_notifications(websocket: WebSocket):
    """
    WebSocket: Notifications stream.

    - Connect without auth for demo; in production enforce auth and origin checks (WEBSOCKET_ALLOWED_ORIGINS).
    - Messages are JSON objects broadcasted by server stubs.
    """
    await notifications_manager.connect(websocket)
    try:
        while True:
            # Keepalive or ignore incoming
            await websocket.receive_text()
    except WebSocketDisconnect:
        notifications_manager.disconnect(websocket)


@app.websocket("/ws/inbox")
async def ws_inbox(websocket: WebSocket):
    """
    WebSocket: Inbox events stream.

    Similar behavior to notifications with separate channel.
    """
    await inbox_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        inbox_manager.disconnect(websocket)


# ===========
# Auth Router
# ===========

auth_router = APIRouter(prefix=API_PREFIX + "/auth", tags=["Auth"])


@auth_router.post("/login", response_model=TokenPair, summary="Login")
def login(body: LoginRequest):
    """
    Authenticate user and issue token pair.
    For demo, any credentials are accepted; 'admin' username grants admin role via token value.
    """
    access = "admin" if body.username.lower() == "admin" else "user"
    refresh = "refresh-" + _gen_id()
    return TokenPair(access_token=access, refresh_token=refresh)


@auth_router.post("/refresh", response_model=TokenPair, summary="Refresh Token")
def refresh_token(refresh_token: str = Query(..., description="Refresh token")):
    """
    Refresh tokens using provided refresh token (mock).
    """
    if not refresh_token.startswith("refresh-"):
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return TokenPair(access_token="user", refresh_token="refresh-" + _gen_id())


@auth_router.post("/logout", summary="Logout")
def logout(user: AuthUser = Depends(jwt_auth_dependency)):
    """
    Logout current session (mock: no state kept).
    """
    return {"status": "ok"}


@auth_router.get("/me", response_model=User, summary="Current User")
def me(user: AuthUser = Depends(jwt_auth_dependency)):
    """
    Return profile for current user.
    """
    return User(id=user.user_id, username="admin" if "admin" in user.roles else "agent", email=None, roles=user.roles)


# ===========================
# Users/Roles/Permissions API
# ===========================

urp_router = APIRouter(prefix=API_PREFIX, tags=["Users", "Roles", "Permissions"])

# Users
@urp_router.get(
    "/users",
    response_model=Pagination,
    summary="List Users",
    responses={400: {"model": ErrorResponse}},
)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    sort: Optional[str] = Query(None, description="Sort by field, prefix with - for desc"),
    status: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Search by username"),
    _: AuthUser = Depends(require_roles("admin")),
):
    items = list(DB["users"].values())
    if q:
        items = [it for it in items if q.lower() in it.get("username", "").lower()]
    items = filter_items(items, {"status": status})
    items = sort_items(items, sort)
    return paginate(items, page, page_size)


@urp_router.post("/users", response_model=User, summary="Create User")
def create_user(body: UserCreate, _: AuthUser = Depends(require_roles("admin"))):
    uid = _gen_id()
    data = {"id": uid, "username": body.username, "email": body.email, "status": "active", "roles": []}
    DB["users"][uid] = data
    return data


@urp_router.get("/users/{id}", response_model=User, summary="Get User")
def get_user(id: str, _: AuthUser = Depends(require_roles("admin"))):
    user = DB["users"].get(id)
    if not user:
        return _error("user.not_found", "User not found", status_code=404)
    return user


@urp_router.put("/users/{id}", response_model=User, summary="Replace User")
def put_user(id: str, body: UserCreate, _: AuthUser = Depends(require_roles("admin"))):
    if id not in DB["users"]:
        return _error("user.not_found", "User not found", status_code=404)
    DB["users"][id]["username"] = body.username
    DB["users"][id]["email"] = body.email
    return DB["users"][id]


@urp_router.patch("/users/{id}", response_model=User, summary="Update User")
def patch_user(id: str, body: UserUpdate, _: AuthUser = Depends(require_roles("admin"))):
    if id not in DB["users"]:
        return _error("user.not_found", "User not found", status_code=404)
    for k, v in body.model_dump(exclude_none=True).items():
        DB["users"][id][k] = v
    return DB["users"][id]


@urp_router.delete("/users/{id}", summary="Delete User")
def delete_user(id: str, _: AuthUser = Depends(require_roles("admin"))):
    if id not in DB["users"]:
        return _error("user.not_found", "User not found", status_code=404)
    del DB["users"][id]
    return {"status": "deleted"}


@urp_router.post("/users/{id}/roles", summary="Assign Roles to User")
def assign_roles(id: str, roles: List[str], _: AuthUser = Depends(require_roles("admin"))):
    if id not in DB["users"]:
        return _error("user.not_found", "User not found", status_code=404)
    DB["users"][id]["roles"] = roles
    DB["user_roles"][id] = [r for r in DB["roles"] if DB["roles"][r]["name"] in roles]
    return {"status": "ok", "roles": roles}


# Roles
@urp_router.get("/roles", response_model=Pagination, summary="List Roles")
def list_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    sort: Optional[str] = None,
    q: Optional[str] = None,
    _: AuthUser = Depends(require_roles("admin")),
):
    items = list(DB["roles"].values())
    if q:
        items = [it for it in items if q.lower() in it.get("name", "").lower()]
    items = sort_items(items, sort)
    return paginate(items, page, page_size)


@urp_router.post("/roles", response_model=Role, summary="Create Role")
def create_role(body: RoleCreate, _: AuthUser = Depends(require_roles("admin"))):
    rid = _gen_id()
    data = {"id": rid, "name": body.name, "description": body.description}
    DB["roles"][rid] = data
    return data


@urp_router.get("/roles/{id}", response_model=Role, summary="Get Role")
def get_role(id: str, _: AuthUser = Depends(require_roles("admin"))):
    role = DB["roles"].get(id)
    if not role:
        return _error("role.not_found", "Role not found", status_code=404)
    return role


@urp_router.put("/roles/{id}", response_model=Role, summary="Replace Role")
def put_role(id: str, body: RoleCreate, _: AuthUser = Depends(require_roles("admin"))):
    if id not in DB["roles"]:
        return _error("role.not_found", "Role not found", status_code=404)
    DB["roles"][id].update({"name": body.name, "description": body.description})
    return DB["roles"][id]


@urp_router.patch("/roles/{id}", response_model=Role, summary="Update Role")
def patch_role(id: str, body: RoleCreate, _: AuthUser = Depends(require_roles("admin"))):
    if id not in DB["roles"]:
        return _error("role.not_found", "Role not found", status_code=404)
    DB["roles"][id].update({k: v for k, v in body.model_dump(exclude_none=True).items()})
    return DB["roles"][id]


@urp_router.delete("/roles/{id}", summary="Delete Role")
def delete_role(id: str, _: AuthUser = Depends(require_roles("admin"))):
    if id not in DB["roles"]:
        return _error("role.not_found", "Role not found", status_code=404)
    del DB["roles"][id]
    return {"status": "deleted"}


@urp_router.post("/roles/{id}/permissions", summary="Grant permissions to Role")
def role_permissions_add(id: str, perm_ids: List[str], _: AuthUser = Depends(require_roles("admin"))):
    if id not in DB["roles"]:
        return _error("role.not_found", "Role not found", status_code=404)
    DB["role_permissions"].setdefault(id, [])
    DB["role_permissions"][id].extend(perm_ids)
    DB["role_permissions"][id] = list(set(DB["role_permissions"][id]))
    return {"status": "ok", "role_id": id, "permission_ids": DB["role_permissions"][id]}


# Permissions
@urp_router.get("/permissions", response_model=Pagination, summary="List Permissions")
def list_permissions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    sort: Optional[str] = None,
    resource: Optional[str] = None,
    action: Optional[str] = None,
    _: AuthUser = Depends(require_roles("admin")),
):
    items = list(DB["permissions"].values())
    items = filter_items(items, {"resource": resource, "action": action})
    items = sort_items(items, sort)
    return paginate(items, page, page_size)


@urp_router.post("/permissions", response_model=Permission, summary="Create Permission")
def create_permission(body: PermissionCreate, _: AuthUser = Depends(require_roles("admin"))):
    pid = _gen_id()
    data = {"id": pid, "resource": body.resource, "action": body.action}
    DB["permissions"][pid] = data
    return data


# ============================
# Customers / Contacts Routers
# ============================

cust_router = APIRouter(prefix=API_PREFIX, tags=["Customers", "Contacts"])

@cust_router.get("/customers", response_model=Pagination, summary="List Customers")
def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    sort: Optional[str] = None,
    q: Optional[str] = Query(None, description="Free-text name contains"),
    tags: Optional[str] = None,
    owner_id: Optional[str] = None,
    _: AuthUser = Depends(require_roles("agent", "admin")),
):
    items = list(DB["customers"].values())
    if q:
        items = [it for it in items if q.lower() in it.get("name", "").lower()]
    if tags:
        tag_set = {t.strip().lower() for t in tags.split(",")}
        items = [it for it in items if tag_set.intersection({t.lower() for t in it.get("tags", [])})]
    items = filter_items(items, {"owner_id": owner_id})
    items = sort_items(items, sort)
    return paginate(items, page, page_size)


@cust_router.post("/customers", response_model=Customer, summary="Create Customer")
def create_customer(body: CustomerCreate, _: AuthUser = Depends(require_roles("agent", "admin"))):
    cid = _gen_id()
    data = {"id": cid, "name": body.name, "tags": body.tags or [], "owner_id": body.owner_id}
    DB["customers"][cid] = data
    return data


@cust_router.get("/customers/{id}", response_model=Customer, summary="Get Customer")
def get_customer(id: str, _: AuthUser = Depends(require_roles("agent", "admin"))):
    data = DB["customers"].get(id)
    if not data:
        return _error("customer.not_found", "Customer not found", status_code=404)
    return data


@cust_router.put("/customers/{id}", response_model=Customer, summary="Replace Customer")
def put_customer(id: str, body: CustomerCreate, _: AuthUser = Depends(require_roles("agent", "admin"))):
    if id not in DB["customers"]:
        return _error("customer.not_found", "Customer not found", status_code=404)
    DB["customers"][id].update({"name": body.name, "tags": body.tags or [], "owner_id": body.owner_id})
    return DB["customers"][id]


@cust_router.patch("/customers/{id}", response_model=Customer, summary="Update Customer")
def patch_customer(id: str, body: CustomerUpdate, _: AuthUser = Depends(require_roles("agent", "admin"))):
    if id not in DB["customers"]:
        return _error("customer.not_found", "Customer not found", status_code=404)
    DB["customers"][id].update({k: v for k, v in body.model_dump(exclude_none=True).items()})
    return DB["customers"][id]


@cust_router.delete("/customers/{id}", summary="Delete Customer")
def delete_customer(id: str, _: AuthUser = Depends(require_roles("admin"))):
    if id not in DB["customers"]:
        return _error("customer.not_found", "Customer not found", status_code=404)
    del DB["customers"][id]
    return {"status": "deleted"}


@cust_router.get("/customers/{id}/timeline", summary="Customer Timeline")
def customer_timeline(id: str, _: AuthUser = Depends(require_roles("agent", "admin"))):
    if id not in DB["customers"]:
        return _error("customer.not_found", "Customer not found", status_code=404)
    interactions = [v for v in DB["interactions"].values() if v["customer_id"] == id]
    srs = [v for v in DB["service_requests"].values() if v["customer_id"] == id]
    complaints = [v for v in DB["complaints"].values() if v["customer_id"] == id]
    return {"interactions": interactions, "service_requests": srs, "complaints": complaints}


@cust_router.get("/customers/search", response_model=Pagination, summary="Search Customers")
def customers_search(
    q: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    owner_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    sort: Optional[str] = None,
    _: AuthUser = Depends(require_roles("agent", "admin")),
):
    return list_customers(page=page, page_size=page_size, sort=sort, q=q, tags=tags, owner_id=owner_id)  # type: ignore


@cust_router.get("/customers/{id}/contacts", response_model=Pagination, summary="List Contacts")
def list_contacts(
    id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    _: AuthUser = Depends(require_roles("agent", "admin")),
):
    contacts = [v for v in DB["contacts"].values() if v["customer_id"] == id]
    return paginate(contacts, page, page_size)


@cust_router.post("/customers/{id}/contacts", response_model=Contact, summary="Create Contact")
def create_contact(id: str, body: ContactCreate, _: AuthUser = Depends(require_roles("agent", "admin"))):
    if id not in DB["customers"]:
        return _error("customer.not_found", "Customer not found", status_code=404)
    cid = _gen_id()
    data = {"id": cid, "customer_id": id, "type": body.type, "value": body.value}
    DB["contacts"][cid] = data
    return data


@cust_router.get("/contacts/{id}", response_model=Contact, summary="Get Contact")
def get_contact(id: str, _: AuthUser = Depends(require_roles("agent", "admin"))):
    data = DB["contacts"].get(id)
    if not data:
        return _error("contact.not_found", "Contact not found", status_code=404)
    return data


@cust_router.put("/contacts/{id}", response_model=Contact, summary="Replace Contact")
def put_contact(id: str, body: ContactCreate, _: AuthUser = Depends(require_roles("agent", "admin"))):
    if id not in DB["contacts"]:
        return _error("contact.not_found", "Contact not found", status_code=404)
    DB["contacts"][id].update({"type": body.type, "value": body.value})
    return DB["contacts"][id]


@cust_router.patch("/contacts/{id}", response_model=Contact, summary="Update Contact")
def patch_contact(id: str, body: ContactCreate, _: AuthUser = Depends(require_roles("agent", "admin"))):
    if id not in DB["contacts"]:
        return _error("contact.not_found", "Contact not found", status_code=404)
    DB["contacts"][id].update({k: v for k, v in body.model_dump(exclude_none=True).items()})
    return DB["contacts"][id]


@cust_router.delete("/contacts/{id}", summary="Delete Contact")
def delete_contact(id: str, _: AuthUser = Depends(require_roles("admin"))):
    if id not in DB["contacts"]:
        return _error("contact.not_found", "Contact not found", status_code=404)
    del DB["contacts"][id]
    return {"status": "deleted"}


# ==================
# Interactions Router
# ==================

inter_router = APIRouter(prefix=API_PREFIX, tags=["Interactions"])

@inter_router.get("/interactions", response_model=Pagination, summary="List Interactions")
def list_interactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    customer_id: Optional[str] = None,
    channel: Optional[str] = None,
    sort: Optional[str] = None,
    _: AuthUser = Depends(require_roles("agent", "admin")),
):
    items = list(DB["interactions"].values())
    items = filter_items(items, {"customer_id": customer_id, "channel": channel})
    items = sort_items(items, sort)
    return paginate(items, page, page_size)


@inter_router.post("/interactions", response_model=Interaction, summary="Create Interaction")
def create_interaction(body: InteractionCreate, _: AuthUser = Depends(require_roles("agent", "admin"))):
    iid = _gen_id()
    data = {"id": iid, **body.model_dump()}
    DB["interactions"][iid] = data
    return data


@inter_router.get("/interactions/{id}", response_model=Interaction, summary="Get Interaction")
def get_interaction(id: str, _: AuthUser = Depends(require_roles("agent", "admin"))):
    data = DB["interactions"].get(id)
    if not data:
        return _error("interaction.not_found", "Interaction not found", status_code=404)
    return data


@inter_router.put("/interactions/{id}", response_model=Interaction, summary="Replace Interaction")
def put_interaction(id: str, body: InteractionCreate, _: AuthUser = Depends(require_roles("agent", "admin"))):
    if id not in DB["interactions"]:
        return _error("interaction.not_found", "Interaction not found", status_code=404)
    DB["interactions"][id].update(body.model_dump())
    return DB["interactions"][id]


@inter_router.patch("/interactions/{id}", response_model=Interaction, summary="Update Interaction")
def patch_interaction(id: str, body: InteractionCreate, _: AuthUser = Depends(require_roles("agent", "admin"))):
    if id not in DB["interactions"]:
        return _error("interaction.not_found", "Interaction not found", status_code=404)
    DB["interactions"][id].update({k: v for k, v in body.model_dump(exclude_none=True).items()})
    return DB["interactions"][id]


@inter_router.delete("/interactions/{id}", summary="Delete Interaction")
def delete_interaction(id: str, _: AuthUser = Depends(require_roles("admin"))):
    if id not in DB["interactions"]:
        return _error("interaction.not_found", "Interaction not found", status_code=404)
    del DB["interactions"][id]
    return {"status": "deleted"}


# =====================
# Service Requests API
# =====================

sr_router = APIRouter(prefix=API_PREFIX, tags=["Service Requests"])

@sr_router.get("/service-requests", response_model=Pagination, summary="List Service Requests")
def list_srs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    sort: Optional[str] = None,
    _: AuthUser = Depends(require_roles("agent", "admin")),
):
    items = list(DB["service_requests"].values())
    items = filter_items(items, {"status": status, "assigned_to": assigned_to})
    items = sort_items(items, sort)
    return paginate(items, page, page_size)


@sr_router.post("/service-requests", response_model=ServiceRequest, summary="Create Service Request")
def create_sr(body: ServiceRequestCreate, _: AuthUser = Depends(require_roles("agent", "admin"))):
    sid = _gen_id()
    data = {"id": sid, "customer_id": body.customer_id, "type": body.type, "priority": body.priority, "status": "New"}
    DB["service_requests"][sid] = data
    return data


@sr_router.get("/service-requests/{id}", response_model=ServiceRequest, summary="Get Service Request")
def get_sr(id: str, _: AuthUser = Depends(require_roles("agent", "admin"))):
    data = DB["service_requests"].get(id)
    if not data:
        return _error("sr.not_found", "Service Request not found", status_code=404)
    return data


@sr_router.put("/service-requests/{id}", response_model=ServiceRequest, summary="Replace Service Request")
def put_sr(id: str, body: ServiceRequestUpdate, _: AuthUser = Depends(require_roles("agent", "admin"))):
    if id not in DB["service_requests"]:
        return _error("sr.not_found", "Service Request not found", status_code=404)
    DB["service_requests"][id].update({k: v for k, v in body.model_dump(exclude_none=True).items()})
    return DB["service_requests"][id]


@sr_router.patch("/service-requests/{id}", response_model=ServiceRequest, summary="Update Service Request")
def patch_sr(id: str, body: ServiceRequestUpdate, _: AuthUser = Depends(require_roles("agent", "admin"))):
    return put_sr(id, body)  # reuse


@sr_router.patch("/service-requests/{id}/transition", response_model=ServiceRequest, summary="Transition SR")
def transition_sr(id: str, status: str = Query(..., description="New|InProgress|Pending|Escalated|Resolved|Closed"), _: AuthUser = Depends(require_roles("agent", "admin"))):
    allowed = {"New", "InProgress", "Pending", "Escalated", "Resolved", "Closed"}
    if status not in allowed:
        return _error("sr.invalid_transition", "Illegal status transition", {"status": status}, 409)
    if id not in DB["service_requests"]:
        return _error("sr.not_found", "Service Request not found", status_code=404)
    DB["service_requests"][id]["status"] = status
    return DB["service_requests"][id]


@sr_router.post("/service-requests/{id}/comments", response_model=Comment, summary="Add Comment to SR")
def add_sr_comment(id: str, text: str = Query(..., description="Comment text"), _: AuthUser = Depends(require_roles("agent", "admin"))):
    if id not in DB["service_requests"]:
        return _error("sr.not_found", "Service Request not found", status_code=404)
    c = {"id": _gen_id(), "text": text}
    DB["sr_comments"].setdefault(id, [])
    DB["sr_comments"][id].append(c)
    return c


@sr_router.get("/service-requests/{id}/comments", response_model=List[Comment], summary="List SR Comments")
def list_sr_comments(id: str, _: AuthUser = Depends(require_roles("agent", "admin"))):
    if id not in DB["service_requests"]:
        return _error("sr.not_found", "Service Request not found", status_code=404)
    return DB["sr_comments"].get(id, [])


@sr_router.post("/service-requests/{id}/attachments", summary="Add Attachment (stub)")
def add_sr_attachment(id: str, filename: str = Query(...), _: AuthUser = Depends(require_roles("agent", "admin"))):
    if id not in DB["service_requests"]:
        return _error("sr.not_found", "Service Request not found", status_code=404)
    return {"status": "ok", "filename": filename}


# ===============
# Complaints API
# ===============

comp_router = APIRouter(prefix=API_PREFIX, tags=["Complaints"])

@comp_router.get("/complaints", response_model=Pagination, summary="List Complaints")
def list_complaints(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    status: Optional[str] = None,
    severity: Optional[str] = None,
    regulator_flag: Optional[bool] = None,
    sort: Optional[str] = None,
    _: AuthUser = Depends(require_roles("agent", "admin")),
):
    items = list(DB["complaints"].values())
    # Convert bool filter to exact match if provided
    if regulator_flag is not None:
        items = [it for it in items if bool(it.get("regulator_flag")) == regulator_flag]
    items = filter_items(items, {"status": status, "severity": severity})
    items = sort_items(items, sort)
    return paginate(items, page, page_size)


@comp_router.post("/complaints", response_model=Complaint, summary="Create Complaint")
def create_complaint(body: ComplaintCreate, _: AuthUser = Depends(require_roles("agent", "admin"))):
    cid = _gen_id()
    data = {"id": cid, **body.model_dump()}
    DB["complaints"][cid] = data
    return data


@comp_router.get("/complaints/{id}", response_model=Complaint, summary="Get Complaint")
def get_complaint(id: str, _: AuthUser = Depends(require_roles("agent", "admin"))):
    data = DB["complaints"].get(id)
    if not data:
        return _error("complaint.not_found", "Complaint not found", status_code=404)
    return data


@comp_router.put("/complaints/{id}", response_model=Complaint, summary="Replace Complaint")
def put_complaint(id: str, body: ComplaintUpdate, _: AuthUser = Depends(require_roles("agent", "admin"))):
    if id not in DB["complaints"]:
        return _error("complaint.not_found", "Complaint not found", status_code=404)
    DB["complaints"][id].update({k: v for k, v in body.model_dump(exclude_none=True).items()})
    return DB["complaints"][id]


@comp_router.patch("/complaints/{id}", response_model=Complaint, summary="Update Complaint")
def patch_complaint(id: str, body: ComplaintUpdate, _: AuthUser = Depends(require_roles("agent", "admin"))):
    return put_complaint(id, body)  # reuse


@comp_router.patch("/complaints/{id}/escalate", response_model=Complaint, summary="Escalate Complaint")
def escalate_complaint(id: str, level: int = Query(..., ge=1, le=5), reason: str = Query(...), _: AuthUser = Depends(require_roles("agent", "admin"))):
    if id not in DB["complaints"]:
        return _error("complaint.not_found", "Complaint not found", status_code=404)
    DB["complaints"][id]["status"] = "Escalated"
    # In a real system, record escalation event
    return DB["complaints"][id]


# =====================
# Omnichannel Inbox API
# =====================

inbox_router = APIRouter(prefix=API_PREFIX, tags=["Inbox"])

@inbox_router.get("/inbox", response_model=Pagination, summary="List Inbox Items")
def list_inbox(
    channel: Optional[str] = None,
    state: Optional[str] = None,
    assignee_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    sort: Optional[str] = None,
    _: AuthUser = Depends(require_roles("agent", "admin")),
):
    # For demo, derive from interactions as inbox threads
    items = [
        {**v, "state": "open", "assignee_id": None}
        for v in DB["interactions"].values()
    ]
    items = filter_items(items, {"channel": channel, "state": state, "assignee_id": assignee_id})
    items = sort_items(items, sort)
    return paginate(items, page, page_size)


@inbox_router.patch("/inbox/{id}/assign", summary="Assign Inbox Item")
def assign_inbox(id: str, assignee_id: str = Query(...), _: AuthUser = Depends(require_roles("agent", "admin"))):
    if id not in DB["interactions"]:
        return _error("inbox.not_found", "Inbox item not found", status_code=404)
    # Broadcast via WS
    return {"status": "ok", "id": id, "assignee_id": assignee_id}


@inbox_router.patch("/inbox/{id}/state", summary="Update Inbox State")
def update_inbox_state(id: str, state: str = Query(...), _: AuthUser = Depends(require_roles("agent", "admin"))):
    if id not in DB["interactions"]:
        return _error("inbox.not_found", "Inbox item not found", status_code=404)
    # Fire-and-forget broadcast; in this sync handler we do not await
    try:
        # Schedule broadcast using background task semantics in production; here, just ignore
        pass
    finally:
        return {"status": "ok", "id": id, "state": state}


# =========================
# Connectors and Webhooks
# =========================

conn_router = APIRouter(prefix=API_PREFIX, tags=["Connectors"])

def _verify_email_webhook(secret: str) -> bool:
    expected = get_env("EMAIL_WEBHOOK_SECRET", "")
    return expected != "" and secret == expected

@conn_router.post("/channels/email/webhook", summary="Email webhook intake")
def email_webhook(x_provider_signature: Optional[str] = Header(None)):
    if not _verify_email_webhook(x_provider_signature or ""):
        return _error("webhook.invalid_signature", "Invalid signature", status_code=400)
    # Normalize and persist as interaction
    iid = _gen_id()
    DB["interactions"][iid] = {"id": iid, "customer_id": "unknown", "channel": "email", "subject": "Inbound", "summary": "Webhook"}
    return {"status": "ok"}

@conn_router.post("/channels/chat/webhook", summary="Chat webhook intake")
def chat_webhook():
    iid = _gen_id()
    DB["interactions"][iid] = {"id": iid, "customer_id": "unknown", "channel": "chat", "subject": "Inbound", "summary": "Webhook"}
    return {"status": "ok"}

@conn_router.post("/channels/social/webhook", summary="Social webhook intake")
def social_webhook():
    iid = _gen_id()
    DB["interactions"][iid] = {"id": iid, "customer_id": "unknown", "channel": "social", "subject": "Inbound", "summary": "Webhook"}
    return {"status": "ok"}

@conn_router.post("/channels/cti/webhook", summary="CTI webhook intake")
def cti_webhook():
    iid = _gen_id()
    DB["interactions"][iid] = {"id": iid, "customer_id": "unknown", "channel": "voice", "subject": "Inbound", "summary": "Webhook"}
    return {"status": "ok"}

@conn_router.get("/connectors/{type}/health", summary="Connector Health")
def connector_health(type: str, _: AuthUser = Depends(require_roles("admin"))):
    return {"type": type, "status": "ok"}

@conn_router.post("/connectors/{type}/send", summary="Send via connector")
def connector_send(type: str, payload: Dict[str, Any], _: AuthUser = Depends(require_roles("agent", "admin"))):
    # Stub sending
    return {"status": "queued", "type": type, "id": _gen_id()}


# ==========================
# Reporting / Analytics API
# ==========================

rep_router = APIRouter(prefix=API_PREFIX, tags=["Reports"])

@rep_router.get("/reports/kpis", response_model=KPIResponse, summary="Top KPIs")
def get_kpis(_: AuthUser = Depends(require_roles("agent", "admin"))):
    return KPIResponse(
        open_srs=len([1 for v in DB["service_requests"].values() if v.get("status") not in {"Resolved", "Closed"}]),
        sla_risk=len([1 for _ in DB["service_requests"].values()]),  # stub
        open_complaints=len([1 for v in DB["complaints"].values() if v.get("status") != "Closed"]),
        inbox_today=len(DB["interactions"]),
    )


@rep_router.get("/reports/timeseries", response_model=List[TimeSeriesPoint], summary="Timeseries Metrics")
def get_timeseries(metric: str = Query(..., description="metric key"), _: AuthUser = Depends(require_roles("agent", "admin"))):
    series = [TimeSeriesPoint(ts=f"2025-11-{d:02d}", value=float(d)) for d in range(1, 8)]
    return series


# =========
# Audit API
# =========

audit_router = APIRouter(prefix=API_PREFIX, tags=["Audit"])

@audit_router.get("/audit", response_model=Pagination, summary="List Audit Logs")
def list_audit(
    actor: Optional[str] = None,
    entity: Optional[str] = None,
    from_: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    _: AuthUser = Depends(require_roles("admin")),
):
    # Basic filtering stub
    items = DB["audit"]
    items = [it for it in items if (not actor or it.get("actor_id") == actor)]
    items = [it for it in items if (not entity or it.get("entity_type") == entity)]
    # from_/to not applied in stub
    return paginate(items, page, page_size)


# ===========
# Settings API
# ===========

settings_router = APIRouter(prefix=API_PREFIX + "/settings", tags=["Settings"])

@settings_router.get("/profile", response_model=ProfileSettings, summary="Get Profile Settings")
def get_profile(_: AuthUser = Depends(require_roles("agent", "admin"))):
    return ProfileSettings(full_name="Demo User", phone=None)

@settings_router.put("/profile", response_model=ProfileSettings, summary="Update Profile Settings")
def put_profile(body: ProfileSettings, _: AuthUser = Depends(require_roles("agent", "admin"))):
    return body

@settings_router.get("/preferences", response_model=Preferences, summary="Get Preferences")
def get_preferences(_: AuthUser = Depends(require_roles("agent", "admin"))):
    return Preferences()

@settings_router.put("/preferences", response_model=Preferences, summary="Update Preferences")
def put_preferences(body: Preferences, _: AuthUser = Depends(require_roles("agent", "admin"))):
    return body


# ======================
# Router Registration
# ======================

app.include_router(auth_router)
app.include_router(urp_router)
app.include_router(cust_router)
app.include_router(inter_router)
app.include_router(sr_router)
app.include_router(comp_router)
app.include_router(inbox_router)
app.include_router(conn_router)
app.include_router(rep_router)
app.include_router(audit_router)
app.include_router(settings_router)
