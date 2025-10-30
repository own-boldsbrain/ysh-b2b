#!/usr/bin/env python3
"""
Script para iniciar o Celery worker para processamento INMETRO.
"""

import sys
import os

# Adicionar o diretório do projeto ao path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
haas_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)
sys.path.insert(0, haas_dir)

# Importar configurações primeiro
from app.config import settings

# Configurar celery
from app.core.celery_app import celery_app

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Start Celery worker')
    parser.add_argument('--loglevel', default='info', help='Log level')
    parser.add_argument('--concurrency', type=int, default=1, help='Worker concurrency')
    parser.add_argument('--pool', default='solo', help='Pool type')
    parser.add_argument('-Q', '--queues', default='inmetro', help='Queues to consume from')

    args = parser.parse_args()

    # Iniciar worker com argumentos
    celery_app.start([
        'worker',
        f'--loglevel={args.loglevel}',
        f'--concurrency={args.concurrency}',
        f'--pool={args.pool}',
        f'-Q={args.queues}'
    ])