from abc import ABC, abstractmethod
from typing import Optional

import lqs.interface.core.models.studio as models


class StudioInterface(ABC):
    @abstractmethod
    def _command_call(self, **kwargs) -> models.CommandCallDataResponse:
        pass

    def command_call(
        self,
        action: str,
        kwargs: Optional[dict] = None,
    ):
        return self._command_call(
            action=action,
            kwargs=kwargs,
        )

    def _command_call_by_model(self, data: models.CommandCallCreateRequest):
        return self.command_call(**data.model_dump())
