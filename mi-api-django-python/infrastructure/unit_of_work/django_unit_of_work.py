import logging
from django.db import transaction
from domain.interfaces.unit_of_work import AbstractUnitOfWork
from infrastructure.repositories.compania_repository_impl import CompaniaRepository
from infrastructure.repositories.empleado_repository_impl import EmpleadoRepository

logger = logging.getLogger(__name__)

class DjangoUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.companias = CompaniaRepository()
        self.empleados = EmpleadoRepository()
        self._atomic = None

    def __enter__(self):
        logger.info("Iniciando transacción")
        self._atomic = transaction.atomic()
        self._atomic.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error(f"Error en transacción: {exc_val}. Ejecutando rollback.")
            self._atomic.__exit__(exc_type, exc_val, exc_tb)
            return False
        self._atomic.__exit__(None, None, None)
        return False

    def commit(self):
        logger.info("Confirmando transacción")

    def rollback(self):
        logger.warning("Rollback solicitado")
        transaction.set_rollback(True)
