# uhooapi - Python Client for uHoo API

[![PyPI version](https://img.shields.io/pypi/v/uhooapi.svg)](https://pypi.org/project/uhooapi/)
[![Python versions](https://img.shields.io/pypi/pyversions/uhooapi.svg)](https://pypi.org/project/uhooapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A modern, asynchronous Python client for the uHoo air quality API. This library provides an intuitive, type-safe interface to access your uHoo device data, manage devices, and retrieve real-time air quality metrics with automatic token management and comprehensive error handling.

## ✨ Features

- **🚀 Async/Await Native**: Built on `aiohttp` for high-performance, non-blocking API calls
- **🔐 Automatic Token Management**: Handles authentication, token refresh, and retry logic automatically
- **📝 Full Type Annotations**: Complete type hints for better IDE support and reliability
- **🎯 Production Ready**: 100% test coverage with comprehensive unit and integration tests
- **🔄 Smart Error Handling**: Custom exceptions with automatic retry for 401/403 errors
- **📊 Complete Sensor Coverage**: Access to all uHoo metrics (temperature, humidity, CO₂, PM2.5, virus index, etc.)
- **⚡ Efficient Data Processing**: Automatic averaging and rounding of sensor readings

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install uhooapi
```