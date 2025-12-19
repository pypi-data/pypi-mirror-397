.. _services:

Service Development
===================

The ``pycarta.services`` module provides a powerful decorator-based framework for creating REST APIs that are automatically hosted and authenticated through the Carta platform. This allows you to turn Python functions into production-ready web services with minimal configuration.

.. contents::
   :local:
   :depth: 2

Overview
--------

Services in pycarta are built on FastAPI and provide:

- **Automatic API Generation**: Turn Python functions into REST endpoints
- **Built-in Authentication**: Integrated Carta authentication for all endpoints  
- **Type Safety**: Request/response validation based on type hints
- **Auto-documentation**: Swagger/OpenAPI documentation generation
- **WebSocket Support**: Real-time communication capabilities
- **Permission Management**: Fine-grained authorization controls

Basic Usage
-----------

Creating Your First Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    import pycarta as pc

    # Create a simple GET endpoint
    @pc.service("my-namespace", "hello-world").get()
    def hello():
        """Say hello to the world."""
        return {"message": "Hello, World!"}

    # Start the service
    if __name__ == "__main__":
        pc.service.connect()

This creates a service accessible at:
``https://carta.contextualize.us.com/my-namespace/hello-world/``

HTTP Methods
^^^^^^^^^^^^

Support for all standard HTTP methods:

.. code:: python

    import pycarta as pc
    from pydantic import BaseModel

    service = pc.service("api", "users")

    # GET endpoint with path parameters
    @service.get("/users/{user_id}")
    def get_user(user_id: int):
        return {"user_id": user_id, "name": f"User {user_id}"}

    # POST endpoint with JSON body
    class UserCreate(BaseModel):
        name: str
        email: str
        age: int

    @service.post("/users")
    def create_user(user: UserCreate):
        return {"message": f"Created user {user.name}"}

    # PUT endpoint for updates
    @service.put("/users/{user_id}")
    def update_user(user_id: int, user: UserCreate):
        return {"message": f"Updated user {user_id}"}

    # DELETE endpoint
    @service.delete("/users/{user_id}")
    def delete_user(user_id: int):
        return {"message": f"Deleted user {user_id}"}

    # PATCH endpoint for partial updates
    @service.patch("/users/{user_id}")
    def patch_user(user_id: int, updates: dict):
        return {"message": f"Patched user {user_id}", "updates": updates}

Advanced Routing
^^^^^^^^^^^^^^^^

Customize your endpoints with path parameters, query parameters, and request bodies:

.. code:: python

    import pycarta as pc
    from typing import Optional, List

    service = pc.service("api", "data")

    # Path parameters
    @service.get("/data/{category}/{item_id}")
    def get_item(category: str, item_id: int):
        return {"category": category, "item_id": item_id}

    # Query parameters
    @service.get("/search")
    def search_items(q: str, limit: Optional[int] = 10, offset: int = 0):
        return {
            "query": q,
            "limit": limit,
            "offset": offset,
            "results": []
        }

    # Mixed parameters
    @service.get("/categories/{category}/items")
    def get_category_items(
        category: str,
        page: int = 1,
        per_page: int = 20,
        sort: str = "name"
    ):
        return {
            "category": category,
            "page": page,
            "per_page": per_page,
            "sort": sort
        }

Authentication and Authorization
-------------------------------

Service-Level Authentication
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All service endpoints automatically require Carta authentication. Users must be logged in to access any endpoint.

Fine-Grained Authorization
^^^^^^^^^^^^^^^^^^^^^^^^^^

Control access to your service with user and group-based permissions:

.. code:: python

    import pycarta as pc

    # Create service with specific authorization
    service = pc.service("secure-api", "admin-tools")

    # Authorize specific groups
    service.authorize(groups=["MyOrg:Admins", "MyOrg:PowerUsers"], role="Editor")

    # Authorize specific users
    service.authorize(users=["alice@example.com", "bob@example.com"], role="User")

    @service.get("/admin/stats")
    def get_admin_stats():
        """Only accessible to authorized users."""
        return {"active_users": 150, "total_services": 45}

Permission Roles
^^^^^^^^^^^^^^^^

Available permission roles:

- **Owner**: Full control including permission management
- **Editor**: Can modify service and grant permissions
- **User**: Can execute service endpoints
- **Guest**: Limited read-only access (if supported)

Service Management
------------------

Service Registration
^^^^^^^^^^^^^^^^^^^^

Services are automatically registered when you connect:

.. code:: python

    import pycarta as pc

    # Define your service endpoints
    @pc.service("my-org", "calculator").get("/add/{a}/{b}")
    def add(a: int, b: int):
        return {"result": a + b}

    # This registers the service and starts serving
    if __name__ == "__main__":
        pc.service.connect()

Manual Service Operations
^^^^^^^^^^^^^^^^^^^^^^^^^

You can also manage services programmatically:

.. code:: python

    from pycarta.admin.service import register_service, unregister_service
    from pycarta.services.server import create_namespace, create_service

    # Create namespace if it doesn't exist
    create_namespace("my-org")

    # Create a service
    create_service("my-org", "my-service", "http://localhost:8000")

    # Register with external URL
    register_service("my-org", "my-service", "https://my-server.com")

    # Unregister when done
    unregister_service("my-org", "my-service")

WebSocket Support
-----------------

Real-Time Communication
^^^^^^^^^^^^^^^^^^^^^^^

Services support WebSocket connections for real-time communication:

.. code:: python

    import pycarta as pc
    import asyncio
    from pycarta.services.proxy import CartaServiceManagerProxy

    # WebSocket proxy for handling real-time events
    async def websocket_handler():
        proxy = CartaServiceManagerProxy(
            uri="ws://localhost:8000/ws",
            service="my-namespace/my-service"
        )
        
        async for connection in proxy.client:
            try:
                await proxy.listen()
            except Exception as e:
                print(f"WebSocket error: {e}")

Service Proxy
^^^^^^^^^^^^^

The proxy handles bidirectional communication between Carta and your service:

.. code:: python

    from pycarta.services.proxy import WebsocketProxy

    class MyServiceProxy(WebsocketProxy):
        async def handler(self, request):
            """Handle incoming requests from Carta."""
            # Process the request
            response = await self.process_request(request)
            return response

        async def process_request(self, request):
            # Your request processing logic
            return {"status": "processed", "data": request}

Documentation
-------------

Automatic Documentation
^^^^^^^^^^^^^^^^^^^^^^^^

Services automatically generate OpenAPI documentation:

.. code:: python

    import pycarta as pc

    service = pc.service("docs-demo", "calculator")

    @service.get("/add/{a}/{b}")
    def add_numbers(a: int, b: int) -> dict:
        """
        Add two numbers together.
        
        Args:
            a: First number to add
            b: Second number to add
            
        Returns:
            Dictionary containing the sum of a and b
        """
        return {"result": a + b}

Documentation is available at:
``https://carta.contextualize.us.com/docs-demo/calculator/docs``

Custom Documentation
^^^^^^^^^^^^^^^^^^^^

Access ReDoc documentation programmatically:

.. code:: python

    service = pc.service("my-namespace", "my-service")
    
    # Get the ReDoc HTML documentation
    docs_response = service.get_redoc()
    
    # The response contains HTML documentation for your service

Deployment and Hosting
----------------------

Local Development
^^^^^^^^^^^^^^^^^

For development, services run locally and proxy through Carta:

.. code:: python

    import pycarta as pc

    @pc.service("dev", "my-app").get("/test")
    def test_endpoint():
        return {"status": "development"}

    if __name__ == "__main__":
        # Runs locally on available port, accessible via Carta
        pc.service.connect()

Production Deployment  
^^^^^^^^^^^^^^^^^^^^^

For production, deploy your service to a server and register the endpoint:

.. code:: python

    from pycarta.admin.service import register_service

    # After deploying to your server
    register_service(
        namespace="production",
        service="my-app", 
        url="https://my-production-server.com"
    )

Service Configuration
^^^^^^^^^^^^^^^^^^^^^

Configure service behavior:

.. code:: python

    import pycarta as pc
    from pycarta.services.server import Service

    # Set global host configuration
    Service.HOST = "https://my-custom-host.com"

    # Create service with cleanup enabled
    service = Service("my-namespace", "my-service", cleanup=True)

Error Handling
--------------

HTTP Exceptions
^^^^^^^^^^^^^^^

Use FastAPI's HTTPException for proper error responses:

.. code:: python

    import pycarta as pc
    from fastapi import HTTPException

    @pc.service("api", "users").get("/users/{user_id}")
    def get_user(user_id: int):
        if user_id < 0:
            raise HTTPException(status_code=400, detail="Invalid user ID")
        if user_id > 1000:
            raise HTTPException(status_code=404, detail="User not found")
        return {"user_id": user_id, "name": f"User {user_id}"}

Custom Exception Handling
^^^^^^^^^^^^^^^^^^^^^^^^^^

Define custom exception handlers:

.. code:: python

    import pycarta as pc
    from fastapi import Request
    from fastapi.responses import JSONResponse

    service = pc.service("api", "custom-errors")

    class CustomException(Exception):
        def __init__(self, message: str):
            self.message = message

    @service.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=400,
            content={"error": "Custom Error", "message": exc.message}
        )

    @service.get("/trigger-error")
    def trigger_error():
        raise CustomException("This is a custom error")

Best Practices
--------------

Service Design
^^^^^^^^^^^^^^

- **Use meaningful namespaces**: Choose descriptive, unique namespace names
- **Version your APIs**: Consider including version in the namespace or endpoint
- **Document thoroughly**: Use docstrings and type hints for auto-documentation
- **Handle errors gracefully**: Provide meaningful error messages and status codes

Security
^^^^^^^^

- **Principle of least privilege**: Only authorize necessary users/groups
- **Validate inputs**: Use Pydantic models for request validation
- **Sanitize outputs**: Be careful about what data you expose
- **Monitor access**: Keep track of who accesses your services

Performance  
^^^^^^^^^^^

- **Use async when appropriate**: For I/O-bound operations
- **Implement caching**: Cache expensive computations
- **Limit payload sizes**: Set reasonable limits on request bodies
- **Monitor resource usage**: Track memory and CPU usage

Example: Complete Service
-------------------------

Here's a complete example showing a real-world service:

.. code:: python

    import pycarta as pc
    from pydantic import BaseModel, EmailStr
    from typing import List, Optional
    from fastapi import HTTPException
    import logging

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Data models
    class User(BaseModel):
        id: Optional[int] = None
        name: str
        email: EmailStr
        age: int
        active: bool = True

    class UserUpdate(BaseModel):
        name: Optional[str] = None
        email: Optional[EmailStr] = None
        age: Optional[int] = None
        active: Optional[bool] = None

    # In-memory store (use a real database in production)
    users_db = {}
    next_id = 1

    # Create service with authorization
    service = pc.service("mycompany", "user-management")
    service.authorize(groups=["MyCompany:Developers"], role="Editor")

    @service.get("/users", response_model=List[User])
    def list_users(skip: int = 0, limit: int = 100):
        """List all users with pagination."""
        users = list(users_db.values())[skip:skip + limit]
        logger.info(f"Listed {len(users)} users")
        return users

    @service.get("/users/{user_id}", response_model=User)
    def get_user(user_id: int):
        """Get a specific user by ID."""
        if user_id not in users_db:
            raise HTTPException(status_code=404, detail="User not found")
        return users_db[user_id]

    @service.post("/users", response_model=User)
    def create_user(user: User):
        """Create a new user."""
        global next_id
        
        # Check if email already exists
        for existing_user in users_db.values():
            if existing_user.email == user.email:
                raise HTTPException(status_code=400, detail="Email already exists")
        
        user.id = next_id
        users_db[next_id] = user
        next_id += 1
        
        logger.info(f"Created user {user.id}: {user.name}")
        return user

    @service.put("/users/{user_id}", response_model=User)
    def update_user(user_id: int, user_update: User):
        """Update an existing user."""
        if user_id not in users_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_update.id = user_id
        users_db[user_id] = user_update
        
        logger.info(f"Updated user {user_id}")
        return user_update

    @service.patch("/users/{user_id}", response_model=User)
    def patch_user(user_id: int, user_update: UserUpdate):
        """Partially update an existing user."""
        if user_id not in users_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        existing_user = users_db[user_id]
        update_data = user_update.dict(exclude_unset=True)
        updated_user = existing_user.copy(update=update_data)
        users_db[user_id] = updated_user
        
        logger.info(f"Patched user {user_id}")
        return updated_user

    @service.delete("/users/{user_id}")
    def delete_user(user_id: int):
        """Delete a user."""
        if user_id not in users_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        del users_db[user_id]
        logger.info(f"Deleted user {user_id}")
        return {"message": f"User {user_id} deleted successfully"}

    @service.get("/health")
    def health_check():
        """Service health check."""
        return {"status": "healthy", "users_count": len(users_db)}

    if __name__ == "__main__":
        # Add some sample data
        sample_users = [
            User(name="Alice Johnson", email="alice@example.com", age=30),
            User(name="Bob Smith", email="bob@example.com", age=25),
        ]
        
        for user in sample_users:
            user.id = next_id
            users_db[next_id] = user
            next_id += 1
        
        logger.info("Starting user management service...")
        pc.service.connect()

This service will be available at:
``https://carta.contextualize.us.com/mycompany/user-management/``

With automatic documentation at:
``https://carta.contextualize.us.com/mycompany/user-management/docs``