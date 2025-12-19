# pycarta - Python Interface to Carta Platform

`pycarta` is a comprehensive Python library that streamlines administrative actions, service development, and integration with the Carta platform. It provides authentication controls, service hosting capabilities, MQTT messaging, data processing utilities, and seamless integration with external platforms like Seven Bridges Genomics.

## Key Features

### 🔐 Authentication & Authorization
- Unified authentication against Carta platform using AWS Cognito
- Support for profiles, environment variables, and interactive login
- Fine-grained authorization controls with the `@pycarta.authorize` decorator
- Automatic authentication management across all modules

```python
import pycarta

@pycarta.authorize(groups=["MyOrg:MyGroup"])
def my_function(*args, **kwds):
    # Code you want to protect.
    pass
```

### 🌐 Service Development 
- Create REST APIs using the `@pycarta.service` decorator
- Automatic FastAPI integration with OpenAPI documentation
- WebSocket support for real-time communication
- Built-in authentication and authorization for service endpoints

```python
import pycarta as pc

@pc.service("my-namespace", "my-service").get()
def hello_world():
    return {"message": "Hello from my service!"}

# Connect to Carta and serve your API
pc.service.connect()
```

### 📡 MQTT Messaging
- Publisher and subscriber support with decorator-based APIs
- Both synchronous and asynchronous MQTT clients
- TLS/SSL support with credentials management
- Quality of Service (QoS) support

```python
from pycarta.mqtt import publish

@publish("my/topic")
def send_notification(message: str):
    return {"notification": message}
```

### 🗃️ Data Management
- **FormsDB**: Schema-aware form data management with hierarchical organization
- **Tablify**: JSON-to-DataFrame conversion with intelligent column ordering
- **Graph**: NetworkX-based graph operations and algorithms

### 🧬 Seven Bridges Integration
- Execute SBG Apps and Workflows as Python functions
- Automatic file upload/download management
- Multi-strategy authentication with fallback options
- Progress tracking and cleanup management

```python
from pycarta.sbg import ExecutableProject

pc.login()
project = ExecutableProject("division/my-project")
result = project.my_workflow(input_file="data.csv")
```

### 🛠️ Administrative Tools
- User and group management
- Service registration and namespace management  
- Permission and resource access control
- Secret management for secure credential storage

# Installation

```bash
pip install pycarta
```

For development or access to the latest features:

```bash
git clone https://gitlab.com/contextualize/pycarta
cd pycarta
pip install -e .
```

# Quick Start

## Authentication

```python
import pycarta as pc

# Login using profiles (recommended)
pc.login(profile="my-profile")

# Or login interactively
pc.login(interactive=True)

# Or use environment variables
# CARTA_USER, CARTA_PASS, CARTA_PROFILE, CARTA_ENV
pc.login()
```

## Creating a Service

```python
import pycarta as pc

# Create a simple service
@pc.service("my-namespace", "calculator").get("/add/{a}/{b}")
def add_numbers(a: int, b: int):
    return {"result": a + b}

# Start the service
if __name__ == "__main__":
    pc.service.connect()
```

## MQTT Messaging

```python
from pycarta.mqtt import publish, subscribe

@publish("sensors/temperature")  
def temperature_reading():
    return {"temperature": 23.5, "timestamp": "2024-01-01T12:00:00Z"}

@subscribe("alerts/system")
def handle_alert(message):
    print(f"Alert received: {message}")
```

## Data Processing

```python
from pycarta.tablify import tablify
from pycarta.formsdb import Folder, Schema

# Convert JSON forms to DataFrame
df = tablify(json_data, schema=my_schema)

# Work with FormsDB
folder = Folder("my-project/data")
schema = Schema.create("user-form", json_schema)
```

# Module Overview

## Authentication (`pycarta.auth`)
- **CartaAgent**: Main authentication agent with AWS Cognito integration
- **Profile**: User profile management for storing credentials
- **Interactive Login**: UI components with headless environment detection
- **Multi-factor Authentication**: Support for various auth methods

## Administrative Tools (`pycarta.admin`)
- **User Management**: Create, search, and manage users
- **Group Management**: Create groups and manage membership
- **Service Management**: Register services and manage namespaces
- **Permission System**: Fine-grained access control
- **Secret Management**: Secure credential storage

## Service Development (`pycarta.services`)
- **Service Decorator**: `@pycarta.service(namespace, service)` for creating APIs
- **HTTP Methods**: Support for GET, POST, PUT, PATCH, DELETE
- **WebSocket Proxy**: Real-time communication capabilities
- **Auto-documentation**: Automatic OpenAPI/ReDoc generation
- **Authentication**: Built-in service-level authorization

## MQTT Messaging (`pycarta.mqtt`)
- **Publisher**: `@publish(topic)` decorator for message publishing
- **Subscriber**: `@subscribe(topic)` decorator for message handling
- **Async Support**: Both paho-mqtt and aiomqtt client support
- **TLS/SSL**: Secure connections with credential management
- **QoS**: Quality of Service support for reliable messaging

## Data Management
### FormsDB (`pycarta.formsdb`)
- **Hierarchical Organization**: Folder-based data organization
- **Schema Management**: JSON Schema support for validation
- **Data Versioning**: Track changes and schema evolution
- **RESTful API**: Integration with Carta FormsDB service

### Tablify (`pycarta.tablify`)
- **JSON to DataFrame**: Convert form data to pandas DataFrames
- **Schema-aware Processing**: Intelligent column ordering
- **Nested Data Handling**: Partial melting for complex structures
- **Command Line Interface**: CLI support for batch processing

### Graph Operations (`pycarta.graph`)
- **NetworkX Integration**: Built on NetworkX DiGraph
- **Algorithms**: Graph algorithms and utilities
- **Visitor Pattern**: Extensible graph traversal

## Seven Bridges Integration (`pycarta.sbg`)
- **ExecutableApp**: Convert SBG Apps to Python functions
- **ExecutableProject**: Convert entire projects to Python classes
- **File Management**: Automatic upload/download handling
- **Authentication**: Multi-strategy authentication with fallback
- **Progress Tracking**: Built-in progress monitoring

# Carta Platform Concepts

## Core Entities

**User**: Someone with a registered Carta account

**Group**: Collection of users for permission management. Use namespaced naming (e.g., "MyOrg:MyGroup") to avoid conflicts

**Project**: Basic organizational unit in Carta, typically correlating to an organization

**Service**: API endpoints exposed through Carta with namespace/service scoping:
`https://carta.contextualize.us.com/<namespace>/<service>/{endpoints}`

**Resource**: Shareable entities including projects, services, and secrets

**Namespace**: Unique identifier scope for services across the Carta platform

## Permission System

Carta uses a comprehensive permission model:
- **Owner**: Full control including permission management
- **Admin**: Can grant/revoke permissions (except to owner)  
- **Read**: View access to resource
- **Write**: Modify access to resource
- **Execute**: Can call/run the resource (especially relevant for services)
- **Clone**: Can duplicate the resource

## Secrets Management

Secure storage for sensitive information like credentials and tokens:
- User-specific (cannot be shared)
- Encrypted at rest
- Accessible across sessions
- Useful for third-party service integration

# Feature Request/Bug-Fix

For login issues, please contact
<customer.service@contextualize.us.com>.

To request a new feature or to report a bug, please email
[pycarta](mailto:a.t.901104402411.u-26296181.4165918c-9632-497d-8601-dfcb2f66ba78@tasks.clickup.com).
Please be sure to describe the goal of the new feature or, for a bug
report, a minimum code that reproduces the error. Note that if you
submit a feature request or bug report, the developers reserve the right
to contact you about that request.
