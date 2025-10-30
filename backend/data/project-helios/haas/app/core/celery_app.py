"""
Configuração do Celery para processamento assíncrono.
Usado para validações INMETRO em background com escalabilidade.
"""

import os
from celery import Celery
from app.config import settings

# Configuração do Celery
broker_url = settings.CELERY_BROKER_URL
if settings.REDIS_PASSWORD:
    # Adicionar senha ao URL do Redis se configurada
    broker_url = broker_url.replace("redis://", f"redis://:{settings.REDIS_PASSWORD}@")

result_backend_url = settings.CELERY_RESULT_BACKEND
if settings.REDIS_PASSWORD:
    result_backend_url = result_backend_url.replace("redis://", f"redis://:{settings.REDIS_PASSWORD}@")

celery_app = Celery(
    "helios_tasks",
    broker=broker_url,
    backend=result_backend_url,
    include=["app.tasks.inmetro_tasks"]
)

# Configurações do Celery
celery_app.conf.update(
    # Timezone
    timezone=settings.TIMEZONE,

    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Task routing
    task_routes={
        "app.tasks.inmetro_tasks.validate_equipment_task": {"queue": "inmetro"},
        "app.tasks.inmetro_tasks.validate_batch_task": {"queue": "inmetro"},
    },

    # Worker settings
    worker_prefetch_multiplier=1,  # Processa uma task por vez
    task_acks_late=True,  # Confirma após processamento
    worker_disable_rate_limits=False,

    # Result backend settings
    result_expires=3600,  # 1 hora
    result_cache_max=10000,

    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Configuração para desenvolvimento
if settings.ENVIRONMENT == "development":
    celery_app.conf.update(
        worker_log_level="INFO",
        worker_pool="solo",  # Único worker para dev
    )

# Configuração para produção
else:
    celery_app.conf.update(
        worker_log_level="WARNING",
        worker_pool="prefork",
        worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,
    )


@celery_app.task(bind=True)
def debug_task(self):
    """Task de debug para testar configuração."""
    print(f"Request: {self.request!r}")


# Import tasks
try:
    from app.tasks import inmetro_tasks
except ImportError:
    pass