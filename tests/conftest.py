import pytest
from unittest.mock import AsyncMock, patch

import sys
import os
from pathlib import Path

pytest_plugins = ["pytest_asyncio"]


# Определяем местоположение корневой директории проекта
project_root = Path(__file__).parent.parent
# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, str(project_root))

# Если ваш код находится в поддиректории (например, src/)
# Добавьте также путь к этой директории
if os.path.exists(project_root / "src"):
    sys.path.insert(0, str(project_root / "src"))

# Настройка для правильного запуска асинхронных тестов
def pytest_configure(config):
    pytest_plugins = getattr(config, "pytest_plugins", [])
    pytest_plugins = pytest_plugins + ["pytest_asyncio.plugin"]
    config.pytest_plugins = pytest_plugins
    
    

