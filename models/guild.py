from sqlmodel import SQLModel, Field


class Guild(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    verification_channel: int = 0
    role_before: int = 0
    role_after: int = 0
    timeout: int = 300
    log_channel: int = 0
    white_list_active: bool = False
    on_create_channel: bool = False
    spoon_pot: int = 0
