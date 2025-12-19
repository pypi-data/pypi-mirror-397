from pydantic import BaseModel, Field, model_validator
from typing import Annotated, Literal, Self
from nexo.enums.system import SystemRole
from nexo.schemas.error.enums import ErrorCode
from nexo.types.string import OptStr
from maleo.identity.enums.user import IdentifierType


class AuthenticationV1Parameters(BaseModel):
    system_role: Annotated[
        Literal[SystemRole.ADMINISTRATOR, SystemRole.USER],
        Field(..., description="User's system role"),
    ]
    organization_key: Annotated[
        OptStr, Field(None, description="Organization's Key", max_length=255)
    ] = None
    identifier_type: Annotated[
        Literal[IdentifierType.EMAIL, IdentifierType.USERNAME],
        Field(..., description="Identifier's Type"),
    ]
    identifier_value: Annotated[str, Field(..., description="Identifier's Value")]
    password: Annotated[str, Field(..., description="Password")]

    @model_validator(mode="after")
    def validate_system_role_and_organization_key(self) -> Self:
        if self.system_role is SystemRole.ADMINISTRATOR:
            if self.organization_key is not None:
                raise ValueError(
                    ErrorCode.BAD_REQUEST,
                    "Organization Key must be None for Administrator System Role",
                )
        elif self.system_role is SystemRole.USER:
            if self.organization_key is None:
                raise ValueError(
                    ErrorCode.BAD_REQUEST,
                    "Organization Key can not be None for User System Role",
                )
        return self


class AuthenticationTokenV1Schema(BaseModel):
    token: Annotated[str, Field(..., description="Token String")]


class AuthenticationSchema(BaseModel):
    access_token: Annotated[str, Field(..., description="Access Token")]
    token_type: Annotated[
        Literal["Bearer"], Field("Bearer", description="Token's type")
    ] = "Bearer"
    expires_in: Annotated[
        int, Field(..., description="Expires In", ge=60, multiple_of=60)
    ]
