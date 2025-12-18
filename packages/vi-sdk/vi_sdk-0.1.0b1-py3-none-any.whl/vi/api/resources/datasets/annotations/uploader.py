#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   uploader.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK annotations uploader module.
"""

from __future__ import annotations

import os
import time
from collections.abc import Sequence
from pathlib import Path

import msgspec
from rich import print as rprint
from rich.progress import BarColumn, TaskID, TimeElapsedColumn
from vi.api.resources.datasets.annotations import consts, responses
from vi.api.resources.datasets.annotations.links import (
    AnnotationImportSessionLinkParser,
)
from vi.api.resources.datasets.annotations.types import (
    AnnotationImportFailurePolicy,
    AnnotationImportFileSpec,
    AnnotationImportPatchCondition,
    AnnotationImportPatchStatus,
    AnnotationImportPayload,
    AnnotationImportSession,
    AnnotationImportSource,
    AnnotationImportSpec,
)
from vi.api.resources.datasets.utils.helper import calculate_crc32c
from vi.api.resources.managers import ResourceUploader
from vi.api.responses import ConditionStatus
from vi.api.types import ResourceMetadata
from vi.client.errors import ViInvalidParameterError
from vi.utils.graceful_exit import GracefulExit, graceful_exit
from vi.utils.progress import ViProgress

UPLOAD_SESSION_TIMEOUT_SECONDS = 55 * 60  # 55 minutes


class AnnotationUploader(ResourceUploader):
    """Uploader for annotations."""

    _link_parser: AnnotationImportSessionLinkParser | None = None

    def upload(
        self,
        dataset_id: str,
        paths: Path | str | Sequence[Path | str],
        upload_timeout: int = UPLOAD_SESSION_TIMEOUT_SECONDS,
        failure_policies: AnnotationImportFailurePolicy = AnnotationImportFailurePolicy(),
        source: AnnotationImportSource = AnnotationImportSource.UPLOADED_INDIVIDUAL_FILES,
        attributes: dict[str, str] | None = None,
        show_progress: bool = True,
    ) -> responses.AnnotationImportSession:
        """Upload an annotation file to the dataset."""
        annotation_file_paths = self._parse_annotation_paths(paths)

        with graceful_exit("Upload cancelled by user") as handler:
            if show_progress:
                with ViProgress(
                    "[progress.description]{task.description}",
                    BarColumn(),
                    "[progress.percentage]{task.percentage:>3.2f}%",
                    TimeElapsedColumn(),
                    transient=True,
                ) as progress:
                    task = progress.add_task(
                        "Initializing annotation import session...",
                        total=len(annotation_file_paths) + 1,
                    )

                    return self._execute_upload(
                        dataset_id,
                        annotation_file_paths,
                        upload_timeout,
                        failure_policies,
                        source,
                        attributes,
                        progress,
                        task,
                        handler,
                    )
            else:
                return self._execute_upload(
                    dataset_id,
                    annotation_file_paths,
                    upload_timeout,
                    failure_policies,
                    source,
                    attributes,
                    None,
                    None,
                    handler,
                )

    def _execute_upload(
        self,
        dataset_id: str,
        annotation_file_paths: list[str],
        upload_timeout: int,
        failure_policies: AnnotationImportFailurePolicy,
        source: AnnotationImportSource,
        attributes: dict[str, str] | None,
        progress: ViProgress | None,
        task: TaskID | None,
        handler: GracefulExit,
    ) -> responses.AnnotationImportSession:
        """Execute the upload process with optional progress tracking."""
        # Step 1: Create annotation import session
        session_response = self._create_annotation_import_session(
            dataset_id=dataset_id,
            upload_timeout=upload_timeout,
            failure_policies=failure_policies,
            source=source,
            attributes=attributes,
        )

        try:
            # Step 2: Add files to session
            files_response = self._add_files_to_session(
                dataset_id=dataset_id,
                annotation_import_session_id=session_response.annotation_import_session_id,
                annotation_file_paths=annotation_file_paths,
            )

            if not files_response.files:
                raise ValueError("No files added to the session")

            # Step 3: Upload files using signed URLs
            self._upload_files(
                annotation_file_paths=annotation_file_paths,
                files_response=files_response,
                progress=progress,
                task=task,
                handler=handler,
            )

            condition = responses.AnnotationImportSessionCondition(
                condition="FilesInserted",
                status=ConditionStatus.REACHED,
                last_transition_time=int(time.time() * 1000),
            )

        except KeyboardInterrupt:
            condition = responses.AnnotationImportSessionCondition(
                condition="FilesInserted",
                status=ConditionStatus.FAILED_REACH,
                last_transition_time=int(time.time() * 1000),
                reason="CancelledByUser",
            )

        except Exception as e:
            rprint(f"Error uploading files: {e}")
            condition = responses.AnnotationImportSessionCondition(
                condition="FilesInserted",
                status=ConditionStatus.FAILED_REACH,
                last_transition_time=int(time.time() * 1000),
                reason="UserUploadErrored",
            )

        return self._patch_annotation_import_session(
            dataset_id, session_response.annotation_import_session_id, condition
        )

    def _parse_annotation_paths(
        self, paths: Path | str | Sequence[Path | str]
    ) -> list[str]:
        """Parse annotation paths."""
        if isinstance(paths, (str, Path)):
            path_list = [paths]
        else:
            path_list = paths

        annotation_file_paths = []
        for path_item in path_list:
            path = Path(path_item).expanduser().resolve()

            if path.is_file():
                annotation_file_paths.append(str(path))

            elif path.is_dir():
                for file_path in path.glob("**/*"):
                    if (
                        file_path.is_file()
                        and file_path.suffix.lower()
                        in consts.SUPPORTED_ANNOTATION_FILE_EXTENSIONS
                    ):
                        annotation_file_paths.append(str(file_path))

            else:
                raise ViInvalidParameterError(
                    "paths",
                    f"Invalid path: {path_item}. Path must be a file or directory",
                )

        return annotation_file_paths

    def get_annotation_import_session(
        self,
        dataset_id: str,
        annotation_import_session_id: str,
    ) -> responses.AnnotationImportSession:
        """Get an annotation import session."""
        self._link_parser = AnnotationImportSessionLinkParser(
            self._auth.organization_id, dataset_id
        )

        response = self._requester.get(
            self._link_parser(annotation_import_session_id),
            response_type=responses.AnnotationImportSession,
        )

        if isinstance(response, responses.AnnotationImportSession):
            return response

        raise ValueError(f"Invalid response {response} with type {type(response)}")

    def _patch_annotation_import_session(
        self,
        dataset_id: str,
        annotation_import_session_id: str,
        condition: responses.AnnotationImportSessionCondition,
    ) -> responses.AnnotationImportSession:
        """Patch an annotation import session."""
        self._link_parser = AnnotationImportSessionLinkParser(
            self._auth.organization_id, dataset_id
        )

        patch_status = AnnotationImportPatchStatus(
            status=AnnotationImportPatchCondition(conditions=[condition])
        )

        response = self._requester.patch(
            self._link_parser(f"{annotation_import_session_id}/status"),
            json_data=msgspec.to_builtins(patch_status, str_keys=True),
            response_type=responses.AnnotationImportSession,
        )

        if isinstance(response, responses.AnnotationImportSession):
            return response

        raise ValueError(f"Invalid response {response} with type {type(response)}")

    def _create_annotation_import_session(
        self,
        dataset_id: str,
        upload_timeout: int,
        failure_policies: AnnotationImportFailurePolicy,
        source: AnnotationImportSource,
        attributes: dict[str, str] | None,
    ) -> responses.AnnotationImportSession:
        """Create an annotation import session."""
        self._link_parser = AnnotationImportSessionLinkParser(
            self._auth.organization_id, dataset_id
        )

        annotation_import_session = AnnotationImportSession(
            spec=AnnotationImportSpec(
                upload_before=int((time.time() + upload_timeout) * 1000),
                failure_policies=failure_policies,
                source=source,
            ),
            metadata=ResourceMetadata(attributes=attributes or {}),
        )

        response = self._requester.post(
            self._link_parser(),
            json_data=msgspec.to_builtins(annotation_import_session, str_keys=True),
            response_type=responses.AnnotationImportSession,
        )

        if isinstance(response, responses.AnnotationImportSession):
            return response

        raise ValueError(f"Invalid response {response} with type {type(response)}")

    def _add_files_to_session(
        self,
        dataset_id: str,
        annotation_import_session_id: str,
        annotation_file_paths: list[str],
    ) -> responses.AnnotationImportFilesResponse:
        """Add files to the session."""
        self._link_parser = AnnotationImportSessionLinkParser(
            self._auth.organization_id, dataset_id
        )

        annotation_files_for_upload = {}
        for file_path in annotation_file_paths:
            annotation_files_for_upload.update(
                {Path(file_path).name: self._generate_annotation_file_spec(file_path)}
            )

        payload = AnnotationImportPayload(files=annotation_files_for_upload)

        response = self._requester.post(
            self._link_parser(f"{annotation_import_session_id}/files"),
            json_data=msgspec.to_builtins(payload, str_keys=True),
            response_type=responses.AnnotationImportFilesResponse,
        )

        if isinstance(response, responses.AnnotationImportFilesResponse):
            return response

        raise ValueError(f"Invalid response {response} with type {type(response)}")

    def _upload_files(
        self,
        annotation_file_paths: list[str],
        files_response: responses.AnnotationImportFilesResponse,
        progress: ViProgress | None,
        task: TaskID | None,
        handler: GracefulExit,
    ) -> None:
        """Upload files to the session."""
        filtered_file_paths = []
        for file_path in files_response.files.keys():
            matching_path = next(
                (
                    path
                    for path in annotation_file_paths
                    if os.path.basename(path) == file_path
                ),
                None,
            )
            if matching_path:
                filtered_file_paths.append(matching_path)

        # Step 3: Upload files using signed URLs
        if progress and task is not None:
            progress.update(
                task,
                description=f"Uploading 0 / {len(filtered_file_paths)} files...",
                advance=1,
            )

        for i, (file_path, file_upload_url) in enumerate(
            zip(filtered_file_paths, files_response.files.values())
        ):
            if handler.exit_now:
                if progress and task is not None:
                    progress.update(task, description="✗ Upload cancelled")
                raise KeyboardInterrupt

            self._upload_single_file(file_path, file_upload_url)
            if progress and task is not None:
                progress.update(
                    task,
                    description=f"Uploading {i + 1} / {len(filtered_file_paths)} files...",
                    advance=1,
                )

        if progress and task is not None:
            progress.update(
                task,
                description="✓ Upload complete!",
                completed=len(filtered_file_paths),
                refresh=True,
            )

    def _upload_single_file(
        self, file_path: str, file_upload_url: responses.AnnotationImportFileUploadUrl
    ) -> None:
        """Upload a file to the upload session."""
        with open(file_path, "rb") as f:
            upload_response = self._http_client.request(
                file_upload_url.method,
                file_upload_url.url,
                content=f,
                headers=file_upload_url.headers,
            )
            upload_response.raise_for_status()

    def _generate_annotation_file_spec(
        self, annotation_path: Path | str
    ) -> AnnotationImportFileSpec:
        """Generate annotation file spec."""
        annotation_path = Path(annotation_path).expanduser().resolve()
        size = annotation_path.stat().st_size

        crc32c_value = calculate_crc32c(annotation_path, base64_encoded=True)

        return AnnotationImportFileSpec(size_bytes=size, crc32c=crc32c_value)
