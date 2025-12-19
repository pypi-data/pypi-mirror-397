import os
import sys
import json
import shutil
import subprocess

from pathlib import Path
from typing import List, Dict
from .enums import Format, SourceType, InputStemType
from .constants import (
    ENV_CODA_CLI_EXE,
    ENV_NO_CODA_EXE,
    ENV_CODA_API_GROUP_ID,
    DEFAULT_PROGRAM_ID,
    DEFAULT_BIT_DEPTH,
    DEFAULT_SAMPLE_RATE,
    URL_PREFIX_S3,
    URL_PREFIX_IO,
)


class Essence:
    """Single source essence for a Coda job.

    This class constructs the essence/s payload, which can
    consist of one or more media files (e.g., an interleaved WAV or a
    group of multi-mono WAVs).

    Attributes:
        payload (dict): The dictionary that holds the essence definition.

    """

    def __init__(
        self,
        format: Format,
        stem_type: InputStemType = InputStemType.PRINTMASTER,
        program: str = DEFAULT_PROGRAM_ID,
        description: str = "",
        timing_info: dict[str, str] | None = None
    ) -> None:
        """Initialize the CodaEssence object.

        Args:
            format (Format): The input audio format of the essence (e.g., "5.1", "7.1.2", "atmos").
            stem_type (InputStemType, optional): The type of input source stem (e.g., "audio/pm", "audio/dx").
                Defaults to InputStemType.PRINTMASTER.
            program (str, optional): The program identifier for the essence definition.
                Defaults to "program-1".
            description (str, optional): A human-readable description of the essence.
                Defaults to "".
            timing_info (dict, optional): Framerate, FFOA and LFOA info.

        Raises:
            ValueError: If format is an empty string.

        """
        if not format or not isinstance(format, str):
            raise ValueError("format must not be an empty string and must be a string type.")

        self.payload = {
            "type": "",
            "definition": {
                "format": format,
                "program": program,
                "description": description,
                "type": stem_type,
            },
            "timing_info": timing_info
        }

    def add_interleaved_resource(
        self,
        file: str | dict,
        channel_selection: dict[str, int],
        channel_count: int,
        frames: int,
        bit_depth: int = DEFAULT_BIT_DEPTH,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        io_location_id: str | None = None
    ) -> None:
        """Configure the essence as a single interleaved resource.

        This sets the essence type to 'interleaved' and populates the definition
        with the properties of a single, multichannel media file.

        Args:
            file (str | dict): The filepath of the interleaved media file, or a dict containing a 'url' key.
                If a dict is passed in it will require a 'url' key to sepcify the location path.
                The dict can contain the optional keys 'auth' and 'opts' for resource authorization.
            channel_selection (dict[str, int]): A map of channel labels to their stream IDs.
            channel_count (int): The total number of channels in the file.
            frames (int): The duration of the file in frames.
            bit_depth (int, optional): The bit depth. Defaults to 24.
            sample_rate (int, optional): The sample rate. Defaults to 48000.
            io_location_id (str, optional): The IO Location ID associated with the source files. Required for agent transfers.

        Raises:
            TypeError: If channel_selection is not a dictionary.
            ValueError: If IO Location ID has not been provided for non-S3 sources.

        """
        if not isinstance(channel_selection, dict):
            raise TypeError("channel_selection must be a dictionary.")

        self.payload["type"] = SourceType.INTERLEAVED

        if isinstance(file, str):
            url = file
            auth = None
            opts = None
        else:
            url = file["url"]
            auth = file.get("auth")
            opts = file.get("opts")

        if URL_PREFIX_S3 not in url:
            if io_location_id is None:
                raise ValueError("IO Location ID is required for non-S3 file sources.")
            url = f"{URL_PREFIX_IO}{io_location_id}{url}"

        resource_dict = {"url": url}
        if auth is not None:
            resource_dict["auth"] = auth
        if opts is not None:
            resource_dict["opts"] = opts

        self.payload["definition"].update({
            "resource": resource_dict,
            "bit_depth": bit_depth,
            "sample_rate": sample_rate,
            "channel_count": channel_count,
            "frames": frames,
            "channel_selection": channel_selection.copy(),
        })

    def add_multi_mono_resources(
        self, files: List, frames: int, bit_depth: int = DEFAULT_BIT_DEPTH, sample_rate: int = DEFAULT_SAMPLE_RATE, io_location_id: str | None = None
    ) -> None:
        """Configure the essence as a group of multi-mono resources.

        This sets the essence type to 'multi_mono' and populates the definition
        with a list of single-channel media files that form a multichannel group.

        Args:
            files (list): A list of file URLs (or dicts with 'url' keys).
            frames (int): The duration of the files in frames.
            bit_depth (int, optional): The bit depth. Defaults to 24.
            sample_rate (int, optional): The sample rate. Defaults to 48000.
            io_location_id (str, optional): The IO Location ID associated with the source files. Required for agent transfers.

        Raises:
            TypeError: If files is not a list.
            ValueError: If the number of provided files does not match the
                channel count implied by the essence's format.
            ValueError: If IO Location ID has not been provided for non-S3 sources.

        """
        if not isinstance(files, list):
            raise TypeError("files must be provided as a list.")

        stem_format = self.payload["definition"]["format"]
        if stem_format != Format.ATMOS:
            try:
                expected_channels = sum(int(p) for p in stem_format.split('.'))
                actual_channels = len(files)
                if actual_channels != expected_channels:
                    raise ValueError(
                        f"Channel count mismatch for format '{stem_format}': "
                        f"Expected {expected_channels} files for multi-mono resources, but received {actual_channels}."
                    )
            except (ValueError, TypeError) as e:
                if isinstance(e, ValueError) and "Channel count mismatch" in str(e):
                    raise e
                print(
                    f"Warning: Could not validate channel count for format '{stem_format}'.",
                    file=sys.stderr,
                )

        self.payload["type"] = SourceType.MULTI_MONO.value
        self.payload["definition"]["resources"] = []
        for file_entry in files:
            if isinstance(file_entry, str):
                url = file_entry
                auth = None
                opts = None
                label = ""
            else:
                url = file_entry["url"]
                auth = file_entry.get("auth")
                opts = file_entry.get("opts")
                label = file_entry.get("channel_label", "")

            if not label:
                ch_labels = [
                    "Lsr", "Rsr", "Lts", "Rts", "Lss", "Rss",
                    "Lfe", "Ls", "Rs", "L", "C", "R",
                ]
                for ch in ch_labels:
                    if "." + ch.upper() + "." in url.upper():
                        label = "LFE" if ch == "Lfe" else ch.capitalize()
                        break

            if URL_PREFIX_S3 not in url:
                if io_location_id is None:
                    raise ValueError("IO Location ID is required for non-S3 file sources.")
                url = f"{URL_PREFIX_IO}{io_location_id}{url}"

            res = {
                "resource": {"url": url},
                "bit_depth": bit_depth,
                "sample_rate": sample_rate,
                "channel_count": 1,
                "frames": frames,
                "channel_label": label,
                "bext_time_reference": 0,
            }
            if auth is not None:
                res["resource"]["auth"] = auth
            if opts is not None:
                res["resource"]["opts"] = opts
            print(res)
            self.payload["definition"]["resources"].append(res)

    def override_stem_type(self, stem_type: InputStemType) -> None:
        """Override the stem type of the essence input source.

        Args:
            stem_type: The type of input source stem (e.g., "audio/pm", "audio/dx").

        """
        self.payload["definition"]["type"] = stem_type

    def override_program(self, program: str) -> None:
        """Override the program identifier of the essence.

        Args:
            program (str): The program identifier for the essence definition.

        """
        self.payload["definition"]["program"] = program

    def override_format(self, format: Format) -> None:
        """Override the audio format of the essence input source.

        Args:
            format (Format): The input audio format of the essence (e.g., "5.1", "7.1.2", "atmos").

        """
        self.payload["definition"]["format"] = format

    def override_language(self, language) -> None:
        """Override the language of the essence.

        Args:
            language: The language for the essence (e.g., Language.ENGLISH).

        """
        lang_value = language.value if hasattr(language, 'value') else language
        self.payload["definition"]["language"] = lang_value

    def override_timing_info(
        self,
        source_frame_rate=None,
        ffoa_timecode: str | None = None,
        lfoa_timecode: str | None = None
    ) -> None:
        """Override timing information for the essence.

        All parameters are optional. Only provided values will be set.

        Args:
            source_frame_rate: The source frame rate (e.g., FrameRate.TWENTY_FOUR).
            ffoa_timecode (str, optional): First frame of action timecode.
            lfoa_timecode (str, optional): Last frame of action timecode.

        """
        # Initialize timing_info if it's None
        if self.payload["timing_info"] is None:
            self.payload["timing_info"] = {}

        if source_frame_rate is not None:
            fr_value = source_frame_rate.value if hasattr(source_frame_rate, 'value') else source_frame_rate
            self.payload["timing_info"]["source_frame_rate"] = fr_value
        if ffoa_timecode is not None:
            self.payload["timing_info"]["ffoa_timecode"] = ffoa_timecode
        if lfoa_timecode is not None:
            self.payload["timing_info"]["lfoa_timecode"] = lfoa_timecode

    def override_bext_time_reference(self, bext_time_reference: int) -> None:
        """Set BEXT time reference on all resources.

        Args:
            bext_time_reference (int): The BEXT time reference value.

        """
        for resource in self.payload["definition"]["resources"]:
            resource["bext_time_reference"] = bext_time_reference

    @staticmethod
    def essences_from_files(
        files: list,
        io_location_id: str | None = None,
        file_info: dict | None = None,
        program: str = "",
        forced_frame_rate: str | None = None,
        no_file_scan: bool = False
    ) -> list["Essence"]:
        """Create a list of CodaEssence objects from files.

        This method inspects local files using the 'coda inspect' command-line tool
        to automatically determine their properties. For S3 files or when the CLI
        is unavailable, it relies on the `file_info` dictionary for manual creation.

        Args:
            files (List): A list of file paths.
            io_location_id (str, optional): The IO Location ID associated with the source files. Required for agent transfers.
            file_info (dict, optional): Manual override info for files. Required for S3.
                Should contain keys like 'format', 'type', 'frames', 's3_auth'. Defaults to None.
                Examples: file_info = {
                            "frames": 720000,
                            "format": Format.SEVEN_ONE,
                            "type": InputStemType.PRINTMASTER,
                            "s3_auth": {
                                "iam_role": os.getenv(ENV_S3_ROLE, "XXXX"),
                                "iam_external_id": os.getenv(ENV_S3_EXTERNAL_ID, "XXXX"),
                            },
                            "s3_options": {"region": "us-west-2"},
                        }

                        Note: `s3_auth` may also use S3 access key secret and ID
                        "s3_auth": {
                            "access_key_id": os.getenv(ENV_S3_ACCESS_KEY_ID, "XXXX"),
                            "secret_access_key": os.getenv(ENV_S3_SECRET_ACCESS_KEY, "XXXX"),
                        }
            program (str, optional): The program identifier to assign to the essences.
                Defaults to "".
            forced_frame_rate (str, optional): Specify the frame rate to calculate the FFOA and LFOA
            no_file_scan (bool, optional): Do not use Coda CLI to scan files for metadata

        Raises:
            ValueError: If `files` is not populated with a list of file paths.
            ValueError: If the 'coda' CLI tool is required but not found, or if
                the inspection process fails.
            ValueError: If the 'coda inspect' CLI tool does not return sources info.
            ValueError: If S3 files are provided without a `file_info` dictionary.
            ValueError: If IO Location ID has not been provided for non-S3 sources.
            ValueError: If CODA_API_GROUP_ID has not been set for using `coda inspect`.

        Returns:
            List[CodaEssence]: A list of CodaEssence objects.

        """
        if not files:
            raise ValueError("Files must contain a list of file paths.")

        local_files = [f for f in files if URL_PREFIX_S3 not in str(f)]
        s3_files = [f for f in files if URL_PREFIX_S3 in str(f)]
        essences = []

        if local_files:
            if io_location_id is None:
                raise ValueError("IO Location ID must be filled to use supplied files.")

            absfiles = [str(Path(f).resolve()) for f in local_files]
            codaexe = shutil.which("coda") or os.getenv(ENV_CODA_CLI_EXE)
            if not codaexe or os.getenv(ENV_NO_CODA_EXE) is not None or no_file_scan is True:
                if not file_info:
                    raise ValueError("Coda CLI not found and file_info was not provided for manual creation.")

                print("Creating essence manually from file_info.", file=sys.stderr)

                essence = Essence(file_info["format"], stem_type=file_info["type"], program=program)
                res = [{"url": url} for url in absfiles]
                essence.add_multi_mono_resources(res, frames=file_info["frames"], io_location_id=io_location_id)
                essences.append(essence)
            else:
                try:
                    group_id = os.getenv(ENV_CODA_API_GROUP_ID)
                    if not group_id:
                        raise ValueError("CODA_API_GROUP_ID must be set. Use workflow.with_group() for convenience.")

                    print(f"coda inspect scanning {len(absfiles)} files", file=sys.stderr)
                    print(f"using coda cli: {codaexe}", file=sys.stderr)

                    args = [codaexe, "inspect", "--group-id", group_id, "--io-location-id", io_location_id]
                    if forced_frame_rate:
                        args = [
                            *args,
                            "--frame-rate",
                            forced_frame_rate,
                        ]
                    args = [*args, *absfiles]

                    ret = subprocess.run(
                        args,
                        shell=False,
                        check=True,
                        capture_output=True,
                        text=True,
                    )

                    j = json.loads(ret.stdout)
                    print(json.dumps(j, indent=2))
                    if not j.get("sources"):
                        raise ValueError("`coda inspect` was unable to retrieve the sources information.")

                    timing_info = {
                        "source_frame_rate": j.get("source_frame_rate"),
                        "ffoa_timecode": j.get("ffoa_timecode"),
                        "lfoa_timecode": j.get("lfoa_timecode")
                    }

                    for source in j.get("sources", []):
                        source_type = source.get("type")
                        if source_type in [SourceType.ADM, SourceType.IAB_MXF]:
                            format = Format.ATMOS
                        source_def = source.get("definition")
                        essence = Essence(
                            format=source_def.get("format") or format,
                            stem_type=source_def.get("type"),
                            program=source_def.get("program", program),
                            description=source_def.get("description"),
                            timing_info=timing_info,
                        )

                        essence.payload["type"] = source_type

                        for key, value in source_def.items():
                            essence.payload["definition"][f"{key}"] = value

                        essences.append(essence)

                except subprocess.CalledProcessError as e:
                    error_message = (
                        f"The 'coda inspect' command failed with exit code {e.returncode}.\n"
                        f"--- STDOUT ---\n{e.stdout}\n"
                        f"--- STDERR ---\n{e.stderr}\n"
                    )
                    raise ValueError(error_message) from e
                except Exception as e:
                    raise ValueError(f"An unexpected error occurred during 'coda inspect': {e}") from e

        if s3_files:
            print(f"Adding {len(s3_files)} S3 files", file=sys.stderr)
            if not file_info:
                raise ValueError("file_info must be provided for S3 files.")

            essence = Essence(
                file_info["format"], stem_type=file_info["type"], program=program
            )

            res = [
                {
                    "url": r,
                    "auth": file_info.get("s3_auth"),
                    "opts": file_info.get("s3_options"),
                }
                for r in s3_files
            ]
            essence.add_multi_mono_resources(res, frames=file_info["frames"])
            essences.append(essence)

        return essences

    def dict(self) -> dict:
        """Return the final payload dictionary for the essence.

        Performs a validation check to ensure the number of resource files or
        channel selections matches the channel count specified by the audio format.

        Raises:
            ValueError: If the number of files/channels doesn't match the format's channel count.

        Returns:
            dict: The essence payload dictionary.

        """
        definition = self.payload["definition"]
        if definition.get("format") in [Format.ATMOS, Format.IMAX5, Format.IMAX6, Format.IMAX12]:
            return self.payload

        try:
            expected_channels = sum(int(e) for e in definition["format"].split("."))
            actual_channels = 0

            if "resources" in definition:
                actual_channels = len(definition["resources"])
            elif "channel_selection" in definition:
                actual_channels = len(definition["channel_selection"])

            if actual_channels > 0 and actual_channels != expected_channels:
                raise ValueError(
                    f"Channel count mismatch for format '{definition['format']}': "
                    f"Expected {expected_channels} channels, but found {actual_channels}."
                )

        except (ValueError, TypeError) as e:
            if isinstance(e, ValueError) and "Channel count mismatch" in str(e):
                raise e
            print(
                f"Warning: Could not validate channel count for format '{definition['format']}'.",
                file=sys.stderr,
            )

        return self.payload
