#!/usr/bin/env python3
"""
Teste simples para verificar se o Celery está funcionando.
"""

import sys
import os

# Adicionar o diretório do projeto ao path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print(f"Python path: {sys.path}")
print(f"Current dir: {os.getcwd()}")

try:
    from app.config import settings
    print("Settings imported successfully")
    print(f"Redis URL: {settings.REDIS_URL}")
    print(f"Celery broker: {settings.CELERY_BROKER_URL}")
except Exception as e:
    print(f"Error importing settings: {e}")

try:
    from app.core.celery_app import celery_app
    print("Celery app imported successfully")
    print(f"Celery broker: {celery_app.conf.broker_url}")
except Exception as e:
    print(f"Error importing celery_app: {e}")

try:
    from app.tasks.inmetro_tasks import health_check_task
    print("Tasks imported successfully")
except Exception as e:
    print(f"Error importing tasks: {e}")