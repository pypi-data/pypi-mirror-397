from zoneramaapi.zeep.common import ServiceProxy, AsyncServiceProxy


class BaseMixin:
    _api_service: ServiceProxy
    _data_service: ServiceProxy


class AsyncBaseMixin:
    _api_service: AsyncServiceProxy
    _data_service: AsyncServiceProxy
