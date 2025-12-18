from lqs.interface.core import StudioInterface
from lqs.client.common import RESTInterface
import lqs.interface.core.models as models


class Studio(StudioInterface, RESTInterface):
    service: str = "lqs"

    def __init__(self, app):
        super().__init__(app=app)

    def _command_call(self, **params):
        return self._create_resource(
            "studio/commandCalls", params, models.CommandCallDataResponse
        )
