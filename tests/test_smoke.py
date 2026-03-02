import socket

import pytest

from simulated_city.config import load_config
from simulated_city.mqtt import MqttConnector, MqttPublisher


def is_broker_available(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((host, port))
        s.close()
        return True
    except (socket.timeout, socket.error):
        return False


# Get default config to find broker host/port
default_config = load_config()
broker_available = is_broker_available(default_config.mqtt.host, default_config.mqtt.port)


@pytest.mark.skipif(not broker_available, reason=f"MQTT broker not available at {default_config.mqtt.host}:{default_config.mqtt.port}")
def test_mqtt_connection_and_publish():
    """Test primary broker connection and publish."""
    cfg = load_config()
    connector = MqttConnector(cfg.mqtt, client_id_suffix="test-smoke")
    try:
        connector.connect()
        assert connector.wait_for_connection(timeout=5), "Failed to connect to MQTT broker"

        publisher = MqttPublisher(connector)
        test_topic = "simulated-city/test/smoke"
        publisher.publish_json(test_topic, '{"test": "smoke"}', qos=1)

    finally:
        # Ensure disconnection even if asserts fail
        if connector.client and connector.client.is_connected():
            connector.disconnect()


def test_multi_broker_config_available():
    """Test that multi-broker configuration is accessible."""
    cfg = load_config()
    
    # Primary broker should be available
    assert cfg.mqtt.host is not None
    assert cfg.mqtt.port is not None
    
    # All brokers should be accessible via mqtt_configs
    assert isinstance(cfg.mqtt_configs, dict)
    assert len(cfg.mqtt_configs) > 0
    
    # Primary broker should be first in the list
    first_broker_name = next(iter(cfg.mqtt_configs.keys()))
    assert cfg.mqtt_configs[first_broker_name].host == cfg.mqtt.host
    assert cfg.mqtt_configs[first_broker_name].port == cfg.mqtt.port


@pytest.mark.skipif(not broker_available, reason=f"MQTT broker not available at {default_config.mqtt.host}:{default_config.mqtt.port}")
def test_mqtt_connection_via_broker_name():
    """Test connecting to a specific broker by name from mqtt_configs."""
    cfg = load_config()
    
    # Get primary broker name (first in configs)
    primary_broker_name = next(iter(cfg.mqtt_configs.keys()))
    broker_cfg = cfg.mqtt_configs[primary_broker_name]
    
    # Connect using the named broker config
    connector = MqttConnector(broker_cfg, client_id_suffix="test-named-broker")
    try:
        connector.connect()
        assert connector.wait_for_connection(timeout=5), f"Failed to connect to {primary_broker_name}"
    finally:
        if connector.client and connector.client.is_connected():
            connector.disconnect()
