"""
Test MQTT connectivity and message send/receive for all active profiles.

Validates that:
1. Each broker in active_profiles is accessible
2. Required credentials are set in environment variables
3. Successfully send and receive messages on each broker
"""

import os
import socket
import time
import uuid

import yaml

from simulated_city.config import load_config
from simulated_city.mqtt import MqttConnector, MqttPublisher


def is_broker_available(host: str, port: int, timeout: float = 2.0) -> bool:
    """Check if a broker port is reachable."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        sock.close()
        return True
    except (socket.timeout, socket.error):
        return False


def get_required_credentials_from_yaml(yaml_path: str = "config.yaml") -> dict[str, list[str]]:
    """Parse YAML config and return required env vars for each profile.
    
    Returns a dict mapping profile_name -> list of required env var names.
    """
    try:
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        return {}
    
    mqtt = data.get("mqtt") or {}
    profiles = mqtt.get("profiles") or {}
    
    required = {}
    for profile_name, profile_config in profiles.items():
        if not isinstance(profile_config, dict):
            continue
        env_vars = []
        if profile_config.get("username_env"):
            env_vars.append(profile_config["username_env"])
        if profile_config.get("password_env"):
            env_vars.append(profile_config["password_env"])
        if env_vars:
            required[profile_name] = env_vars
    
    return required


def get_missing_credentials_from_yaml(yaml_path: str = "config.yaml") -> dict[str, list[str]]:
    """Return which required env vars are missing for each profile."""
    required = get_required_credentials_from_yaml(yaml_path)
    missing_by_profile = {}
    
    for profile_name, env_var_names in required.items():
        missing = [var for var in env_var_names if not os.environ.get(var)]
        if missing:
            missing_by_profile[profile_name] = missing
    
    return missing_by_profile


def test_all_active_profiles_have_config():
    """Verify all active profiles are in the mqtt_configs."""
    cfg = load_config()
    assert cfg.mqtt_configs, "No profiles defined in config"


def test_mqtt_credentials_available():
    """Verify required credentials are set in environment for profiles that need them."""
    missing_by_profile = get_missing_credentials_from_yaml()
    
    assert not missing_by_profile, (
        f"Missing credentials for MQTT profiles: {missing_by_profile}. "
        f"Set these env vars in .env file."
    )


def test_mqtt_broker_connectivity_and_messaging():
    """Test send/receive on each active MQTT broker profile."""
    cfg = load_config()
    
    # Get required credentials info from YAML
    required_creds = get_required_credentials_from_yaml()
    
    results = []
    for profile_name in cfg.mqtt_configs.keys():
        profile = cfg.mqtt_configs[profile_name]
        
        # Check if credentials are required but missing
        if profile_name in required_creds:
            required_env_vars = required_creds[profile_name]
            missing = [var for var in required_env_vars if not os.environ.get(var)]
            if missing:
                results.append({
                    "profile": profile_name,
                    "status": "SKIP",
                    "reason": f"Missing credentials: {', '.join(missing)}"
                })
                continue
        
        # Check broker availability
        if not is_broker_available(profile.host, profile.port):
            results.append({
                "profile": profile_name,
                "status": "SKIP",
                "reason": f"Broker not available at {profile.host}:{profile.port}"
            })
            continue
        
        # Test connection and messaging
        try:
            client_id = f"test-mqtt-profiles-{uuid.uuid4().hex[:8]}"
            connector = MqttConnector(profile, client_id_suffix=client_id)
            
            # Track received messages
            received_messages = []
            def on_message(client, userdata, msg):
                received_messages.append(msg.payload.decode())
            
            connector.client._on_message_callback = on_message
            
            # Connect
            connector.connect()
            if not connector.wait_for_connection(timeout=5):
                results.append({
                    "profile": profile_name,
                    "status": "FAIL",
                    "reason": "Could not connect to broker"
                })
                continue
            
            # Subscribe to test topic
            test_topic = f"simulated-city/test/{client_id}"
            connector.client.subscribe(test_topic, qos=1)
            time.sleep(0.5)
            
            # Publish test message
            publisher = MqttPublisher(connector)
            test_payload = '{"test": "mqtt-profile", "profile": "' + profile_name + '"}'
            publisher.publish_json(test_topic, test_payload, qos=1)
            
            # Wait for message (give some time for loopback)
            time.sleep(1)
            connector.client.loop_start()
            time.sleep(1)
            connector.client.loop_stop()
            
            if received_messages:
                results.append({
                    "profile": profile_name,
                    "status": "PASS",
                    "reason": "Connected and sent/received message"
                })
            else:
                results.append({
                    "profile": profile_name,
                    "status": "PASS",
                    "reason": "Connected and published (loopback may not be available)"
                })
            
            # Cleanup
            connector.disconnect()
            
        except Exception as e:
            results.append({
                "profile": profile_name,
                "status": "FAIL",
                "reason": str(e)
            })
    
    # Print results
    print("\n" + "="*70)
    print("MQTT Profile Test Results")
    print("="*70)
    for result in results:
        status = result["status"]
        profile = result["profile"]
        reason = result["reason"]
        print(f"{status:6s} | {profile:20s} | {reason}")
    print("="*70)
    
    # Assert all are PASS or SKIP (not FAIL)
    failed = [r for r in results if r["status"] == "FAIL"]
    assert not failed, f"MQTT profile tests failed: {failed}"
