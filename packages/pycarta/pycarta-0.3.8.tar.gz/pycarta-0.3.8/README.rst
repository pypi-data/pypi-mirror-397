pycarta - Python Interface to Carta Platform
============================================

``pycarta`` is a comprehensive Python library that streamlines administrative actions, 
service development, and integration with the Carta platform. It provides 
authentication controls, service hosting capabilities, MQTT messaging, data 
processing utilities, and seamless integration with external platforms like 
Seven Bridges Genomics.

Key Features
------------

🔐 **Authentication & Authorization**
   Unified authentication against Carta platform using AWS Cognito with support 
   for profiles, environment variables, and interactive login.

🌐 **Service Development**
   Create REST APIs using decorators with automatic FastAPI integration, 
   WebSocket support, and built-in authentication.

📡 **MQTT Messaging**
   Publisher and subscriber support with decorator-based APIs, both synchronous 
   and asynchronous clients, and TLS/SSL support.

🗃️ **Data Management**
   FormsDB for schema-aware form data management, Tablify for JSON-to-DataFrame 
   conversion, and Graph operations with NetworkX integration.

🧬 **Seven Bridges Integration**
   Execute SBG Apps and Workflows as Python functions with automatic file 
   management and multi-strategy authentication.

🛠️ **Administrative Tools**
   User and group management, service registration, permission control, and 
   secure credential storage.

Quick Example
-------------

.. code:: python

    import pycarta as pc

    # Authentication and authorization
    @pc.authorize(groups=["MyOrg:MyGroup"])
    def my_function(*args, **kwds):
        # Code you want to protect
        pass

    # Service development
    @pc.service("my-namespace", "calculator").get("/add/{a}/{b}")
    def add_numbers(a: int, b: int):
        return {"result": a + b}

    # MQTT messaging
    from pycarta.mqtt import publish

    @publish("sensors/temperature")
    def read_temperature():
        return {"temperature": 23.5, "unit": "celsius"}

Installation
------------

.. code:: bash

    pip install pycarta

For development access:

.. code:: bash

    git clone https://gitlab.com/contextualize/pycarta
    cd pycarta  
    pip install -e .

Definitions
-----------

Throughout, this documentation will refer to a number of Carta-specific
concepts and, while every effort has been made to remain true to the
*prima facia* meaning of terms, there are some nuances that may be important in
certain circumstances.

Group
    One or more users may form a group. This is particularly useful for
    assigning permissions to various Carta resources.

Resource
    Carta resources include authentication, projects, secrets, and services.
    Some, specifically projects and services, can be shared using the Carta
    permission system. Others (authentication and secrets) are specific to the
    user and cannot be shared.

Permissions
    As with other permission systems, Carta Permisions allows owners to share
    access to resources with other users, with groups, and even with other
    resources based on the users' roles. Each resource will have exactly one
    owner, but other users may be granted admin, read, write, execute, and
    clone permissions. An *admin*, like the owner, may grant or rescind
    permission to anyone (except the owner). *read* and *write* permissions
    have their obvious meaning. *execute* permissions, which is particularly
    relevant to services, determine whether a user can make a call to (execute)
    the action accessible through the service API. Finally, *clone* permissions
    allow select resources to be duplicated, similar to forking a repository.

Project
    Projects are the basic unit of organization in Carta. While not required,
    projects generally correlate to an organization.

Secrets
    Carta provides a secure method for temporarily storing small secrets, such
    as usernames, passwords, tokens, etc. and are useful for accessing
    third-party resources. Because of their sensitive nature, secrets may not
    be shared between users.

Service
    A central function for Carta is to act as a proxy that abstracts away the
    details of a backend, third-party resource. Services are APIs exposed
    and authenticated through Carta. These are scoped with a ``namespace``, which
    must be unique across the Carta platform, and a ``service``, the name of the
    service. The functionality of the service is exposed through
    ``https://carta.contextualize.us.com/<namespace>/<service>/{endpoints}``.

User
    A user is someone who has registered an account with Carta.

Feature Request/Bug-Fix
-----------------------

For login issues, please contact customer.service@contextualize.us.com.

To request a new feature or to report a bug, please email
`pycarta <mailto:a.t.901104402411.u-26296181.4165918c-9632-497d-8601-dfcb2f66ba78@tasks.clickup.com>`_.
Please be sure to describe the goal of the new feature or, for a bug report,
a minimum code that reproduces the error. Note that if you submit a feature
request or bug report, the developers reserve the right to contact you about
that request.
