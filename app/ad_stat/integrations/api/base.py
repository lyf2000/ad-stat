import csv
import io
import logging
import re
from contextlib import contextmanager
from copy import deepcopy
from functools import partial, wraps
from io import StringIO
from itertools import chain
from time import sleep
from typing import Any, Callable, Dict, Iterable, Optional, Type, TypeVar, Union

from ad_stat.integrations.api.errors import BaseAPIError, UnexpectedAPIError
from common.models import BaseModel
from common.utils import item_by_source
from requests import Response, Session
from requests.exceptions import JSONDecodeError
from rest_framework.status import HTTP_429_TOO_MANY_REQUESTS

# TODO mv to root
logger = logging.getLogger(__name__)


# region reponse parsers
class BaseResponseParser:
    def parse(self, data: Any) -> Any:
        return data


class CSVResponseParser(BaseResponseParser):
    def parse(self, data: str) -> list[dict]:
        return list(csv.DictReader(StringIO(data), skipinitialspace=True))


class SourceResponseParser(BaseResponseParser):
    def __init__(self, source: str) -> None:
        super().__init__()
        self.source = source  # Example: `response.accounts`

    def parse(self, data: dict) -> Union[dict, list]:
        return item_by_source(self.source, data)


class DumpDetailResponseParser(BaseResponseParser):
    def __init__(self, **specs: dict[str, str] | dict[str, tuple[str, type]]) -> None:
        super().__init__()
        self.specs = {field: (source[0] if isinstance(source, tuple) else source) for field, source in specs.items()}
        self.field_types = {field: source[1] for field, source in specs.items() if isinstance(source, tuple)}

    def parse(self, data: dict) -> dict:
        result = deepcopy(data) if type(data) is dict else dict()
        for field, source in self.specs.items():
            self._parse_item(result, field, source, data)
        return result

    def _parse_item(self, resulting: dict, field: str, source: str, data):
        if (obj := field.split(".")[0]) == field:
            value = item_by_source(source, data)
            if new_type := self.field_types.get(field):
                value = new_type(value)

            resulting.update({field: value})
        elif "[" in obj:  # list of obj items
            objs = re.findall(r"\[(.*)\]", obj)[0].replace("|", ".")
            obj = obj.split("[")[0]

            field_ = field.split(".")[1]
            data_ = item_by_source(objs, data)

            resulting.setdefault(obj, [])
            items = resulting[obj]
            if items:
                for item_data, item in zip(data_, items):
                    self._parse_item(item, field_, source, item_data)
            else:
                for item_data in data_:
                    new_item = {}
                    self._parse_item(new_item, field_, source, item_data)
                    items.append(new_item)
        else:  # obj
            field_ = field.split(".", 1)[1]
            resulting.setdefault(obj, {})
            item = resulting[obj]
            self._parse_item(item, field_, source, data)


# endregion

# region API Clients


class BaseAPIClient:
    _session: Optional[Any] = None

    @property
    def session(self) -> Any:
        if self._session is None:
            self._update_session()

        return self._session

    def _api_call(self, *args, **kwargs) -> Response:
        raise NotImplementedError

    def _get_session(self) -> Any:
        raise NotImplementedError

    def _update_session(self):
        self._session = self._get_session()


class BaseRequestsClient(BaseAPIClient):
    """
    Через requests
    """

    _headers: Dict = {}
    domain: str = ""

    @property
    def session(self) -> Session:
        return super().session

    @property
    def headers(self) -> Dict:
        return self._headers

    def _api_call(self, method: str, url: str, **method_kwargs) -> Response:
        return getattr(self.session, method)(f"{self.domain}{url}", **method_kwargs)

    def _get_session(self) -> Session:
        session = Session()
        session.headers.update(self.headers)

        return session

    def get(self, url: str) -> Response:
        return self._api_call("get", url)

    def post(self, url: str, data: dict | None = None) -> Response:
        return self._api_call("post", url, json=data or {})

    @contextmanager
    def _download_file(self, url: str):
        response = self.get(url)
        file_content = io.BytesIO()
        for chunk in response.iter_content(chunk_size=1024):
            file_content.write(chunk)
        file_content.seek(0)
        yield file_content


# endregion

ApiClass = TypeVar("ApiClass", bound=BaseAPIClient)


# TODO refactor
class BaseAdapterAPIClient:
    API_CLASS: ApiClass = None

    def __getattribute__(self, name: str) -> Any:
        if name != "API_CLASS" and name in super().__getattribute__("methods"):  # TODO fix
            strategy = getattr(self, f"_{self.selected_strategy}")
            result = partial(strategy, method=name)
            del self.selected_strategy
            return result

        return super().__getattribute__(name)

    @property
    def methods(self) -> tuple:
        decorated_methods = []
        for attr_name in dir(self.API_CLASS):
            attr_value = getattr(self.API_CLASS, attr_name)
            if callable(attr_value) and request in getattr(attr_value, "_marked", []):
                decorated_methods.append(attr_name)

        return tuple(decorated_methods)

    def all(self):
        self.selected_strategy = "all"
        return self

    def _all(self, method: str, *meth_args, **meth_kwargs):
        results = []
        for api in self._per_api():
            results = results + getattr(api, method)(*meth_args, **meth_kwargs)

        return results

    def _per_api(self) -> ApiClass:
        for init_data in self._per_api_init_data():
            yield self.API_CLASS(**init_data)

    def _per_api_init_data(self) -> Iterable[dict]:
        raise NotImplementedError


ResponseModel = TypeVar("ResponseModel", bound=BaseModel)
APIError = TypeVar("APIError", bound=BaseAPIError)


def request(
    response_model: Optional[ResponseModel] = None,
    response_parser: Optional[Type[BaseResponseParser]] = None,
    detail_response_parser: Optional[Type[BaseResponseParser]] = None,
    errors: tuple[Type[APIError]] | None = None,
) -> Callable:  # TODO: move response, parser to service
    def wrapper(func: Callable) -> Callable:
        func._marked = getattr(func, "_marked", [])
        func._marked.append(request)

        @wraps(func)
        def send_request(*args, **kwargs) -> ResponseModel | Any:  # TODO: fix hint
            content = None
            while not content:
                try:
                    resp: Response | Any = func(*args, **kwargs)

                    if type(resp) is Response:
                        if resp.status_code == HTTP_429_TOO_MANY_REQUESTS:
                            sleep(3)
                            continue
                        resp.raise_for_status()

                        try:
                            content: Any = resp.json()
                        except JSONDecodeError:
                            content: Any = resp.content.decode()

                    else:
                        content = resp
                except tuple(chain.from_iterable(err.except_ for err in (errors or []))) or tuple() as err_handled:
                    next(error for error in errors if type(err_handled) in error.except_).handle(
                        *args, exc=err_handled, func_=func, logger=logger, **kwargs
                    )
                except Exception as err:
                    UnexpectedAPIError.handle(*args, exc=err, func_=func, logger=logger, **kwargs)

            if response_parser:
                content = response_parser.parse(content)

            def get_content(content) -> dict:
                if detail_response_parser:
                    return detail_response_parser.parse(content)
                return content

            if not response_model:
                return content
            return (
                response_model(**get_content(content))
                if type(content) is dict
                or (type(content) is list and content and type(content[0]) in (int, float, str))
                else [response_model(**get_content(content_)) for content_ in content]
            )  # TODO: refact

        return send_request

    return wrapper
