from typing import Literal, Optional

from intugle.common.schema import SchemaBase


class DuckdbConfig(SchemaBase): 
    path: str
    type: Literal["csv", "parquet", "excel", "table", "delta"]


class DuckdbS3Config(SchemaBase):
    s3_access_key_id: Optional[str] = None
    s3_secret_access_key: Optional[str] = None
    s3_region: Optional[str] = None
    s3_endpoint: Optional[str] = None
    s3_session_token: Optional[str] = None
    s3_url_style: Optional[str] = None
