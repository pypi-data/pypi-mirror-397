from __future__ import annotations

from abc import ABC
from typing import Any

from ids_peak_common.exceptions import IOException
from ids_peak_common.pipeline.ipipeline import IPipeline


class PipelineBase(IPipeline, ABC):
    """
    Base class for implementing a custom pipeline.

    Provides a partial implementation of the IPipeline interface.
    Can be used as a foundation for creating custom pipeline behavior.

    .. versionadded:: ids_peak_common 1.1
    .. ingroup:: ids_peak_common_python_pipeline
    """

    def export_settings_to_file(self, file_path: str) -> None:
        """
        Saves the current settings of the pipeline and its modules to a file.

        This base implementation calls `export_settings_to_string()` and
        writes the resulting string to the specified file path.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.export_settings_to_string())
        except OSError as e:
            raise IOException(
                f"Saving settings to the file {file_path} failed: {e}") from e

    def import_settings_from_file(self, file_path: str) -> None:
        """
        Loads the settings of the pipeline and its modules from a file.

        This base implementation reads the file contents and passes them to
        `import_settings_from_string()` to restore the pipeline state.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                settings = f.read()
            self.import_settings_from_string(settings)
        except OSError as e:
            raise IOException(
                f"Loading settings from the file {file_path} failed: {e}"
            ) from e

    def process(self, data: Any) -> Any:
        """
        Processes the input data through all pipeline modules
        and returns the result.

        This base implementation iterates over all modules returned
        by `get_modules()`, calling each module's `process()` method in
        sequence and passing the result along.

        :param data: The input data to process.

        :return: The processed input.
        """
        for module in self._modules:
            data = module.process(data)

        return data
