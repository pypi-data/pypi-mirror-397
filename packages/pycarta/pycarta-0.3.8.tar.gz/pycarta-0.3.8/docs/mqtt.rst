.. _mqtt:

MQTT Messaging
==============

The ``pycarta.mqtt`` module provides comprehensive MQTT messaging capabilities with support for both synchronous and asynchronous operations. It offers decorator-based publishing and subscribing with automatic message formatting, TLS/SSL support, and Quality of Service (QoS) management.

.. contents::
   :local:
   :depth: 2

Overview
--------

MQTT (Message Queuing Telemetry Transport) is a lightweight messaging protocol designed for IoT and real-time applications. The pycarta MQTT module provides:

- **Decorator-based API**: Simple ``@publish`` and ``@subscribe`` decorators
- **Dual Client Support**: Both synchronous (paho-mqtt) and asynchronous (aiomqtt) clients
- **TLS/SSL Security**: Secure connections with credential management
- **QoS Support**: Quality of Service levels for reliable messaging
- **Automatic Formatting**: JSON serialization and message handling
- **Error Handling**: Retry logic and timeout management

Getting Started
---------------

Basic Publishing
^^^^^^^^^^^^^^^^

Use the ``@publish`` decorator to automatically publish function results:

.. code:: python

    from pycarta.mqtt import publish

    @publish("sensors/temperature")
    def read_temperature():
        """Read temperature from sensor and publish to MQTT."""
        # Your sensor reading logic here
        temperature = 23.5
        return {
            "temperature": temperature,
            "unit": "celsius",
            "timestamp": "2024-01-01T12:00:00Z",
            "sensor_id": "temp_001"
        }

    # Call the function - result is automatically published
    result = read_temperature()
    print(f"Published: {result}")

Basic Subscribing
^^^^^^^^^^^^^^^^^

Use the ``@subscribe`` decorator to handle incoming messages:

.. code:: python

    from pycarta.mqtt import subscribe

    @subscribe("alerts/system")
    def handle_system_alert(message):
        """Handle system alerts from MQTT."""
        print(f"System Alert: {message}")
        
        # Process the alert
        if message.get("level") == "critical":
            # Handle critical alerts
            send_notification(message)
        elif message.get("level") == "warning":
            # Log warnings
            log_warning(message)

    def send_notification(alert):
        # Your notification logic
        pass

    def log_warning(warning):
        # Your logging logic
        pass

Publishing
----------

Decorator-Based Publishing
^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``@publish`` decorator automatically publishes function return values:

.. code:: python

    from pycarta.mqtt import publish
    import datetime

    @publish("data/metrics")
    def collect_metrics():
        """Collect and publish system metrics."""
        return {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_usage": 23.1,
            "timestamp": datetime.datetime.now().isoformat()
        }

    @publish("events/user_action")
    def log_user_action(user_id: str, action: str):
        """Log user actions to MQTT."""
        return {
            "user_id": user_id,
            "action": action,
            "timestamp": datetime.datetime.now().isoformat()
        }

    # Usage
    collect_metrics()  # Publishes metrics to "data/metrics"
    log_user_action("user123", "login")  # Publishes to "events/user_action"

Manual Publishing
^^^^^^^^^^^^^^^^^

For more control, use the Publisher class directly:

.. code:: python

    from pycarta.mqtt import Publisher

    publisher = Publisher()

    # Publish a single message
    publisher.publish("sensors/humidity", {"humidity": 65.3, "location": "room1"})

    # Publish multiple messages
    messages = [
        ("sensors/temp1", {"temperature": 22.1}),
        ("sensors/temp2", {"temperature": 23.8}),
        ("sensors/temp3", {"temperature": 21.9})
    ]

    for topic, payload in messages:
        publisher.publish(topic, payload)

    # Clean up
    publisher.disconnect()

Publishing with QoS
^^^^^^^^^^^^^^^^^^^

Control message delivery reliability with Quality of Service levels:

.. code:: python

    from pycarta.mqtt import publish, Publisher

    # Using decorator with QoS
    @publish("critical/alerts", qos=2)  # Exactly once delivery
    def send_critical_alert():
        return {"alert": "System failure detected", "severity": "critical"}

    # Using Publisher with QoS
    publisher = Publisher()
    
    # QoS 0: At most once (fire and forget)
    publisher.publish("logs/info", {"message": "System started"}, qos=0)
    
    # QoS 1: At least once (acknowledged delivery)
    publisher.publish("data/important", {"value": 42}, qos=1)
    
    # QoS 2: Exactly once (guaranteed delivery)
    publisher.publish("commands/execute", {"command": "shutdown"}, qos=2)

Subscribing
-----------

Decorator-Based Subscribing
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``@subscribe`` decorator automatically handles incoming messages:

.. code:: python

    from pycarta.mqtt import subscribe

    @subscribe("sensors/+/temperature")  # Wildcard subscription
    def handle_temperature(message):
        """Handle temperature readings from any sensor."""
        sensor_id = message.get("sensor_id")
        temperature = message.get("temperature")
        print(f"Sensor {sensor_id}: {temperature}°C")

    @subscribe("alerts/#")  # Multi-level wildcard
    def handle_all_alerts(message):
        """Handle all alert messages."""
        alert_type = message.get("type")
        severity = message.get("severity", "info")
        print(f"Alert [{severity}]: {alert_type}")

    # Multiple subscriptions for one function
    @subscribe(["commands/restart", "commands/shutdown"])
    def handle_commands(message):
        """Handle system commands."""
        command = message.get("command")
        if command == "restart":
            restart_system()
        elif command == "shutdown":
            shutdown_system()

Manual Subscribing
^^^^^^^^^^^^^^^^^^

Use the Subscriber class for more control:

.. code:: python

    from pycarta.mqtt import Subscriber

    def message_handler(topic, payload):
        """Custom message handler."""
        print(f"Received on {topic}: {payload}")

    subscriber = Subscriber()
    
    # Subscribe to single topic
    subscriber.subscribe("data/stream", message_handler)
    
    # Subscribe to multiple topics
    topics = [
        ("sensors/temperature", 0),  # (topic, qos)
        ("sensors/humidity", 1),
        ("alerts/system", 2)
    ]
    subscriber.subscribe_multiple(topics, message_handler)
    
    # Start listening (blocking)
    subscriber.loop_forever()

Topic Patterns
^^^^^^^^^^^^^^

MQTT supports powerful topic patterns for flexible subscriptions:

.. code:: python

    from pycarta.mqtt import subscribe

    # Single-level wildcard (+)
    @subscribe("sensors/+/data")
    def handle_sensor_data(message):
        # Matches: sensors/temp/data, sensors/humidity/data, etc.
        pass

    # Multi-level wildcard (#)
    @subscribe("building1/floor2/#")
    def handle_floor2_data(message):
        # Matches: building1/floor2/room1/temp, building1/floor2/room2/humidity/sensor1, etc.
        pass

    # Exact topic
    @subscribe("system/status")
    def handle_system_status(message):
        # Matches only: system/status
        pass

    # Multiple patterns
    @subscribe(["sensors/+/temperature", "sensors/+/humidity"])
    def handle_environmental_data(message):
        # Matches temperature and humidity from any sensor
        pass

Asynchronous MQTT
-----------------

For high-performance applications, use the async MQTT support:

Async Publishing
^^^^^^^^^^^^^^^^

.. code:: python

    import asyncio
    from pycarta.mqtt import AsyncPublisher

    async def async_publish_example():
        publisher = AsyncPublisher()
        
        # Connect to broker
        await publisher.connect()
        
        # Publish messages
        await publisher.publish("async/data", {"value": 123})
        await publisher.publish("async/status", {"status": "active"})
        
        # Disconnect
        await publisher.disconnect()

    # Run the async function
    asyncio.run(async_publish_example())

Async Subscribing
^^^^^^^^^^^^^^^^^

.. code:: python

    import asyncio
    from pycarta.mqtt import AsyncSubscriber

    async def message_handler(topic, payload):
        """Async message handler."""
        print(f"Async received on {topic}: {payload}")
        # Perform async operations
        await process_message(payload)

    async def process_message(payload):
        """Process message asynchronously."""
        # Simulate async processing
        await asyncio.sleep(0.1)
        print(f"Processed: {payload}")

    async def async_subscribe_example():
        subscriber = AsyncSubscriber()
        
        # Connect and subscribe
        await subscriber.connect()
        await subscriber.subscribe("async/commands", message_handler)
        
        # Listen for messages
        await subscriber.start_listening()

    asyncio.run(async_subscribe_example())

Async Decorators
^^^^^^^^^^^^^^^^

MQTT decorators recognize whether the callable is coroutine and, if so, creates
an async task:

.. code:: python

    from pycarta.mqtt import async_publish, async_subscribe
    import asyncio

    @publish("async/results")
    async def compute_result():
        """Async computation that publishes results."""
        # Simulate async computation
        await asyncio.sleep(1)
        return {"result": 42, "computation_time": 1.0}

    @subscribe("async/tasks")
    async def handle_task(message):
        """Handle async task messages."""
        task_id = message.get("task_id")
        # Process task asynchronously
        result = await process_task(task_id)
        return result

    async def process_task(task_id):
        """Process a task asynchronously."""
        await asyncio.sleep(0.5)
        return f"Task {task_id} completed"

Configuration
-------------

Connection Settings
^^^^^^^^^^^^^^^^^^^

Configure MQTT broker connection:

.. code:: python

    from pycarta.mqtt import Publisher, Subscriber

    # Custom broker configuration
    config = {
        "host": "mqtt.example.com",
        "port": 1883,
        "username": "mqtt_user",
        "password": "mqtt_pass",
        "client_id": "pycarta_client"
    }

    publisher = Publisher(**config)
    subscriber = Subscriber(**config)

TLS/SSL Configuration
^^^^^^^^^^^^^^^^^^^^^

Secure your MQTT connections:

.. code:: python

    from pycarta.mqtt import Publisher
    import ssl

    # TLS configuration
    tls_config = {
        "ca_certs": "/path/to/ca.pem",
        "certfile": "/path/to/client.crt", 
        "keyfile": "/path/to/client.key",
        "cert_reqs": ssl.CERT_REQUIRED,
        "tls_version": ssl.PROTOCOL_TLS_CLIENT
    }

    publisher = Publisher(
        host="secure-mqtt.example.com",
        port=8883,
        tls=tls_config
    )

AWS IoT Core Integration
^^^^^^^^^^^^^^^^^^^^^^^^

Configure for AWS IoT Core:

.. code:: python

    from pycarta.mqtt import Publisher

    # AWS IoT Core configuration
    aws_config = {
        "host": "your-endpoint.iot.region.amazonaws.com",
        "port": 8883,
        "tls": {
            "ca_certs": "/path/to/AmazonRootCA1.pem",
            "certfile": "/path/to/device.pem.crt",
            "keyfile": "/path/to/private.pem.key"
        }
    }

    publisher = Publisher(**aws_config)

QoS Validation
^^^^^^^^^^^^^^

The module automatically validates QoS compatibility with AWS IoT:

.. code:: python

    from pycarta.mqtt import publish

    # This will work with AWS IoT Core
    @publish("data/sensor", qos=0)  # QoS 0 supported
    def send_sensor_data():
        return {"temperature": 25.0}

    @publish("data/sensor", qos=1)  # QoS 1 supported
    def send_important_data():
        return {"critical_value": 100}

    # This will raise a warning for AWS IoT Core
    @publish("data/sensor", qos=2)  # QoS 2 not supported by AWS IoT
    def send_guaranteed_data():
        return {"value": 42}

Message Formatting
------------------

Automatic JSON Serialization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Messages are automatically serialized to JSON:

.. code:: python

    from pycarta.mqtt import publish
    import datetime

    @publish("data/complex")
    def send_complex_data():
        return {
            "timestamp": datetime.datetime.now(),
            "values": [1, 2, 3, 4, 5],
            "metadata": {
                "source": "sensor_array",
                "location": {"lat": 40.7128, "lon": -74.0060}
            }
        }

Custom Formatters
^^^^^^^^^^^^^^^^^

Implement custom message formatters:

.. code:: python

    from pycarta.mqtt import Publisher
    import json
    import pickle

    class CustomFormatter:
        def format(self, payload):
            """Custom formatter that uses pickle for complex objects."""
            return pickle.dumps(payload)
        
        def parse(self, message):
            """Parse pickled messages."""
            return pickle.loads(message)

    # Use custom formatter
    publisher = Publisher(formatter=CustomFormatter())

Error Handling
--------------

Connection Errors
^^^^^^^^^^^^^^^^^

Handle connection failures gracefully:

.. code:: python

    from pycarta.mqtt import Publisher, MQTTError

    publisher = Publisher()

    try:
        publisher.connect()
        publisher.publish("test/topic", {"message": "Hello"})
    except MQTTError as e:
        print(f"MQTT Error: {e}")
        # Implement retry logic
        retry_connection(publisher)
    except Exception as e:
        print(f"Unexpected error: {e}")

Retry Logic
^^^^^^^^^^^

Implement automatic retry for failed operations:

.. code:: python

    from pycarta.mqtt import publish
    import time

    @publish("data/retryable", retry_count=3, retry_delay=1.0)
    def send_with_retry():
        """Function with automatic retry on publish failure."""
        return {"data": "important_value"}

    def retry_connection(publisher, max_retries=5):
        """Custom retry logic for connections."""
        for attempt in range(max_retries):
            try:
                publisher.connect()
                return True
            except Exception as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        return False

Monitoring and Logging
----------------------

Message Logging
^^^^^^^^^^^^^^^

Enable logging for debugging and monitoring:

.. code:: python

    import logging
    from pycarta.mqtt import Publisher, Subscriber

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('pycarta.mqtt')

    @publish("monitored/topic")
    def monitored_function():
        logger.info("Publishing monitored data")
        return {"status": "active", "value": 42}

    @subscribe("monitored/responses")
    def handle_response(message):
        logger.info(f"Received response: {message}")

Connection Monitoring
^^^^^^^^^^^^^^^^^^^^^

Monitor connection status:

.. code:: python

    from pycarta.mqtt import Publisher

    class MonitoredPublisher(Publisher):
        def on_connect(self, client, userdata, flags, rc):
            """Called when connection is established."""
            print(f"Connected with result code {rc}")
            
        def on_disconnect(self, client, userdata, rc):
            """Called when connection is lost."""
            print(f"Disconnected with result code {rc}")
            
        def on_publish(self, client, userdata, mid):
            """Called when message is published."""
            print(f"Message {mid} published successfully")

    publisher = MonitoredPublisher()

Best Practices
--------------

Topic Design
^^^^^^^^^^^^

- **Use hierarchical topics**: Structure topics like ``company/department/device/metric``
- **Avoid deep nesting**: Keep topic levels reasonable (typically 4-6 levels max)
- **Use consistent naming**: Establish and follow naming conventions
- **Consider wildcards**: Design topics to work well with + and # wildcards

Performance
^^^^^^^^^^^

- **Use appropriate QoS**: Don't use QoS 2 unless absolutely necessary
- **Batch messages**: Send multiple related data points together
- **Use retained messages wisely**: Only for state information that should persist
- **Monitor message size**: Keep payloads reasonable (typically < 256KB)

Security
^^^^^^^^

- **Always use TLS in production**: Encrypt connections and credentials
- **Implement proper authentication**: Use client certificates or username/password
- **Limit topic permissions**: Restrict publish/subscribe access as needed
- **Validate message content**: Sanitize and validate incoming data

Reliability
^^^^^^^^^^^

- **Handle disconnections**: Implement reconnection logic
- **Use persistent sessions**: For QoS > 0 when reliability is critical
- **Monitor connection health**: Implement heartbeat or keep-alive mechanisms
- **Log important events**: Track message delivery and connection status

Example: IoT Data Pipeline
--------------------------

Here's a complete example showing an IoT data collection and processing pipeline:

.. code:: python

    import asyncio
    import json
    import logging
    from datetime import datetime
    from typing import Dict, Any
    from pycarta.mqtt import publish, subscribe, AsyncPublisher
    import random

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Simulated sensor data collection
    @publish("sensors/temperature", qos=1)
    def read_temperature_sensor(sensor_id: str):
        """Read temperature from sensor and publish."""
        temperature = round(random.uniform(18.0, 30.0), 2)
        return {
            "sensor_id": sensor_id,
            "temperature": temperature,
            "unit": "celsius",
            "timestamp": datetime.now().isoformat(),
            "location": "building_1"
        }

    @publish("sensors/humidity", qos=1)
    def read_humidity_sensor(sensor_id: str):
        """Read humidity from sensor and publish."""
        humidity = round(random.uniform(30.0, 80.0), 2)
        return {
            "sensor_id": sensor_id,
            "humidity": humidity,
            "unit": "percent",
            "timestamp": datetime.now().isoformat(),
            "location": "building_1"
        }

    # Data processing subscribers
    @subscribe("sensors/+/temperature")
    def process_temperature(message: Dict[str, Any]):
        """Process temperature readings."""
        sensor_id = message.get("sensor_id")
        temperature = message.get("temperature")
        
        logger.info(f"Processing temperature from {sensor_id}: {temperature}°C")
        
        # Check for alerts
        if temperature > 28.0:
            send_temperature_alert(sensor_id, temperature)
        
        # Store in database (simulated)
        store_sensor_data("temperature", message)

    @subscribe("sensors/+/humidity")
    def process_humidity(message: Dict[str, Any]):
        """Process humidity readings."""
        sensor_id = message.get("sensor_id")
        humidity = message.get("humidity")
        
        logger.info(f"Processing humidity from {sensor_id}: {humidity}%")
        
        # Check for alerts
        if humidity > 70.0:
            send_humidity_alert(sensor_id, humidity)
        
        # Store in database (simulated)
        store_sensor_data("humidity", message)

    @publish("alerts/temperature", qos=2)
    def send_temperature_alert(sensor_id: str, temperature: float):
        """Send temperature alert."""
        return {
            "alert_type": "temperature_high",
            "sensor_id": sensor_id,
            "temperature": temperature,
            "threshold": 28.0,
            "severity": "warning",
            "timestamp": datetime.now().isoformat()
        }

    @publish("alerts/humidity", qos=2)
    def send_humidity_alert(sensor_id: str, humidity: float):
        """Send humidity alert."""
        return {
            "alert_type": "humidity_high",
            "sensor_id": sensor_id,
            "humidity": humidity,
            "threshold": 70.0,
            "severity": "warning",
            "timestamp": datetime.now().isoformat()
        }

    @subscribe("alerts/#")
    def handle_alerts(message: Dict[str, Any]):
        """Handle all alert messages."""
        alert_type = message.get("alert_type")
        severity = message.get("severity")
        sensor_id = message.get("sensor_id")
        
        logger.warning(f"ALERT [{severity}]: {alert_type} from {sensor_id}")
        
        # Send to notification system (simulated)
        send_notification(message)

    def store_sensor_data(data_type: str, data: Dict[str, Any]):
        """Simulate storing sensor data in database."""
        # In production, this would save to a real database
        logger.info(f"Stored {data_type} data: {data['sensor_id']} = {list(data.values())[1]}")

    def send_notification(alert: Dict[str, Any]):
        """Simulate sending notification."""
        # In production, this would send email, SMS, or push notification
        logger.info(f"Notification sent for alert: {alert['alert_type']}")

    # Async data aggregation
    async def data_aggregator():
        """Aggregate sensor data and publish summaries."""
        publisher = AsyncPublisher()
        await publisher.connect()
        
        while True:
            # Simulate data aggregation
            summary = {
                "timestamp": datetime.now().isoformat(),
                "building": "building_1",
                "sensor_count": 10,
                "avg_temperature": round(random.uniform(20.0, 25.0), 2),
                "avg_humidity": round(random.uniform(40.0, 60.0), 2),
                "alert_count": random.randint(0, 3)
            }
            
            await publisher.publish("summaries/hourly", summary)
            logger.info(f"Published hourly summary: {summary}")
            
            # Wait 5 seconds (in production, this might be hourly)
            await asyncio.sleep(5)

    async def sensor_simulator():
        """Simulate multiple sensors sending data."""
        sensor_ids = ["temp_001", "temp_002", "hum_001", "hum_002"]
        
        while True:
            for sensor_id in sensor_ids:
                if "temp" in sensor_id:
                    read_temperature_sensor(sensor_id)
                else:
                    read_humidity_sensor(sensor_id)
            
            # Send data every 2 seconds
            await asyncio.sleep(2)

    async def main():
        """Main application loop."""
        logger.info("Starting IoT data pipeline...")
        
        # Start data aggregator and sensor simulator
        await asyncio.gather(
            data_aggregator(),
            sensor_simulator()
        )

    if __name__ == "__main__":
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("Shutting down IoT data pipeline...")

This example demonstrates:

- **Multiple sensor types** with different topics
- **Automatic data processing** using subscribers
- **Alert generation** based on thresholds
- **Quality of Service** levels for different message types
- **Async operations** for high-performance aggregation
- **Proper logging** and error handling
- **Real-world patterns** for IoT applications

The pipeline processes sensor data in real-time, generates alerts when thresholds are exceeded, and provides aggregated summaries for monitoring and analysis.