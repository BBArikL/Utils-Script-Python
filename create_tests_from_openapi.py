from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Optional, Type


@dataclass(kw_only=True)
class ContentType:
    content_type: str
    content_schema: dict[str, str]


@dataclass(kw_only=True)
class Response:
    response_code: int
    description: str
    content: list[ContentType] = field(default_factory=dict)

    def __post_init__(self):
        if self.content is not None:
            self.content: dict[str, dict[str, Any]]
            self.content: list[ContentType] = [
                ContentType(content_type=content_type, content_schema=content_schema)
                for content_type, content_schema in self.content.items()
            ]


@dataclass(kw_only=True)
class RequestBody:
    content: ContentType
    required: bool

    def __post_init__(self):
        self.content: dict[str, dict[str, Any]]
        self.content: list[ContentType] = [
            ContentType(content_type=content_type, content_schema=content_schema)
            for content_type, content_schema in self.content.items()
        ]


@dataclass(kw_only=True)
class BasePropertySchema:
    title: str
    type: str


@dataclass(kw_only=True)
class Parameter:
    required: bool
    schema: BasePropertySchema
    name: str
    _in: str
    description: str = ""


@dataclass(kw_only=True)
class HTTPMethod:
    method: str
    summary: str
    operationId: str
    responses: list[Response]
    description: str = ""
    tags: list[str] = field(default_factory=list)
    security: list[dict[str, list]] = field(default_factory=list)
    requestBody: Optional[RequestBody] = None
    parameters: Optional[list[Parameter]] = None

    def __post_init__(self):
        self.responses: dict[str, dict[str, str]]
        self.responses: list[Response] = [
            Response(response_code=int(response_code), **response_info)
            for response_code, response_info in self.responses.items()
        ]

        if self.requestBody is not None:
            self.requestBody: dict[str, dict[str, str]]
            self.requestBody: RequestBody = RequestBody(**self.requestBody)

        if self.parameters is not None:
            self.parameters: list[dict[str, str]]
            parameters_in: list[str] = [param.pop("in") for param in self.parameters]
            self.responses: list[Parameter] = [
                Parameter(**param, _in=param_in)
                for param, param_in in zip(self.parameters, parameters_in)
            ]


@dataclass(kw_only=True)
class UrlPath:
    path: str
    methods: list[HTTPMethod]

    def __post_init__(self):
        self.methods: dict[str, dict[str, Any]]
        self.methods: list[HTTPMethod] = [
            HTTPMethod(method=method, **method_info)
            for method, method_info in self.methods.items()
        ]


@dataclass(kw_only=True)
class APIPaths:
    paths: list[UrlPath]


@dataclass(kw_only=True)
class Tag:
    name: str
    description: str


@dataclass(kw_only=True)
class View:
    ref: Type[ViewEnabledProperty]


@dataclass(kw_only=True)
class ViewEnabledProperty:
    title: str = ""
    type: str = ""
    default: str | int | bool = ""
    format: str = ""
    description: str = ""
    # enum: list[str] = field(default_factory=list)
    allOf: list[View] | None = None
    anyOf: list[View] | None = None
    view: View | None = None
    items: list[View] | None = None
    pattern: str = ""
    writeOnly: bool = False

    def __post_init__(self):
        ...


@dataclass(kw_only=True)
class ModelSchema(BasePropertySchema):
    description: str = ""
    required: list[str] = field(default_factory=list)
    properties: list[ViewEnabledProperty] = field(default_factory=dict)
    enum: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.properties: dict[str, dict[str, Any]]
        ref_list = [
            properties.pop("$ref") if "$ref" in properties else None
            for properties in self.properties.values()
        ]
        self.properties: list[ViewEnabledProperty] = [
            ViewEnabledProperty(view=ref, **val)
            for val, ref in zip(self.properties.values(), ref_list)
        ]  # noqa: view is set in the ViewEnabledProperty's post init


@dataclass()
class Scope:
    ...


@dataclass(kw_only=True)
class Flow:
    flow_type: str
    scopes: list[Scope]
    tokenUrl: str = ""


@dataclass(kw_only=True)
class SecurityScheme:
    title: str
    type: str
    flows: list[Flow]

    def __post_init__(self):
        self.flows: dict[str, dict[str, Any]]
        self.flows: list[Flow] = [
            Flow(flow_type=key, **val) for key, val in self.flows.items()
        ]


@dataclass(kw_only=True)
class Components:
    schemas: list[ModelSchema]
    securitySchemes: dict[str, str]

    def __post_init__(self):
        self.schemas: dict[str, dict[str, Any]]
        self.schemas: list[ModelSchema] = [
            ModelSchema(**val) for val in self.schemas.values()
        ]

        self.securitySchemes: dict[str, dict[str, Any]]
        self.securitySchemes: list[SecurityScheme] = [
            SecurityScheme(title=key, **val)
            for key, val in self.securitySchemes.items()
        ]


@dataclass(kw_only=True)
class OpenApiSchemainfo:
    title: str
    description: str
    version: str


@dataclass(kw_only=True)
class OpenApiSchema:
    openapi: str
    info: OpenApiSchemainfo
    paths: list[UrlPath]
    components: Components
    tags: list[Tag]

    def __post_init__(self):
        self.info: dict[str, str]
        self.info = OpenApiSchemainfo(**self.info)

        self.paths: dict[str, dict[str, Any]]
        self.temp_paths = []
        for uri_path, path_info in self.paths.items():
            # Methods will be defined in UrlPath's post init
            url_path = UrlPath(path=uri_path, methods=path_info)  # noqa
            self.temp_paths.append(url_path)
        self.paths: list[UrlPath]

        self.tags: list[dict[str, str]]
        self.tags = [Tag(**tag) for tag in self.tags]
        self.components: dict[str, dict[str, Any]]
        self.components: Components = Components(**self.components)


if __name__ == "__main__":
    openapi_schema: dict[str, Any]
    with open("openapi.json", "rt") as f:
        openapi_schema = json.load(f)

    global_schema = OpenApiSchema(
        **openapi_schema
    )

    for path in global_schema.paths:
        for meth in path.methods:

            path_params = {}

            base = f"def test_{meth.operationId}(client: TestClient"

            for name, val_type in path_params.items():
                base += f", {name}: {val_type}"

            base += "):\n"
            for resp in meth.responses:
                base += f"  resp: Response = client.{meth.method}({path.path}"

                if path_params != {}:
                    base += ", params={}"
