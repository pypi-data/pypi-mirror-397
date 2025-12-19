"""Job and JobPayloadBuilder modules for creating and managing Coda jobs."""

import copy
import requests
import sys
import time

from typing import TYPE_CHECKING, List, Dict, Any
from coda.sdk.enums import Format, FrameRate, Language, VenueType
from .constants import DEFAULT_PROGRAM_ID
from .essence import Essence
from .utils import validate_group_id, make_request
from ..tc_tools import tc_to_time_seconds

if TYPE_CHECKING:
    from .workflow import WorkflowDefinition


class JobPayloadBuilder:
    """Coda Job payload builder."""

    def __init__(self, name: str) -> None:
        """Initialize the CodaJobBuilder.

        This constructor sets up a new job payload builder with a given name and
        initializes the internal attributes that will be configured through
        the builder's various `.with_*()` methods.

        Args:
            name (str): The name of the job, used for identification.

        Raises:
            ValueError: If the provided name is empty.

        """
        if not name or not isinstance(name, str):
            raise ValueError("Job name must be a non-empty string.")

        self._name: str = name
        self._group_id: str = validate_group_id()
        self._venue: str = VenueType.NEARFIELD
        self._language: str = Language.UNDETERMINED
        self._essences: List[Essence] = []
        self._time_options: Dict = {}
        self._workflow: WorkflowDefinition | None = None
        self._edits: Dict | None = None
        self._reference_run: int | None = None

    def with_venue(self, venue: VenueType) -> "JobPayloadBuilder":
        """Set the input venue for the job.

        Args:
            venue (VenueType): The input venue enum.

        Returns:
            JobPayloadBuilder: The builder instance for fluent chaining.

        """
        self._venue = venue.value
        return self

    def with_language(self, language: Language) -> "JobPayloadBuilder":
        """Set the output language for the job.

        Args:
            language (Language): The output language enum.

        Returns:
            JobPayloadBuilder: The builder instance for fluent chaining.

        """
        self._language = language.value
        return self

    def with_input_timing(
        self, frame_rate: FrameRate | None = None, ffoa: str | None = None, lfoa: str | None = None, start_time: str | None = None
    ) -> "JobPayloadBuilder":
        """Set the input timing information for the source files.

        Args:
            frame_rate (FrameRate, optional): The frame rate enum. Defaults to None.
            ffoa (str, optional): The first frame of audio timecode. Defaults to None.
            lfoa (str, optional): The last frame of audio timecode. Defaults to None.
            start_time (str, optional): The start time in timecode format. Defaults to None.

        Returns:
            JobPayloadBuilder: The builder instance for fluent chaining.

        """
        self._time_options["frame_rate"] = frame_rate
        self._time_options["ffoa"] = ffoa
        self._time_options["lfoa"] = lfoa
        if start_time is not None:
            self._time_options["start_time"] = tc_to_time_seconds(start_time, frame_rate)
        return self

    def with_essences(self, essences: List[Essence]) -> "JobPayloadBuilder":
        """Add a list of Essence objects to the job's inputs.

        Args:
            essences (List[Essence]): A list of Essence objects.

        Returns:
            JobPayloadBuilder: The builder instance for fluent chaining.

        Raises:
            TypeError: If input is not a list or if any item in the list is not an Essence object.

        """
        if not isinstance(essences, list):
            raise TypeError("Essences must be provided as a list.")

        for essence in essences:
            if not isinstance(essence, Essence):
                raise TypeError(f"All items in list must be CodaEssence objects, but found an object of type {type(essence).__name__}.")

        self._essences.extend(essences)

        return self

    def with_workflow(self, workflow: "WorkflowDefinition") -> "JobPayloadBuilder":
        """Set the WorkflowDefinition for the job.

        Args:
            workflow (WorkflowDefinition): The WorkflowDefinition object.

        Returns:
            JobPayloadBuilder: The builder instance for fluent chaining.

        Raises:
            TypeError: If the provided workflow is not a valid WorkflowDefinition object.

        """
        if not hasattr(workflow, "__class__") or workflow.__class__.__name__ != "WorkflowDefinition":
            raise TypeError(f"Workflow must be a valid Workflow object, but received type {type(workflow).__name__}.")

        self._workflow = copy.deepcopy(workflow)
        return self

    def with_edits(self, edits: dict) -> "JobPayloadBuilder":
        """Add an edit payload for reel splitting.

        Args:
            edits (dict): The reel edit payload dictionary.

        Returns:
            JobPayloadBuilder: The builder instance for fluent chaining.

        Raises:
            TypeError: If the provided edits is not a dictionary.

        Example:
            edit_payload = {
                "reel_splitting": {
                    "leader_integer_seconds": 8,
                    "prelap_integer_seconds": 2,
                    "overlap_integer_seconds": 2,
                    "tail_leader_integer_seconds": 2,
                    "reel_pops": True
                },
                "reels": [
                    {
                        "source_start_time": "01:00:00:00",
                        "dest_start_time": "00:00:00:00"
                    },
                    {
                        "source_start_time": "01:00:07:00",
                        "dest_start_time": "00:00:00:00"
                    },
                    {
                        "source_start_time": "01:00:12:00",
                        "dest_start_time": "00:00:00:00"
                    },
                    {
                        "source_start_time": "01:00:20:00",
                        "dest_start_time": "00:00:00:00"
                    }
                ]
            }

        """
        if not isinstance(edits, dict):
            raise TypeError("Edits must be provided as a dictionary.")

        self._edits = edits
        return self

    def with_reference_job(self, job_id: int) -> "JobPayloadBuilder":
        """Set a parent job to use for cache referencing.

        Args:
            job_id (int): The ID of the reference job.

        Returns:
            JobPayloadBuilder: The builder instance for fluent chaining.

        Raises:
            TypeError: If the provided job_id is not an integer.

        """
        if not isinstance(job_id, int):
            raise TypeError("Reference job ID must be an integer.")

        self._reference_run = job_id
        return self

    def with_forced_imax5(self) -> "JobPayloadBuilder":
        """Force all essences to the 'imax5' format, if compatible.

        Verifies that all added essences have a compatible format ('5.0' or
        'imax5') and then updates them.

        Returns:
            JobPayloadBuilder: The builder instance for fluent chaining.

        Raises:
            ValueError: If no essences have been added yet.
            ValueError: If any essence has an incompatible format.

        """
        if not self._essences:
            raise ValueError(
                "Cannot force imax5. No essences have been added. "
                "Call with_essences() before using this method."
            )

        incompatible_formats = [
            essence.payload["definition"]["format"]
            for essence in self._essences
            if essence.payload["definition"]["format"] not in ["5.0", "imax5"]
        ]

        if incompatible_formats:
            raise ValueError(
                f"Cannot force imax5. Incompatible formats found: {', '.join(set(incompatible_formats))}"
            )

        for essence in self._essences:
            essence.payload["definition"]["format"] = "imax5"

        return self

    def with_input_language(self, language: Language) -> "JobPayloadBuilder":
        """Set the language for all input essences.

        Args:
            language (Language): The language code.

        Returns:
            JobPayloadBuilder: The builder instance for fluent chaining.

        Raises:
            ValueError: If no essences have been added yet.

        """
        if not self._essences:
            raise ValueError(
                "Cannot set input language. No essences have been added. "
                "Call with_essences() before using this method."
            )

        for essence in self._essences:
            essence.payload["definition"]["language"] = language.value
        return self

    def with_program_for_type(
        self, type: str, program: str = DEFAULT_PROGRAM_ID
    ) -> "JobPayloadBuilder":
        """Set the program for all essences of a specific type.

        Args:
            type (str): The essence type.
            program (str, optional): The program name. Defaults to "program-1".

        Returns:
            JobPayloadBuilder: The builder instance for fluent chaining.

        Raises:
            ValueError: If no essences have been added yet.

        """
        if not self._essences:
            raise ValueError(
                "Cannot set program for type. No essences have been added. "
                "Call with_essences() before using this method."
            )

        for essence in self._essences:
            if type in essence.payload["definition"]["type"]:
                essence.payload["definition"]["program"] = program
        return self

    def with_program_for_format(
        self, format: Format, program: str = DEFAULT_PROGRAM_ID
    ) -> "JobPayloadBuilder":
        """Set the program for all essences of a specific format.

        Args:
            format (Format): The essence format.
            program (str, optional): The program name. Defaults to "program-1".

        Returns:
            JobPayloadBuilder: The builder instance for fluent chaining.

        Raises:
            ValueError: If no essences have been added yet.

        """
        if not self._essences:
            raise ValueError(
                "Cannot set program for format. No essences have been added. "
                "Call with_essences() before using this method."
            )

        for essence in self._essences:
            if format == essence.payload["definition"]["format"]:
                essence.payload["definition"]["program"] = program
        return self

    def with_unique_program(self, program: str = DEFAULT_PROGRAM_ID) -> "JobPayloadBuilder":
        """Set the same program for all input essences.

        Args:
            program (str, optional): The program name. Defaults to "program-1".

        Returns:
            JobPayloadBuilder: The builder instance for fluent chaining.

        Raises:
            ValueError: If no essences have been added yet.

        """
        if not self._essences:
            raise ValueError(
                "Cannot set unique program. No essences have been added. "
                "Call with_essences() before using this method."
            )

        for essence in self._essences:
            essence.payload["definition"]["program"] = program
        return self

    def build(self) -> dict:
        """Assemble and return the final job payload dictionary.

        Returns:
            dict: The assembled job payload dictionary.

        Raises:
            ValueError: If critical components like essences or workflow have not been set.

        """
        if not self._essences:
            raise ValueError("Cannot build job payload: At least one essence must be added.")
        if not self._workflow:
            raise ValueError("Cannot build job payload: A workflow must be set.")
        if not self._venue:
            raise ValueError("Cannot build job payload: A venue must be set.")

        ffoa = None
        lfoa = None
        fr = None

        if self._time_options.get("frame_rate"):
            fr = self._time_options.get("frame_rate")
        if self._time_options.get("ffoa"):
            ffoa = self._time_options.get("ffoa")
        if self._time_options.get("lfoa"):
            lfoa = self._time_options.get("lfoa")

        for e in self._essences:
            current_timing = e.payload.get("timing_info") or {}
            new_timing = dict(current_timing)
            if not new_timing.get("ffoa_timecode"):
                new_timing["ffoa_timecode"] = ffoa
            if not new_timing.get("lfoa_timecode"):
                new_timing["lfoa_timecode"] = lfoa
            if not new_timing.get("source_frame_rate"):
                new_timing["source_frame_rate"] = fr
            e.payload["timing_info"] = new_timing

        sources = [e.dict() for e in self._essences]

        start_time = self._time_options.get("start_time")
        if start_time is not None:
            for source_obj in sources:
                definition = source_obj.get("definition", {})
                if "resources" in definition:
                    for r in definition["resources"]:
                        if "sample_rate" in r:
                            r["bext_time_reference"] = int(start_time * r["sample_rate"])

        wf_in = {
            "project": {
                "title": self._name,
                "language": self._language,
            },
            "venue": self._venue,
            "sources": sources,
            "source_frame_rate": fr,
            "ffoa_timecode": ffoa,
            "lfoa_timecode": lfoa,
        }

        if self._edits:
            wf_in["edits"] = self._edits

        wf_def = copy.deepcopy(self._workflow.dict())

        if "packages" in wf_def:
            package_data = {}
            for package_id, pdata in wf_def["packages"].items():
                if "naming_convention" in pdata.get("definition", {}):
                    package_data[package_id] = {
                        "naming_convention": pdata["definition"]["naming_convention"]
                    }
                    del pdata["definition"]["naming_convention"]
            if package_data:
                wf_in["package_data"] = package_data

        payload = {
            "workflow_input": wf_in,
            "workflow_definition": wf_def,
        }

        if self._reference_run:
            payload["parent_job_id"] = self._reference_run

        return payload


class Job:
    """Create and manage Coda Jobs."""

    def __init__(self, payload: dict) -> None:
        """Initialize the CodaJob with a payload.

        Args:
            payload (dict): The job payload dictionary.

        Raises:
            ValueError: If payload is missing or invalid.

        """
        if not payload or "workflow_input" not in payload:
            raise ValueError("Cannot initialize CodaJob with an invalid payload.")
        self.payload = payload
        self.group_id = validate_group_id()

    def validate(self, skip_cloud_validation: bool = True) -> requests.Response:
        """Validate the job payload against the Coda API.

        Args:
            skip_cloud_validation (bool, optional): Whether to skip cloud validation. Defaults to True.

        Returns:
            requests.Response: The validation response object.

        """
        endpoint = f"/interface/v2/groups/{self.group_id}/jobs/validate?skip_cloud_validation={skip_cloud_validation}"
        return make_request(requests.post, endpoint, self.payload)

    def run(self) -> int | None:
        """Validate the payload against the Coda API and run the job.

        Returns:
            int | None: The job ID if successful, otherwise None.

        """
        print("Validating job payload.", file=sys.stderr)
        validation_result = self.validate()

        if validation_result.status_code != 200:
            print("Job validation failed. Cannot run job.", file=sys.stderr)
            print(validation_result.json(), file=sys.stderr)
            return None

        print("Launching job.", file=sys.stderr)
        endpoint = f"/interface/v2/groups/{self.group_id}/jobs"
        response = make_request(requests.post, endpoint, self.payload)
        response_json = response.json()

        print(response_json, file=sys.stderr)
        if "errors" in response_json or "job_id" not in response_json:
            return None

        return int(response_json["job_id"])

    def get_edge_payload(self, skip_cloud_validation: bool = True) -> dict:
        """Get the raw conductor graph for a coda edge job.

        Args:
            skip_cloud_validation (bool, optional): Whether to skip cloud validation.
                Defaults to True.

        Returns:
            dict: The coda edge payload.

        Raises:
            RuntimeError: If job validation fails or edge payload retrieval fails.

        """
        validation_result = self.validate(skip_cloud_validation=skip_cloud_validation)

        if validation_result.status_code != 200:
            raise RuntimeError(f"Edge job validation failed. \nStatus: {validation_result.status_code}\n Resp: {validation_result.json()}")

        endpoint = f"/interface/v2/groups/{self.group_id}/edge?skip_cloud_validation={skip_cloud_validation}"
        response = make_request(requests.post, endpoint, self.payload)

        if response.status_code != 200:
            raise RuntimeError(f"Edge payload retrieval failed with status code: {response.json()}")

        try:
            edge_payload = response.json()
        except Exception as err:
            raise RuntimeError(f"Error parsing edge payload response: {err}") from err

        if "errors" in edge_payload:
            raise RuntimeError(f"Edge payload retrieval failed with errors: {edge_payload['errors']}")

        return edge_payload

    @staticmethod
    def validate_raw_payload(json_payload: dict) -> requests.Response:
        """Validate a raw JSON payload dictionary against the Coda API.

        Args:
            json_payload (dict): The raw JSON payload dictionary.

        Returns:
            requests.Response: The raw payload validation response object.

        """
        group_id = validate_group_id()
        endpoint = f"/interface/v2/groups/{group_id}/jobs/validate"
        response = make_request(requests.post, endpoint, json_payload)
        print("validate raw: ", response.json(), file=sys.stderr)
        return response

    @staticmethod
    def run_raw_payload(json_payload: dict) -> int | None:
        """Validate and run a job from a raw JSON payload dictionary.

        Args:
            json_payload (dict): The raw JSON payload dictionary.

        Returns:
            int | None: The job ID if successful, otherwise None.

        """
        group_id = validate_group_id()

        validation_result = Job.validate_raw_payload(json_payload)
        if validation_result.status_code != 200:
            print("Raw payload validation failed. Cannot run job.", file=sys.stderr)
            print(validation_result.json(), file=sys.stderr)
            return None

        endpoint = f"/interface/v2/groups/{group_id}/jobs"
        response = make_request(requests.post, endpoint, json_payload)
        response_json = response.json()

        print(response_json, file=sys.stderr)
        if "errors" in response_json or "job_id" not in response_json:
            return None

        return int(response_json["job_id"])

    @staticmethod
    def get_status(job_id: int) -> Dict[str, Any] | None:
        """Get the status of a job.

        This method polls the API for the job's status and will retry up to 3 times
        if an error is encountered during the request.

        Args:
            job_id (int): The ID of the job.

        Returns:
            dict | None: The job status and progress if successful, otherwise None.

        """
        group_id = validate_group_id()
        ret = make_request(
            requests.get, f"/interface/v2/groups/{group_id}/jobs/{job_id}"
        )
        j = ret.json()
        error_count = 0
        while "error" in j and error_count < 3:
            print("error in get_status: ", ret.status_code, j["error"], file=sys.stderr)
            time.sleep(1)
            ret = make_request(
                requests.get, f"/interface/v2/groups/{group_id}/jobs/{job_id}"
            )
            j = ret.json()
            error_count += 1
        if "error" in j:
            return None
        return {"status": j["status"], "progress": j["progress"]}

    @staticmethod
    def get_report(job_id: int) -> dict:
        """Get the report of a job.

        Args:
            job_id (int): The ID of the job.

        Returns:
            dict: The job report JSON.

        """
        ret = make_request(requests.get, f"/interface/v2/report/{job_id}/raw")
        return ret.json()

    @staticmethod
    def get_jobs_by_date(start_date: str, end_date: str) -> list:
        """Get jobs within a date range.

        Args:
            start_date (str): Start date for the query.
            end_date (str): End date for the query.

        Returns:
            list: List of jobs within the date range.

        """
        ret = make_request(requests.get, f"/interface/v1/jobs?sort=asc&start_date={start_date}&end_date={end_date}")
        return ret.json()
