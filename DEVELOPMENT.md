# SoilGuard Portal: Development Guide

## Local Development Setup

```bash
git clone https://github.com/fivepanelhat/SoilGuard-Portal.git
cd SoilGuard-Portal
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
```

## Running Tests

```bash
pytest tests/ -v
```

## Mocking MQTT in Development

Set `MQTT_MOCK=true` in `.env` to run without a live broker.
The mock publisher in `tests/mock_mqtt.py` simulates ESP32 soil sensor payloads.

## Land-Use Category Testing

Test with different NEMS-SQ land-use categories by changing `LAND_USE_CATEGORY` in `.env`.
Valid values: `dairy`, `drystock`, `cropping`, `horticulture`, `forestry`, `deer`.

## Linting and Formatting

```bash
black .
flake8 .
mypy .
```
