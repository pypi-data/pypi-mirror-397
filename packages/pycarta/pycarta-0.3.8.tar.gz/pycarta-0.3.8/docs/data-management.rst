.. _data-management:

Data Management
===============

``pycarta`` provides several modules for data management, processing, and transformation. These modules help you work with structured data, forms, and graph operations.

.. contents::
   :local:
   :depth: 2

FormsDB
-------

The ``pycarta.formsdb`` module provides schema-aware data management with hierarchical organization, allowing you to store, retrieve, and manage form data with JSON schema validation.

Overview
^^^^^^^^

FormsDB features:

- **Hierarchical Organization**: Folder-based data organization with path support
- **Schema Management**: JSON Schema support for data validation
- **Data Versioning**: Track changes and schema evolution over time
- **RESTful API**: Integration with Carta FormsDB service
- **CRUD Operations**: Full create, read, update, delete support

Basic Usage
^^^^^^^^^^^

.. code:: python

    import pycarta as pc
    from pycarta.formsdb import FormsDb

    # First, authenticate with pycarta
    pc.login()
    agent = pc.get_agent()

    # Initialize FormsDB with credentials and project
    formsdb = FormsDb(credentials=agent, project_id="my-project-id")

    # Create a folder hierarchy
    root_folder = formsdb.folder.create("my-project")
    surveys_folder = formsdb.folder.create("my-project/surveys")
    
    # Define a JSON schema for validation  
    user_schema = formsdb.schema.create("user-survey", {
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "age": {"type": "integer", "minimum": 0, "maximum": 150},
            "email": {"type": "string", "format": "email"},
            "responses": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["name", "age"]
    })

Working with Folders
^^^^^^^^^^^^^^^^^^^^

.. code:: python

    import pycarta as pc
    from pycarta.formsdb import FormsDb

    # Initialize FormsDB
    pc.login()
    formsdb = FormsDb(credentials=pc.get_agent(), project_id="my-project")

    # Create folders
    project_folder = formsdb.folder.create("research-project")
    data_folder = formsdb.folder.create("research-project/data")
    results_folder = formsdb.folder.create("research-project/results")
    
    # Get existing folders
    folder = formsdb.folder.get("research-project/data")
    
    # List folder contents
    contents = formsdb.folder.list_contents("research-project")
    
    # Delete folders (use with caution)
    # formsdb.folder.delete("research-project/temp")

Working with Schemas
^^^^^^^^^^^^^^^^^^^^

.. code:: python

    import pycarta as pc
    from pycarta.formsdb import FormsDb

    # Initialize FormsDB
    pc.login()
    formsdb = FormsDb(credentials=pc.get_agent(), project_id="my-project")

    # Create a comprehensive schema
    survey_schema = formsdb.schema.create("customer-feedback", {
        "type": "object",
        "title": "Customer Feedback Survey",
        "description": "Collect customer satisfaction data",
        "properties": {
            "customer_id": {"type": "string"},
            "satisfaction": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5,
                "description": "Satisfaction rating 1-5"
            },
            "feedback": {"type": "string"},
            "recommend": {"type": "boolean"},
            "contact_info": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "phone": {"type": "string"}
                }
            }
        },
        "required": ["customer_id", "satisfaction"]
    })
    
    # Update schema
    updated_schema = formsdb.schema.update("customer-feedback", {
        # Updated schema definition
        "properties": {
            # Add new fields or modify existing ones
            "survey_date": {"type": "string", "format": "date"}
        }
    })
    
    # Link schema to folder
    formsdb.schema.link("customer-feedback", "surveys/customer")

Working with Data
^^^^^^^^^^^^^^^^^

.. code:: python

    import pycarta as pc
    from pycarta.formsdb import FormsDb

    # Initialize FormsDB
    pc.login()
    formsdb = FormsDb(credentials=pc.get_agent(), project_id="my-project")

    # Create data with schema validation
    customer_data = {
        "customer_id": "CUST001",
        "satisfaction": 4,
        "feedback": "Great service!",
        "recommend": True,
        "contact_info": {
            "email": "customer@example.com",
            "phone": "+1-555-0123"
        }
    }
    
    folder = formsdb.folder.get("surveys/customer")
    schema = formsdb.schema.get("customer-feedback")
    
    # Create data entry (validates against schema)
    data_entry = formsdb.data.create(folder, schema, customer_data)
    
    # Retrieve data
    retrieved_data = formsdb.data.get(data_entry.id)
    
    # Update data
    updated_data = formsdb.data.update(data_entry.id, {
        "satisfaction": 5,
        "feedback": "Excellent service!"
    })
    
    # List all data in folder
    all_entries = formsdb.data.list_by_folder(folder)

Advanced Features
^^^^^^^^^^^^^^^^^

.. code:: python

    import pycarta as pc
    from pycarta.formsdb import FormsDb
    from datetime import datetime

    # Initialize FormsDB
    formsdb = FormsDb(credentials=pc.get_agent(), project_id="my-project")

    # Data with metadata
    metadata = {
        "created_by": "researcher_001",
        "study_phase": "pilot",
        "collection_date": datetime.now().isoformat()
    }
    
    data_with_metadata = formsdb.data.create(
        folder=folder,
        schema=schema,
        data=survey_response,
        metadata=metadata
    )
    
    # Query data by metadata
    pilot_data = formsdb.data.query_by_metadata({"study_phase": "pilot"})
    
    # Schema evolution - handle changes over time
    schema_v2 = formsdb.schema.create("customer-feedback-v2", {
        # Evolved schema with new fields
        "allOf": [
            {"$ref": "#/definitions/customer-feedback"},
            {
                "properties": {
                    "nps_score": {"type": "integer", "minimum": 0, "maximum": 10}
                }
            }
        ]
    })

Tablify
-------

The ``pycarta.tablify`` module converts JSON form data to pandas DataFrames with intelligent column ordering based on JSON schemas.

Overview
^^^^^^^^

Tablify features:

- **Schema-aware Processing**: Intelligent column ordering based on JSON schemas
- **Nested Data Handling**: Partial melting for complex data structures  
- **Pandas Integration**: Direct conversion to pandas DataFrames
- **Command Line Interface**: CLI support for batch processing
- **Flexible Configuration**: Customizable conversion options

Basic Usage
^^^^^^^^^^^

.. code:: python

    from pycarta.tablify import tablify
    import pandas as pd

    # Simple JSON data
    json_data = [
        {"name": "Alice", "age": 30, "city": "New York"},
        {"name": "Bob", "age": 25, "city": "San Francisco"},
        {"name": "Charlie", "age": 35, "city": "Chicago"}
    ]
    
    # Convert to DataFrame
    df = tablify(json_data)
    print(df)
    #      name  age           city
    # 0   Alice   30       New York
    # 1     Bob   25  San Francisco
    # 2 Charlie   35        Chicago

Schema-Aware Conversion
^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from pycarta.tablify import tablify

    # JSON data with various field types
    form_data = [
        {
            "id": "001",
            "demographics": {"age": 30, "gender": "F"},
            "scores": [85, 92, 78],
            "metadata": {"created": "2024-01-01"}
        },
        {
            "id": "002", 
            "demographics": {"age": 25, "gender": "M"},
            "scores": [90, 88, 95],
            "metadata": {"created": "2024-01-02"}
        }
    ]
    
    # Define schema for column ordering
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string", "order": 1},
            "demographics": {
                "type": "object", 
                "order": 2,
                "properties": {
                    "age": {"type": "integer", "order": 1},
                    "gender": {"type": "string", "order": 2}
                }
            },
            "scores": {"type": "array", "order": 3},
            "metadata": {"type": "object", "order": 4}
        }
    }
    
    # Convert with schema-based column ordering
    df = tablify(form_data, schema=schema)
    print(df.columns.tolist())
    # Columns will be ordered according to schema

Partial Melting
^^^^^^^^^^^^^^^

Handle nested arrays and objects with partial melting:

.. code:: python

    from pycarta.tablify import tablify

    # Data with nested arrays
    nested_data = [
        {
            "participant": "P001",
            "responses": [
                {"question": "Q1", "answer": "Yes", "confidence": 5},
                {"question": "Q2", "answer": "No", "confidence": 3}
            ]
        },
        {
            "participant": "P002",
            "responses": [
                {"question": "Q1", "answer": "No", "confidence": 4},
                {"question": "Q2", "answer": "Yes", "confidence": 5}
            ]
        }
    ]
    
    # Melt nested responses into separate rows
    df = tablify(nested_data, melt=["responses"])
    print(df)
    # participant responses.question responses.answer responses.confidence
    # 0       P001               Q1              Yes                     5
    # 1       P001               Q2               No                     3
    # 2       P002               Q1               No                     4
    # 3       P002               Q2              Yes                     5

Advanced Configuration
^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from pycarta.tablify import tablify

    complex_data = [
        {
            "study_id": "S001",
            "participant": {"id": "P001", "group": "A"},
            "sessions": [
                {
                    "session": 1,
                    "tasks": [
                        {"task": "memory", "score": 85},
                        {"task": "attention", "score": 92}
                    ]
                },
                {
                    "session": 2, 
                    "tasks": [
                        {"task": "memory", "score": 88},
                        {"task": "attention", "score": 90}
                    ]
                }
            ]
        }
    ]
    
    # Configure melting for multiple levels
    df = tablify(
        complex_data,
        melt=["sessions", "sessions.tasks"],  # Melt both sessions and tasks
        schema=schema,
        flatten_nested=True  # Flatten nested objects
    )

Command Line Interface
^^^^^^^^^^^^^^^^^^^^^^

Tablify provides a CLI for batch processing:

.. code:: bash

    # Convert JSON file to CSV
    tablify input.json output.csv
    
    # With schema file
    tablify input.json output.csv --schema schema.json
    
    # With melting configuration
    tablify input.json output.csv --melt responses --melt sessions
    
    # Output to different formats
    tablify input.json output.xlsx  # Excel
    tablify input.json output.parquet  # Parquet

Integration with FormsDB
^^^^^^^^^^^^^^^^^^^^^^^^

Combine FormsDB and Tablify for complete data workflows:

.. code:: python

    import pycarta as pc
    from pycarta.formsdb import FormsDb
    from pycarta.tablify import tablify

    # Initialize FormsDB
    pc.login()
    formsdb = FormsDb(credentials=pc.get_agent(), project_id="my-project")

    # Retrieve data from FormsDB
    folder = formsdb.folder.get("surveys/customer-feedback")
    all_responses = formsdb.data.list_by_folder(folder)
    
    # Extract the data portion
    json_data = [response.data for response in all_responses]
    
    # Convert to DataFrame for analysis
    schema = formsdb.schema.get("customer-feedback")
    df = tablify(json_data, schema=schema._schema)
    
    # Perform analysis
    satisfaction_avg = df['satisfaction'].mean()
    print(f"Average satisfaction: {satisfaction_avg}")
    
    # Export results
    df.to_csv('customer_feedback_analysis.csv', index=False)

Graph Operations
----------------

The ``pycarta.graph`` module provides NetworkX-based graph operations with a visitor pattern for extensible graph algorithms.

Overview
^^^^^^^^

Graph module features:

- **NetworkX Integration**: Built on NetworkX DiGraph for robust graph operations
- **Vertex Objects**: Rich vertex objects with metadata support
- **Visitor Pattern**: Extensible graph traversal and algorithms
- **Algorithm Library**: Common graph algorithms and utilities

Basic Usage
^^^^^^^^^^^

.. code:: python

    from pycarta.graph import Graph
    from pycarta.graph.vertex import Vertex

    # Create a graph
    graph = Graph()
    
    # Create vertices with data
    v1 = Vertex("node_1", {"name": "Alice", "role": "Manager"})
    v2 = Vertex("node_2", {"name": "Bob", "role": "Developer"}) 
    v3 = Vertex("node_3", {"name": "Charlie", "role": "Designer"})
    
    # Add vertices to graph
    graph.add_vertex(v1)
    graph.add_vertex(v2)
    graph.add_vertex(v3)
    
    # Add edges (relationships)
    graph.add_edge(v1, v2, weight=1.0, relationship="manages")
    graph.add_edge(v1, v3, weight=1.0, relationship="manages")
    graph.add_edge(v2, v3, weight=0.5, relationship="collaborates")

Visitor Pattern
^^^^^^^^^^^^^^^

Implement custom graph algorithms using the visitor pattern:

.. code:: python

    from pycarta.graph.visitor import Visitor

    class DataCollectionVisitor(Visitor):
        def __init__(self):
            self.collected_data = []
            
        def visit(self, vertex):
            """Collect data from each vertex."""
            self.collected_data.append({
                "id": vertex.id,
                "name": vertex.data.get("name"),
                "role": vertex.data.get("role")
            })
            
    class RoleCountVisitor(Visitor):
        def __init__(self):
            self.role_counts = {}
            
        def visit(self, vertex):
            """Count vertices by role."""
            role = vertex.data.get("role", "Unknown")
            self.role_counts[role] = self.role_counts.get(role, 0) + 1
    
    # Use visitors
    collector = DataCollectionVisitor()
    graph.accept(collector)
    print("Collected data:", collector.collected_data)
    
    counter = RoleCountVisitor()
    graph.accept(counter)
    print("Role counts:", counter.role_counts)

Graph Algorithms
^^^^^^^^^^^^^^^^

Access NetworkX algorithms through the graph:

.. code:: python

    from pycarta.graph import Graph
    import networkx as nx

    # Create a more complex graph
    graph = Graph()
    
    # Add vertices and edges for analysis
    vertices = [Vertex(f"v{i}", {"value": i}) for i in range(6)]
    for v in vertices:
        graph.add_vertex(v)
    
    # Create connections
    edges = [(0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 5)]
    for i, j in edges:
        graph.add_edge(vertices[i], vertices[j])
    
    # Access underlying NetworkX graph for algorithms
    nx_graph = graph._graph  # Access NetworkX DiGraph
    
    # Shortest path
    path = nx.shortest_path(nx_graph, vertices[0].id, vertices[5].id)
    print("Shortest path:", path)
    
    # Centrality measures
    centrality = nx.betweenness_centrality(nx_graph)
    print("Betweenness centrality:", centrality)
    
    # Connected components (for undirected version)
    undirected = nx_graph.to_undirected()
    components = list(nx.connected_components(undirected))
    print("Connected components:", components)

Advanced Graph Operations
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from pycarta.graph import Graph
    from pycarta.graph.vertex import Vertex
    from pycarta.graph.visitor import Visitor
    
    class PathFindingVisitor(Visitor):
        def __init__(self, target_id):
            self.target_id = target_id
            self.path = []
            self.found = False
            
        def visit(self, vertex):
            self.path.append(vertex.id)
            if vertex.id == self.target_id:
                self.found = True
                return True  # Stop traversal
            return False
    
    class SubgraphVisitor(Visitor):
        def __init__(self, condition_func):
            self.condition_func = condition_func
            self.matching_vertices = []
            
        def visit(self, vertex):
            if self.condition_func(vertex):
                self.matching_vertices.append(vertex)
    
    # Example usage
    graph = Graph()
    # ... populate graph with vertices and edges ...
    
    # Find specific vertex
    finder = PathFindingVisitor("target_node")
    graph.accept(finder)
    
    # Find vertices matching condition
    role_filter = SubgraphVisitor(lambda v: v.data.get("role") == "Manager")
    graph.accept(role_filter)
    print("Managers:", [v.data.get("name") for v in role_filter.matching_vertices])

Best Practices
--------------

FormsDB Best Practices
^^^^^^^^^^^^^^^^^^^^^^

- **Schema Design**: Design schemas to be forward-compatible
- **Folder Structure**: Use logical, hierarchical folder organization
- **Data Validation**: Always validate data against schemas
- **Metadata Usage**: Store relevant metadata for data provenance
- **Version Control**: Track schema changes and data versions

Tablify Best Practices
^^^^^^^^^^^^^^^^^^^^^^

- **Schema Definition**: Define schemas for consistent column ordering
- **Memory Management**: Process large datasets in chunks if needed
- **Data Types**: Ensure proper data type handling in schemas
- **Nested Data**: Use melting judiciously for nested structures
- **Performance**: Consider DataFrame operations for large datasets

Graph Best Practices
^^^^^^^^^^^^^^^^^^^^^

- **Vertex IDs**: Use meaningful, unique vertex identifiers
- **Edge Weights**: Include edge weights for algorithm compatibility
- **Data Storage**: Store relevant data in vertex and edge attributes
- **Algorithm Choice**: Choose appropriate NetworkX algorithms for your use case
- **Memory Usage**: Be mindful of memory usage with large graphs

Integration Examples
--------------------

Complete Data Pipeline
^^^^^^^^^^^^^^^^^^^^^^

Here's an example combining all three modules:

.. code:: python

    from pycarta.formsdb import Folder, Schema, Data
    from pycarta.tablify import tablify
    from pycarta.graph import Graph
    from pycarta.graph.vertex import Vertex
    import pandas as pd

    # 1. Set up FormsDB structure
    pc.login()
    formsdb = FormsDb(credentials=pc.get_agent(), project_id="social-network")
    
    project_folder = formsdb.folder.create("social-network-study")
    
    # Create schema for participant data
    participant_schema = formsdb.schema.create("participant", {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "connections": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
    })
    
    # 2. Store participant data
    participants = [
        {"id": "P001", "name": "Alice", "age": 30, "connections": ["P002", "P003"]},
        {"id": "P002", "name": "Bob", "age": 25, "connections": ["P001", "P004"]},
        {"id": "P003", "name": "Charlie", "age": 35, "connections": ["P001", "P004"]},
        {"id": "P004", "name": "Diana", "age": 28, "connections": ["P002", "P003"]}
    ]
    
    for participant in participants:
        formsdb.data.create(project_folder, participant_schema, participant)
    
    # 3. Retrieve and convert to DataFrame
    all_data = formsdb.data.list_by_folder(project_folder)
    json_data = [entry.data for entry in all_data]
    df = tablify(json_data, schema=participant_schema._schema)
    
    print("Participant DataFrame:")
    print(df)
    
    # 4. Build social network graph
    graph = Graph()
    
    # Add participants as vertices
    vertices = {}
    for _, row in df.iterrows():
        vertex = Vertex(row['id'], {
            "name": row['name'],
            "age": row['age']
        })
        graph.add_vertex(vertex)
        vertices[row['id']] = vertex
    
    # Add connections as edges
    for _, row in df.iterrows():
        participant_id = row['id']
        connections = row['connections']
        for connection_id in connections:
            if connection_id in vertices:
                graph.add_edge(
                    vertices[participant_id],
                    vertices[connection_id],
                    relationship="friend"
                )
    
    # 5. Analyze the social network
    from pycarta.graph.visitor import Visitor
    
    class NetworkAnalysisVisitor(Visitor):
        def __init__(self):
            self.analysis = {
                "total_participants": 0,
                "age_groups": {"20-29": 0, "30-39": 0},
                "connections": []
            }
            
        def visit(self, vertex):
            self.analysis["total_participants"] += 1
            
            age = vertex.data.get("age", 0)
            if 20 <= age < 30:
                self.analysis["age_groups"]["20-29"] += 1
            elif 30 <= age < 40:
                self.analysis["age_groups"]["30-39"] += 1
    
    analyzer = NetworkAnalysisVisitor()
    graph.accept(analyzer)
    
    print("\\nNetwork Analysis:")
    print(f"Total participants: {analyzer.analysis['total_participants']}")
    print(f"Age distribution: {analyzer.analysis['age_groups']}")
    
    # 6. Export results
    df.to_csv("participant_data.csv", index=False)
    
    print("\\nData pipeline completed!")

This example demonstrates a complete workflow using all three data management modules to collect, process, analyze, and export research data.