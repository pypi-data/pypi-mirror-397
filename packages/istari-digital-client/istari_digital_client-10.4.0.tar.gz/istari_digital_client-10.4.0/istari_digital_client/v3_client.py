from typing import Union
import os
from pathlib import Path
from typing_extensions import override

from istari_digital_client.configuration import Configuration
from istari_digital_client.api_client import ApiClient
from istari_digital_client.storage.api.storage_api import StorageApi
from istari_digital_client.v3.api.v3_api import V3Api
from istari_digital_client.v3.models.resource_dto import ResourceDto
from istari_digital_client.v3.models.resource_type_dto import ResourceTypeDto
from istari_digital_client.v3.models.resource_create_dto import ResourceCreateDto
from istari_digital_client.v3.models.token_create_dto import TokenCreateDto
from istari_digital_client.v3.models.resource_revision_create_dto import ResourceRevisionCreateDto
from istari_digital_client.v3.models.resource_revision_dto import ResourceRevisionDto


PathLike = Union[str, os.PathLike, Path]

class V3Client(V3Api):
    def __init__(self, config: Configuration) -> None:
        self._api_client = ApiClient(config)
        self._storage_api = StorageApi(config=config, api_client=self._api_client)
        super().__init__(config=config, api_client=self._api_client)


    @override
    def create_resource(
        self,
        path: PathLike,
        resource_type: ResourceTypeDto,
        *,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> ResourceDto:
        file_revision = self._storage_api.create_revision(
            file_path=path,
            display_name=display_name,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
        )

        return super().create_resource(
            resource_create_dto=ResourceCreateDto(
                name=file_revision.name,
                extension=file_revision.extension,
                size=file_revision.size,
                mime=file_revision.mime,
                description=file_revision.description,
                version_name=file_revision.version_name,
                external_identifier=file_revision.external_identifier,
                display_name=file_revision.display_name,
                content_token=TokenCreateDto(
                    sha=file_revision.content_token.sha,
                    salt=file_revision.content_token.salt,
                ),
                properties_token=TokenCreateDto(
                    sha=file_revision.properties_token.sha,
                    salt=file_revision.properties_token.salt,
                ),
                resource_type=resource_type,
                upstream_remote_id=None,
            )
        )

    @override
    def create_resource_revision(
        self,
        resource_id: str,
        path: PathLike,
        *,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
    ) -> ResourceRevisionDto:
        file_revision = self._storage_api.create_revision(
            file_path=path,
            display_name=display_name,
            description=description,
            version_name=version_name,
            external_identifier=external_identifier,
        )

        return super().create_resource_revision(
            resource_id=resource_id,
            resource_revision_create_dto=ResourceRevisionCreateDto(
                name=file_revision.name,
                extension=file_revision.extension,
                size=file_revision.size,
                mime=file_revision.mime,
                description=file_revision.description,
                version_name=file_revision.version_name,
                external_identifier=file_revision.external_identifier,
                display_name=file_revision.display_name,
                content_token=TokenCreateDto(
                    sha=file_revision.content_token.sha,
                    salt=file_revision.content_token.salt,
                ),
                properties_token=TokenCreateDto(
                    sha=file_revision.properties_token.sha,
                    salt=file_revision.properties_token.salt,
                ),
            )
        )
