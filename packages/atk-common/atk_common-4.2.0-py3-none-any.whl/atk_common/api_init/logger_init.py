from typing import Callable, Any, Optional
from http import HTTPStatus
from atk_common.enums import *
from atk_common.interfaces import *
from atk_common.classes import *
from atk_common.utils import *

# GetLogLevelFn = Callable[
#     [BoLogger, IEnvHandler, IErrorHandler, str],
#     dict[str, Any]
# ]

# UpdateLogLevelFn = Callable[
#     [BoLogger, IEnvHandler, IErrorHandler, Any],
#     dict[str, Any]
# ]

_bo_logger: BoLogger | None = None
_image_name_key: str | None = None
# _get_log_level: GetLogLevelFn | None = None
# _update_log_level: UpdateLogLevelFn | None = None

def create_bo_logger(env_handler: IEnvHandler, log_level: LogLevel, image_name_key: str, image_version_key: str):
    global _bo_logger
    global _image_name_key
    _image_name_key = image_name_key
    # log_level = LogLevel.INFO  # Ideally get from config/db
    _bo_logger = BoLogger(
        log_level, 
        env_handler.get_env_value(image_name_key), 
        env_handler.get_env_value(image_version_key))
    _bo_logger.info(f"Log level set to default {LogLevel.INFO.name}")

def get_bo_logger():
    global _bo_logger
    if _bo_logger is None:
        raise ValueError("BoLogger not initialized. Call create_bo_logger first.")
    return _bo_logger

# def set_log_level(env_handler: IEnvHandler, error_handler: IErrorHandler):
#     global _bo_logger
#     global _get_log_level
#     global _image_name_key

#     if _bo_logger is None:
#         raise ValueError("BoLogger not initialized. Call create_bo_logger first.")

#     if _image_name_key is None:
#         raise ValueError("_image_name_key not initialized. Call create_bo_logger first.")

#     if _get_log_level is None:
#         raise RuntimeError("get_log_level callback not registered. "
#                            "Pass it to create_bo_logger.")

#     component_name = parse_component_name(env_handler.get_env_value(_image_name_key))
#     get_log_level_resp = _get_log_level(_bo_logger, env_handler, error_handler, component_name)
#     if is_response_ok(get_log_level_resp):
#         log_level = get_log_level_resp.get('responseMsg').get('logLevel')
#         if log_level is not None:
#             ll = LogLevel(log_level)
#             _bo_logger.set_level(ll)
#             _bo_logger.info(f"Log level set to {ll.name}")
#         else:
#             ll = _bo_logger.get_level()
#             _bo_logger.info(f"Log level is None, using default {ll.name}.")

def create_log_level_response(log_level: LogLevel):
    response_msg = {
        'logLevel': log_level.name
    }
    return create_response(ResponseStatusType.OK, HTTPStatus.OK, response_msg)

def set_log_level(http_response_handler: IHttpResponseHandler, request):
    global _bo_logger

    try:
        if _bo_logger is None:
            raise ValueError("Logger not initialized. Call create_bo_logger first.")
        
        log_level = request.json.get('logLevel')
        if log_level is not None:
            ll = LogLevel(log_level)
            _bo_logger.set_level(ll)
            _bo_logger.info(f"Log level set to {ll.name}")
        else:
            ll = LogLevel.INFO
            _bo_logger.set_level(ll)
            _bo_logger.info(f"Log level set to default {ll.name}")
        return http_response_handler.http_response('set-log-level', create_log_level_response(ll))
    except Exception as error:
        _bo_logger.error(get_message(error))
        return http_response_handler.http_response(
            'update-and-set-log-level', 
            create_response(ResponseStatusType.INTERNAL, HTTPStatus.INTERNAL_SERVER_ERROR, get_message(error)))
