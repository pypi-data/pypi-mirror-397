import requests
import sys

from typing import ClassVar, Dict, Any, List
from .enums import PresetType
from .utils import make_request, validate_group_id


class Preset:
    """A client for interacting with Coda's preset API endpoints.

    This class provides methods to create, update, and retrieve various
    types of presets, such as those for loudness, naming conventions, and
    encoding profiles.

    Attributes:
        routes (ClassVar[Dict[PresetType, str]]): A mapping of preset types
            to their corresponding API endpoint routes.

    """

    group_path = "groups/:group_id/"

    routes: ClassVar[Dict[PresetType, str]] = {
        PresetType.JOBS: group_path + "jobs",
        PresetType.WORKFLOWS: group_path + "workflows",
        PresetType.LOUDNESS: group_path + "presets/loudness",
        PresetType.TIMECODE: group_path + "presets/timecode",
        PresetType.GROUPS: "groups",
        PresetType.NAMING: "naming-conventions",
        PresetType.DOLBY: "presets/encoding/dolby",
        PresetType.DTS: "presets/encoding/dts",
        PresetType.SUPER_SESSION: "presets/super-session",
        PresetType.IO_LOCATIONS: "io-locations",
    }

    def __init__(self, preset_type: PresetType, value: dict[str, Any]) -> None:
        """Initialize the Preset object.

        This constructor prepares a preset object that can be sent to the Coda
        API to either create a new preset or update an existing one.

        Args:
            preset_type (PresetType): The type of preset being handled (e.g.,
                LOUDNESS, NAMING).
            value (dict[str, Any]): The dictionary containing the preset's
                definition and name.

        Attributes:
            preset (PresetType): Stores the type of the preset.
            value (dict[str, Any]): Stores the definition payload for the preset.
            group_id (None): An initialized placeholder for the group ID.

        """
        self.preset = preset_type
        self.value = value
        self.group_id = None

    def register(self) ->  requests.Response:
        """Register (creates or updates) a preset in Coda.

        If a preset with the same name already exists, it will be updated.
        Otherwise, a new preset will be created.

        Raises:
            ValueError: If the preset type is invalid, or if a preset name
                is ambiguous (matches multiple existing presets).

        Returns:
            requests.Response: The Response object from the `requests` library.

        """
        if self.preset not in Preset.routes:
            raise ValueError(f"Invalid preset type provided: {self.preset}")

        presets = Preset.get_presets(self.preset)
        found_id = None
        if presets and len(presets) > 0:
            pf = [p for p in presets if p["name"] == self.value["name"]]
            if len(pf) > 1:
                raise ValueError(
                    f"Found multiple presets of type '{self.preset.value}' with the name '{self.value['name']}'. "
                    "Preset names must be unique."
                )
            if len(pf) == 1:
                # Map preset type to its specific ID key
                key_map = {
                    PresetType.DOLBY: "encoding_preset_id",
                    PresetType.DTS: "encoding_preset_id",
                    PresetType.LOUDNESS: "loudness_preset_id",
                    PresetType.TIMECODE: "timecode_preset_id",
                    PresetType.NAMING: "id",
                    PresetType.SUPER_SESSION: "super_session_preset_id",
                    PresetType.GROUPS: "group_id",
                }
                id_key = key_map.get(self.preset)
                if id_key:
                    found_id = pf[0][id_key]

        route = Preset.routes[self.preset]
        if ":group_id" in route:
            route = route.replace(":group_id", str(validate_group_id()))

        if not found_id:
            # Add preset with that name for the first time
            print(f"creating new preset {self.value['name']}", file=sys.stderr)
            ret = make_request(requests.post, f"/interface/v2/{route}", self.value)
        else:
            request_type = requests.patch
            if self.preset in [PresetType.TIMECODE, PresetType.LOUDNESS]:
                request_type = requests.put

            # Update found preset
            print(f"updating preset {self.value['name']}, id={found_id}", file=sys.stderr)
            ret = make_request(request_type, f"/interface/v2/{route}/{found_id}", self.value)

        return ret

    @staticmethod
    def get_presets(preset_type: PresetType) -> List[dict]:
        """Fetch a list of all existing presets of a specific type.

        Args:
            preset_type (PresetType): The type of presets to retrieve from Coda.

        Raises:
            ValueError: If the API call returns an error, indicating the presets
                could not be fetched.

        Returns:
            List[dict]: A list of dictionaries, where each dictionary represents a preset.

        """
        group_id = ""
        if preset_type in (PresetType.LOUDNESS, PresetType.TIMECODE, PresetType.JOBS, PresetType.WORKFLOWS):
            group_id = validate_group_id()

        route = Preset.routes[preset_type].replace(":group_id", str(group_id))
        ret = make_request(requests.get, f"/interface/v2/{route}")
        j = ret.json()
        if "error" in j:
            raise ValueError(f"Unable to find preset '{preset_type}': {j}")
        return j

    @staticmethod
    def get_group_id_by_name(group_name: str) -> str:
        """Get a group ID by its name.

        Args:
            group_name (str): The name of the group to search for.

        Returns:
            str: The group ID (group_id field).

        Raises:
            ValueError: If no group with the given name is found, or if multiple groups match.

        """
        groups = Preset.get_presets(PresetType.GROUPS)
        matches = [g["group_id"] for g in groups if g["name"] == group_name]

        if len(matches) == 0:
            raise ValueError(f"No group found with name '{group_name}'")
        if len(matches) > 1:
            raise ValueError(f"Multiple groups found with name '{group_name}': {matches}")

        return matches[0]

    @staticmethod
    def get_io_location_id_by_name(io_location_name: str) -> str:
        """Get an IO Location ID by its name. Requires Org Admin/Owner API token.

        Args:
            io_location_name (str): The name of the IO location to search for.

        Returns:
            str: The IO location ID (id field).

        Raises:
            ValueError: If no IO location with the given name is found, or if multiple match.

        """
        io_locations = Preset.get_presets(PresetType.IO_LOCATIONS)
        matches = [loc["id"] for loc in io_locations if loc["name"] == io_location_name]

        if len(matches) == 0:
            raise ValueError(f"No IO location found with name '{io_location_name}'")
        if len(matches) > 1:
            raise ValueError(f"Multiple IO locations found with name '{io_location_name}': {matches}")

        return matches[0]

    @staticmethod
    def get_workflow_by_name(workflow_name: str) -> dict:
        """Get a workflow by its name.

        Args:
            workflow_name (str): The name of the workflow to search for.

        Returns:
            dict: The complete workflow object.

        Raises:
            ValueError: If no workflow with the given name is found, or if multiple match.

        """
        workflows = Preset.get_presets(PresetType.WORKFLOWS)
        matches = [w for w in workflows if w["name"] == workflow_name]

        if len(matches) == 0:
            raise ValueError(f"No workflow found with name '{workflow_name}'")
        if len(matches) > 1:
            raise ValueError(f"Multiple workflows found with name '{workflow_name}': {[w['id'] for w in matches]}")

        return matches[0]

    @staticmethod
    def get_naming_convention_by_name(naming_convention_name: str) -> dict:
        """Get a naming convention by its name.

        Args:
            naming_convention_name (str): The name of the naming convention to search for.

        Returns:
            dict: The complete naming_convention object.

        Raises:
            ValueError: If no naming convention with the given name is found, or if multiple match.

        """
        naming_conventions = Preset.get_presets(PresetType.NAMING)
        matches = [n for n in naming_conventions if n["name"] == naming_convention_name]

        if len(matches) == 0:
            raise ValueError(f"No naming convention found with name '{naming_convention_name}'")
        if len(matches) > 1:
            raise ValueError(f"Multiple naming conventions found with name '{naming_convention_name}': {[n['id'] for n in matches]}")

        return matches[0]["convention_data"]
