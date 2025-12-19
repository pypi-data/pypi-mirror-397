"""
Create an instance of an Api Service implementation to received published messages and send command requests.
"""

import logging

from autotrainer.api import ApiCommandRequest, ApiCommandRequestResponse, ApiCommandReqeustResult, ApiCommand, \
    ConfigurationResponse, StatusResponse
from autotrainer.api import create_api_service
from autotrainer.api import create_default_api_options
from autotrainer.api.command.status_response import ApiAppStatus, ApiTrainingMode


def _respond_to_command_request(request: ApiCommandRequest) -> ApiCommandRequestResponse:
    logger.debug("Received command request: %s", request.command)

    if request.command == ApiCommand.GET_CONFIGURATION:
        data = ConfigurationResponse("000000", "/home/ubuntu/Autotrainer", "/home/ubuntu/Documents/RawDataLocal",
                                     "/home/ubuntu/Autotrainer/animals", "/home/ubuntu/Documents/RawDataLocal/logs",
                                     "/home/ubuntu/Autotrainer/inference_model")
        return ApiCommandRequestResponse(result=ApiCommandReqeustResult.SUCCESS, data=data)
    elif request.command == ApiCommand.GET_STATUS:
        data = StatusResponse(app_status=ApiAppStatus.IDLE, training_mode=ApiTrainingMode.MANUAL, animal_id="123456")
        return ApiCommandRequestResponse(result=ApiCommandReqeustResult.SUCCESS, data=data)

    return ApiCommandRequestResponse(result=ApiCommandReqeustResult.SUCCESS, data={"seen": True})


def run_server():
    options = create_default_api_options()

    service = create_api_service(options)

    service.command_request_delegate = _respond_to_command_request

    service.start()

    input("Press enter to stop the service...\n")

    service.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s\t [%(name)s] %(message)s")
    logging.getLogger('autotrainer').setLevel(logging.DEBUG)
    logging.getLogger('tools').setLevel(logging.DEBUG)

    logger = logging.getLogger(__name__)

    run_server()
