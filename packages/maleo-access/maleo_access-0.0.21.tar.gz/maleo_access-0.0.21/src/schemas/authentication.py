from pydantic import BaseModel, Field
from typing import Annotated
from nexo.types.string import OptStr
from maleo.identity.mixins.user import UsernameUserIdentifier, EmailUserIdentifier


UserIdentifier = UsernameUserIdentifier | EmailUserIdentifier


class RegularAuthenticationParameters(BaseModel):
    organization_key: Annotated[
        OptStr, Field(None, description="Organization's Key", max_length=255)
    ] = None
    identifier: Annotated[UserIdentifier, Field(..., description="User's Identifier")]
    password: Annotated[str, Field(..., description="User's Password")]


class RefreshAuthenticationParameters(BaseModel):
    refresh_token: Annotated[str, Field(..., description="Refresh Token")]


AuthenticationParameters = (
    RegularAuthenticationParameters | RefreshAuthenticationParameters
)
