from abc import ABC, abstractmethod
import structlog
import asyncio
import traceback
from dattos_data_engine_common.webhook.models import BaseAsyncRequest
from dattos_data_engine_common.webhook.utils import send_webhook_notification

logger = structlog.stdlib.get_logger()


def execute_process_wrapper(
    cls_type: type["BaseWebhookService"], request, kwargs, result_queue
):
    try:
        # Cria instância real (no processo filho!)
        service = cls_type()
        # Roda o método execute de forma síncrona
        result_data = service.execute(request, **kwargs)
        result_queue.put({"success": True, "data": result_data})
    except Exception as exc:
        logger.error("Erro no processo filho", exc_info=True)
        result_queue.put(
            {
                "success": False,
                "error_message": str(exc),
                "trace": traceback.format_exc(),
            }
        )


class BaseWebhookService(ABC):
    async def process_async(self, request: BaseAsyncRequest):
        heartbeat_task = None
        try:
            if request.heartbeat_check_seconds_interval:
                # Inicia o heartbeat em paralelo
                heartbeat_task = asyncio.create_task(
                    self._heartbeat_loop(
                        request.webhook_uri,
                        request.webhook_token,
                        request.request_id,
                        interval=request.heartbeat_check_seconds_interval,
                    )
                )

            result_data = await asyncio.to_thread(self.execute, request)

            await self.send_success_notification(
                request.webhook_uri,
                request.webhook_token,
                request.request_id,
                data=result_data,
            )

        except Exception as e:
            logger.error("Erro durante o processamento principal.", exc_info=True)
            await self.send_failure_notification(
                request.webhook_uri,
                request.webhook_token,
                request.request_id,
                error_message=str(e),
            )
            raise
        finally:
            # Cancela o heartbeat se ainda estiver rodando
            if heartbeat_task:
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass

    async def send_success_notification(
        self, webhook_uri, webhook_token, request_id, data
    ):
        await send_webhook_notification(
            webhook_uri,
            webhook_token,
            request_id,
            success=True,
            heartbeat_check=False,
            data=data,
        )

    async def send_failure_notification(
        self, webhook_uri, webhook_token, request_id, error_message
    ):
        await send_webhook_notification(
            webhook_uri,
            webhook_token,
            request_id,
            success=False,
            heartbeat_check=False,
            data={"message": error_message},
        )

    async def send_check_notification(self, webhook_uri, webhook_token, request_id):
        return await send_webhook_notification(
            webhook_uri,
            webhook_token,
            request_id,
            success=True,
            heartbeat_check=True,
            data=None,
        )

    async def _heartbeat_loop(
        self, webhook_uri, webhook_token, request_id, interval=10
    ):
        """
        Loop que envia check_notification periodicamente durante o processamento.
        """
        try:
            while True:
                await asyncio.sleep(interval)
                await self.send_check_notification(
                    webhook_uri, webhook_token, request_id=request_id
                )
        except asyncio.CancelledError:
            # Pode ser usado para enviar um 'heartbeat stopped', se quiser
            pass

    @abstractmethod
    def execute(self, request: BaseAsyncRequest, **kwargs):
        pass
