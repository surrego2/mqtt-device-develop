from datetime import datetime
from pydantic import BaseSettings


class Settings(BaseSettings):
    SERIAL_PORT: str = "COM3"
    SERIAL_BAUDRATE: int = 115200

    MQTT_BROKER: str = "broker.hivemq.com"
    MQTT_PORT: int = 1883
