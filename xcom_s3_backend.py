import os
import uuid
import io
import pandas as pd

from typing import Any
from airflow.models.xcom import BaseXCom
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import logging


class S3XComBackend(BaseXCom):
    PREFIX = "xcom_s3"
    BUCKET_NAME = os.environ.get("S3_XCOM_BUCKET_NAME")
    S3_XCOM_CONN_NAME = os.environ.get("S3_XCOM_CONN_NAME")

    @staticmethod
    def _assert_s3_backend():
        if S3XComBackend.BUCKET_NAME is None:
            raise ValueError("Unknown bucket for S3 backend.")

    @staticmethod
    def serialize_value(
        value: Any,
        *,
        key: str | None = None,
        task_id: str | None = None,
        dag_id: str | None = None,
        run_id: str | None = None,
        map_index: int | None = None,
    ) -> Any:
        if isinstance(value, pd.DataFrame):
            S3XComBackend._assert_s3_backend()
            hook = S3Hook(S3XComBackend.S3_XCOM_CONN_NAME)
            key = f"{dag_id}/{run_id}/{task_id}.csv"
            logging.debug(f's3 key: {key}')

            with io.BytesIO() as buffer:                                
                buffer.write(
                    bytes(
                        value.to_csv(None, index=False),
                        encoding="utf-8"
                    )
                )               
                hook.load_bytes(
                    buffer.getvalue(),
                    key=key,
                    bucket_name=S3XComBackend.BUCKET_NAME,
                    replace=True
                )

            value = f"{S3XComBackend.PREFIX}://{S3XComBackend.BUCKET_NAME}/{key}"

        return BaseXCom.serialize_value(value)

    @staticmethod
    def deserialize_value(result) -> Any:
        result = BaseXCom.deserialize_value(result)

        if isinstance(result, str) and result.startswith(S3XComBackend.PREFIX):
            S3XComBackend._assert_s3_backend()
            hook = S3Hook()
            key = result.replace(f"{S3XComBackend.PREFIX}://{S3XComBackend.BUCKET_NAME}/", "")
            filename = hook.download_file(
                key=key,
                bucket_name=S3XComBackend.BUCKET_NAME,
                local_path="/tmp"
            )
            result = pd.read_csv(filename)

        return result
