import copy
import os
import sys
import requests

from typing import List, Any, Callable, Tuple, Dict
from .enums import Format, FrameRate, InputFilter, InputStemType, PackageType, StemType, PresetType, VenueType
from .preset import Preset
from .utils import is_key_value_comma_string, validate_group_id, make_request, get_channels


_DEFAULT_LOUDNESS_TOLERANCES = {
    "target_program_loudness": [-0.5, 0.4],
    "target_dialog_loudness": [-0.5, 0.4],
    "target_true_peak": [-0.2, 0.0],
}

_IMAX_ENHANCED_FORMAT_MAPPINGS = {
    Format.IMAX12: "5.1.4;mode=imax_enhanced",
    Format.IMAX6: "5.1.1;mode=imax_enhanced",
    Format.IMAX5: "5.1;mode=imax_enhanced",
}

_VALID_IMAX_FORMATS = [
    Format.FIVE_ONE,
    Format.FIVE_ONE_FOUR,
    Format.SEVEN_ONE_FIVE,
    Format.FIVE_ONE_ONE,
    Format.IMAX5,
    Format.IMAX6,
    Format.IMAX12,
]

_DEFAULT_ATMOS_RENDERS = [Format.SEVEN_ONE_FOUR, Format.SEVEN_ONE]

_DME_STEM_MAPPING = {
    "audio/adr": "audio/dx;contents=comp",
    "audio/arch": "audio/dx;contents=comp",
    "audio/audiodescription": "audio/dx;contents=comp",
    "audio/bg": "audio/fx;contents=comp",
    "audio/crd": "audio/fx;contents=comp",
    "audio/dx": "audio/dx;contents=comp",
    # "audio/dx1": "audio/dx;contents=comp",
    # "audio/dx2": "audio/dx;contents=comp",
    # "audio/dxcomp": "audio/dx;contents=comp",
    "audio/fffx": "audio/fx;contents=comp",
    "audio/fix": "audio/fx;contents=comp",
    # "audio/fix1": "audio/fx;contents=comp",
    # "audio/fix2": "audio/fx;contents=comp",
    # "audio/fix3": "audio/fx;contents=comp",
    # "audio/fix4": "audio/fx;contents=comp",
    "audio/fol": "audio/fx;contents=comp",
    # "audio/fol1": "audio/fx;contents=comp",
    # "audio/fol2": "audio/fx;contents=comp",
    "audio/fx": "audio/fx;contents=comp",
    # "audio/fx1": "audio/fx;contents=comp",
    # "audio/fx2": "audio/fx;contents=comp",
    # "audio/fx3": "audio/fx;contents=comp",
    # "audio/fx4": "audio/fx;contents=comp",
    # "audio/fxcomp": "audio/fx;contents=comp",
    "audio/lg": "audio/dx;contents=comp",
    "audio/mnemx": "audio/mx;contents=comp",
    "audio/mx": "audio/mx;contents=comp",
    # "audio/mx1": "audio/mx;contents=comp",
    # "audio/mx2": "audio/mx;contents=comp",
    # "audio/mxcomp": "audio/mx;contents=comp",
    "audio/nar": "audio/dx;contents=comp",
    "audio/pfx": "audio/fx;contents=comp",
    "audio/scr": "audio/mx;contents=comp",
    "audio/sng": "audio/mx;contents=comp",
    "audio/vo": "audio/dx;contents=comp",
    "audio/vox": "audio/dx;contents=comp",
    # "audio/wla": "audio/fx;contents=comp",
}


class WorkflowDefinitionBuilder:
    """Uses the Builder pattern to construct a Coda workflow definition."""

    _SAME_AS_INPUT = "same_as_input"
    _ALL_FROM_ESSENCE = "all_from_essence"

    def __init__(self, name: str) -> None:
        """Initialize the WorkflowBuilder.

        This constructor sets up a new builder with a given name and initializes
        the internal attributes for storing the workflow definition components.

        Args:
            name (str): The name of the workflow.

        """
        self._name: str = name
        self._packages: dict = {}
        self._process_blocks: dict = {}
        self._destinations: dict = {}
        self._wf_params: dict = {}

    def with_group(self, group: str) -> 'WorkflowDefinitionBuilder':
        """Set the CODA_API_GROUP_ID env var based on known group name associated with the CODA_API_TOKEN.

        Args:
            group (str): A known group name or group id which the CODA_API_TOKEN has access to.

        Raises:
            ValueError: If the group ID for the given group name is not found.

        Returns:
            WorkflowDefinitionBuilder: The builder instance for fluent chaining.

        """
        all_groups = Preset.get_presets(PresetType.GROUPS)

        found_group = next((g for g in all_groups if g.get("name") == group or g.get("group_id") == group), None)

        if not found_group or not found_group.get("group_id"):
            raise ValueError(f"Group '{group}' not found.")

        os.environ["CODA_API_GROUP_ID"] = str(found_group["group_id"])

        return self

    def with_parameters(self, params: dict) -> 'WorkflowDefinitionBuilder':
        """Set the workflow-wide parameters.

        Args:
            params (dict): A dictionary of parameters to apply to the workflow.

        Returns:
            WorkflowDefinitionBuilder: The builder instance for fluent chaining.

        """
        self._wf_params = params.copy()
        return self

    def with_process_block(
        self,
        name: str,
        output_venue: VenueType = VenueType.NEARFIELD,
        loudness_preset: dict | str | None = None,
        timecode_preset: dict | str | None = None,
        input_filter: str = InputFilter.ALL_STEMS,
    ) -> 'WorkflowDefinitionBuilder':
        """Add a process block to the workflow.

        Args:
            name (str): The name of the process block.
            output_venue (VenueType, optional): The output venue enum. Defaults to VenueType.NEARFIELD.
            loudness_preset (dict | str, optional): Loudness preset name or definition. Defaults to None.
            timecode_preset (dict | str, optional): Timecode preset name or definition. Defaults to None.
            input_filter (str, optional): The input filter enum to use. Defaults to InputFilter.ALL_STEMS.

        Raises:
            ValueError: If a timecode or loudness preset name is provided but not found.

        Returns:
            WorkflowDefinitionBuilder: The builder instance for fluent chaining.

        """
        if output_venue == VenueType.ALL_FROM_ESSENCE:
            raise ValueError("Output venue cannot be VenueType.ALL_FROM_ESSENCE in process blocks. Use VenueType.SAME_AS_INPUT for dynamic venue selection.")
        if not loudness_preset:
            loudness_preset = {}
        if not timecode_preset:
            timecode_preset = {}

        if isinstance(timecode_preset, str):
            presets = Preset.get_presets(PresetType.TIMECODE)
            pf = [p for p in presets if p["name"] == timecode_preset]
            if not pf:
                raise ValueError(f"Timecode preset '{timecode_preset}' not found.")
            timecode_preset = pf[0]["definition"]

        if isinstance(loudness_preset, str):
            presets = Preset.get_presets(PresetType.LOUDNESS)
            pf = [p for p in presets if p["name"] == loudness_preset]
            if not pf:
                raise ValueError(f"Loudness preset '{loudness_preset}' not found.")
            loudness_preset = pf[0]["definition"]

        if isinstance(loudness_preset, dict) and "tolerances" not in loudness_preset:
            loudness_preset["tolerances"] = _DEFAULT_LOUDNESS_TOLERANCES.copy()
        process_block_config = {
            "name": name,
            "input_filter": input_filter,
            "output_settings": {
                "loudness": loudness_preset,
                "venue": output_venue,
            },
            "output_essences": {},
        }
        if timecode_preset:
            process_block_config["output_settings"]["timecode"] = timecode_preset

        pid = f"my-process-block-{len(self._process_blocks) + 1}"
        self._process_blocks[pid] = process_block_config

        return self

    def with_dcp_package(
        self,
        name: str,
        process_blocks: List[str],
        reels: bool = False,
        naming_convention_preset: str | dict | int | None = None,
        naming_options: str | None = None,
    ) -> 'WorkflowDefinitionBuilder':
        """Add a DCP MXF package to the workflow.

        Args:
            name (str): Name of the package.
            process_blocks (List[str]): List of process block names to connect.
            reels (bool, optional): Enable reel splitting. Defaults to False.
            naming_convention_preset (str | int | dict, optional): Naming convention preset name (str), ID (int),
                or definition (dict). Defaults to None.
            naming_options (str, optional): Comma-separated key-value pairs for the naming convention. Defaults to None.

        Raises:
            ValueError: If venue type is not "theatrical".
            TypeError: If naming_options is not a string.

        Returns:
            WorkflowDefinitionBuilder: The builder instance for fluent chaining.

        """
        if naming_options is not None and \
            (not isinstance(naming_options, str) or not is_key_value_comma_string(naming_options)):
            raise TypeError("naming_options must be a comma-delimited string in KEY=VALUE format.")

        naming_convention_id = None
        naming_convention_dict = None
        if naming_convention_preset:
            naming_convention_id, naming_convention_dict = self._resolve_preset(naming_convention_preset, PresetType.NAMING)

        block_list = self._get_process_block_ids(process_blocks)
        for block_id in block_list:
            block = self._process_blocks[block_id]
            if block["output_settings"]["venue"] != VenueType.THEATRICAL:
                raise ValueError(
                    f"This package type requires a '{VenueType.THEATRICAL}' venue, "
                    f"but the process block '{block['name']}' is set to '{block['output_settings']['venue']}'."
                )
            fps = FrameRate.TWENTY_FOUR
            fmt = [Format.ATMOS]
            typ = [StemType.PRINTMASTER]
            for f in fmt:
                for t in typ:
                    block["output_essences"][f"{t}_{fps}_{f}"] = {
                        "audio_format": f,
                        "frame_rate": fps,
                        "type": t,
                    }

        count = sum(1 for pkg in self._packages.values() if pkg.get("type") == "dcp_mxf")
        pid = f"my-dcp-mxf-package-{count + 1}"

        package_definition = {
            "name": name,
            "process_block_ids": block_list,
            "include_reel_splitting": reels,
        }

        if naming_convention_id:
            package_definition["naming_convention_id"] = naming_convention_id
        if naming_convention_dict:
            package_definition["naming_convention"] = copy.deepcopy(naming_convention_dict)
        if naming_options:
            package_definition["naming_convention_options"] = naming_options

        self._packages[pid] = {"type": PackageType.DCP_MXF, "definition": package_definition}
        return self

    def with_super_session_package(
        self,
        name: str,
        track_definitions: List[Tuple[str, Format, StemType, VenueType]],
        output_frame_rate: FrameRate = FrameRate.ALL_FROM_ESSENCE,
        super_session_preset: str | int | dict[str, Any] | None = None,
        naming_convention_preset: str | int | dict | None = None,
        naming_options: str | None = None,
    ) -> 'WorkflowDefinitionBuilder':
        """Add a Super Session package to the workflow.

        Args:
            name (str): Name of the package.
            track_definitions (List[Tuple[str, Format, StemType, VenueType]]): A list of 4-element tuples,
                where each tuple defines a track configuration as (process_block_name, audio_format, stem_type, venue_type).
                venue_type may only be VenueType.THEATRICAL or VenueType.NEARFIELD.
            output_frame_rate (FrameRate, optional): The output frame rate enum. Defaults to FrameRate.ALL_FROM_ESSENCE.
            super_session_preset (str | int | dict, optional): Super session preset name, ID, or definition. Defaults to None.
            naming_convention_preset (str | int | dict, optional): Naming convention preset name, ID, or definition. Defaults to None.
            naming_options (str, optional): Comma-separated key-value pairs for the naming convention. Defaults to None.

        Raises:
            TypeError: If 'track_definitions' is not a list of 4-element string tuples.
            ValueError: If a process block specified in `track_definitions` is not found,
                or if stem_type or audio_format is set to "all_from_essence", or if venue_type is invalid.

        Returns:
            WorkflowDefinitionBuilder: The builder instance for fluent chaining.

        """
        if naming_options is not None and \
            (not isinstance(naming_options, str) or not is_key_value_comma_string(naming_options)):
            raise TypeError("naming_options must be a comma-delimited string in KEY=VALUE format.")

        if not isinstance(track_definitions, list):
            raise TypeError("The 'track_definitions' parameter must be a list of (process_block_name, audio_format, stem_type) tuples.")

        block_names = []
        for idx, track_tuple in enumerate(track_definitions):
            if not isinstance(track_tuple, tuple) or len(track_tuple) != 4:
                raise TypeError(
                    f"Track configuration at index {idx} must be a tuple of (process_block_name: str, audio_format: Format, stem_type: StemType, venue_type: VenueType), "
                    f"but got {type(track_tuple).__name__} of length {len(track_tuple)}."
                )
            if not all(isinstance(s, str) for s in track_tuple):
                raise TypeError(
                    f"Track configuration at index {idx} must contain only strings."
                )
            block_names.append(track_tuple[0])

        block_list = self._get_process_block_ids(block_names)

        naming_convention_id = None
        naming_convention_dict = None
        super_session_preset_id = None
        super_session_preset_dict = None

        if naming_convention_preset:
            naming_convention_id, naming_convention_dict = self._resolve_preset(naming_convention_preset, PresetType.NAMING)
        if super_session_preset:
            super_session_preset_id, super_session_preset_dict = self._resolve_preset(super_session_preset, PresetType.SUPER_SESSION)

        if super_session_preset_dict is None and super_session_preset_id is None:
            super_session_preset_dict = {
                "session_name_template": "{{TITLE}}_{{FRAME_RATE}}",
                "tracks": [],
            }

        tracks = []
        for idx, (_, audio_format, stem_type, venue_type) in enumerate(track_definitions):
            block_id = block_list[idx]
            block = self._process_blocks[block_id]
            if venue_type not in (VenueType.NEARFIELD, VenueType.THEATRICAL):
                raise ValueError("Venue type must be VenueType.NEARFIELD or VenueType.THEATRICAL only.")
            venue = venue_type
            fr = self._SAME_AS_INPUT if output_frame_rate == self._ALL_FROM_ESSENCE else output_frame_rate
            if audio_format == self._ALL_FROM_ESSENCE:
                raise ValueError(f"Audio format must not be {audio_format}")
            if stem_type == self._ALL_FROM_ESSENCE:
                raise ValueError(f"Stem type must not be {stem_type}")
            block["output_essences"][f"{stem_type}_{fr}_{audio_format}"] = {
                "audio_format": audio_format,
                "frame_rate": fr,
                "type": stem_type,
            }

            track_item = {
                "element": stem_type,
                "format": audio_format,
                "venue": venue
            }

            if venue != VenueType.ALL_FROM_ESSENCE:
                tracks.append(track_item)
            else:
                tracks.append({**track_item, "venue": VenueType.THEATRICAL})
                tracks.append({**track_item, "venue": VenueType.NEARFIELD})

        if isinstance(super_session_preset_dict, dict) and not super_session_preset_dict.get("tracks"):
            expanded_tracks = []
            for track in tracks:
                element = track.get("element")
                if element == StemType.WIDES:
                    stem_list = [InputStemType.DX, InputStemType.FX, InputStemType.MX, InputStemType.VOX, InputStemType.FOL, InputStemType.FIX]
                    for k in stem_list:
                        expanded_tracks.append({"element": k, "format": track["format"], "venue": track["venue"]})
                elif element == StemType.DME:
                    stem_list = [InputStemType.DX, InputStemType.FX, InputStemType.MX]
                    for k in stem_list:
                        expanded_tracks.append({"element": k, "format": track["format"], "venue": track["venue"]})
                elif element == StemType.PRINTMASTER:
                    expanded_tracks.append({"element": InputStemType.PRINTMASTER, "format": track["format"], "venue": track["venue"]})
                else:
                    expanded_tracks.append(track)
            super_session_preset_dict["tracks"] = expanded_tracks

        count = sum(1 for pkg in self._packages.values() if pkg.get("type") == "super_session")
        pid = f"my-super-session-package-{count + 1}"

        package_definition = {
            "name": name,
            "process_block_ids": block_list,
            "frame_rate": output_frame_rate,
        }

        if super_session_preset_id:
            package_definition["super_session_profile_id"] = super_session_preset_id
        if super_session_preset_dict:
            package_definition["super_session_profile"] = super_session_preset_dict
        if naming_convention_id:
            package_definition["naming_convention_id"] = naming_convention_id
        if naming_convention_dict:
            package_definition["naming_convention"] = naming_convention_dict
        if naming_options:
            package_definition["naming_convention_options"] = naming_options

        self._packages[pid] = {"type": PackageType.SUPER_SESSION, "definition": package_definition}
        return self

    def with_multi_mono_reels_package(
        self,
        name: str,
        process_blocks: List[str],
        formats: List[Format] | None = None,
        naming_convention_preset: str | int | dict | None = None,
        naming_options: str | None = None,
    ) -> 'WorkflowDefinitionBuilder':
        """Add a Multi-mono Reels package to the workflow.

        Note:
            You will need to add `with_edits()` in the JobPayloadBuilder to properly set up this package.
                See an example of the dict needed in the JobPayloadBuilder.with_edits() method documentation.

        Args:
            name (str): Name of the package.
            process_blocks (List[str]): List of process block names to connect.
            formats (List[Format] | None, optional): List of formats. Defaults to ["all_from_essence"].
            naming_convention_preset (str | int | dict, optional): Naming convention preset name, ID, or definition. Defaults to None.
            naming_options (str, optional): Comma-separated key-value pairs for the naming convention. Defaults to None.

        Raises:
            ValueError: If the output venue for any connected process block is not 'theatrical'.
            TypeError: If naming_options is not a string.

        Returns:
            WorkflowDefinitionBuilder: The builder instance for fluent chaining.

        """
        if naming_options is not None and \
            (not isinstance(naming_options, str) or not is_key_value_comma_string(naming_options)):
            raise TypeError("naming_options must be a comma-delimited string in KEY=VALUE format.")

        if formats is None:
            formats = [Format.ALL_FROM_ESSENCE]

        naming_convention_id = None
        naming_convention_dict = None
        if naming_convention_preset:
            naming_convention_id, naming_convention_dict = self._resolve_preset(naming_convention_preset, PresetType.NAMING)

        blist = self._get_process_block_ids(process_blocks)
        for block_id in blist:
            block = self._process_blocks[block_id]
            if block["output_settings"]["venue"] != VenueType.THEATRICAL:
                raise ValueError(
                    f"This package type requires a '{VenueType.THEATRICAL}' venue, "
                    f"but the process block '{block['name']}' is set to '{block['output_settings']['venue']}'."
                )
            fps = FrameRate.TWENTY_FOUR
            fmt = formats
            typ = StemType.PRINTMASTER
            for f_original in fmt:
                f = self._SAME_AS_INPUT if f_original == self._ALL_FROM_ESSENCE else f_original
                block["output_essences"][f"{typ}_{fps}_{f}"] = {
                    "audio_format": f,
                    "frame_rate": fps,
                    "type": typ,
                }

        count = sum(1 for pkg in self._packages.values() if pkg.get("type") == "multi_mono_reels")
        pid = f"my-multi-mono-reels-package-{count + 1}"

        package_definition = {
            "name": name,
            "process_block_ids": blist,
            "formats": fmt,
        }

        if naming_convention_id:
            package_definition["naming_convention_id"] = naming_convention_id
        if naming_convention_dict:
            package_definition["naming_convention"] = copy.deepcopy(naming_convention_dict)
        if naming_options:
            package_definition["naming_convention_options"] = naming_options

        self._packages[pid] = {
            "type": PackageType.MULTI_MONO_REELS,
            "definition": package_definition,
        }
        return self

    def with_dolby_encode_package(
        self,
        name: str,
        process_blocks: List[str],
        encoding_preset: str | int | dict,
        output_frame_rate: FrameRate = FrameRate.ALL_FROM_ESSENCE,
        output_format: Format = Format.ALL_FROM_ESSENCE,
        naming_convention_preset: str | int | dict | None = None,
        naming_options: str | None = None,
    ) -> 'WorkflowDefinitionBuilder':
        """Add a Dolby Encode package to the workflow.

        Args:
            name (str): Name of the package.
            process_blocks (List[str]): List of process block names to connect.
            encoding_preset (str | int | dict): Dolby encoding preset name (str), ID (int),
                or definition (dict). Defaults to None.
            output_frame_rate (FrameRate, optional): A FrameRate enum defining the output frame rate.
                Defaults to "all_from_essence"
            output_format (Format, optional): A Format enum defining the output format.
                Defaults to "all_from_essence"
            naming_convention_preset (str | int | dict, optional): Naming convention preset name (str), ID (int),
                or definition (dict). Defaults to None.
            naming_options (str, optional): Comma-separated key-value pairs for the naming convention. Defaults to None.

        Raises:
            TypeError: If the 'essences' parameter is not a tuple with the expected structure of (frame_rate, format),
                or if naming_options is not a string.
            ValueError: If the provided Dolby encoding preset does not support the required format,
                or if the output venue for any connected process block is not 'nearfield'.

        Returns:
            WorkflowDefinitionBuilder: The builder instance for fluent chaining.

        """
        if naming_options is not None and \
            (not isinstance(naming_options, str) or not is_key_value_comma_string(naming_options)):
            raise TypeError("naming_options must be a comma-delimited string in KEY=VALUE format.")

        def format_filter(preset: dict) -> bool:
            return output_format in preset.get("formats", [])

        encode_profile_id, encode_profile_dict = self._resolve_preset(
            encoding_preset, PresetType.DOLBY, filter_lambda=format_filter
        )

        if encode_profile_dict and output_format not in encode_profile_dict.get("formats", []):
            raise ValueError(f"Provided Dolby encode preset definition does not support format '{output_format}'.")

        naming_convention_id = None
        naming_convention_dict = None
        if naming_convention_preset:
            naming_convention_id, naming_convention_dict = self._resolve_preset(naming_convention_preset, PresetType.NAMING)

        blist = self._get_process_block_ids(process_blocks)
        for block_id in blist:
            block = self._process_blocks[block_id]
            if block["output_settings"]["venue"] != VenueType.NEARFIELD:
                raise ValueError(f"Dolby encode packages require a '{VenueType.NEARFIELD}' venue.")
            fmt, typ = output_format, StemType.PRINTMASTER
            fr = self._SAME_AS_INPUT if output_frame_rate == self._ALL_FROM_ESSENCE else output_frame_rate
            block["output_essences"][f"{typ}_{fr}_{fmt}"] = {"audio_format": fmt, "frame_rate": fr, "type": typ}

        count = sum(1 for pkg in self._packages.values() if pkg.get("type") == "dolby")
        pid = f"my-dolby-package-{count + 1}"

        package_definition = {"name": name, "process_block_ids": blist, "format": output_format, "frame_rate": output_frame_rate}

        if encode_profile_id:
            package_definition["encoding_profile_id"] = encode_profile_id
        if encode_profile_dict:
            package_definition["encoding_profile"] = encode_profile_dict
        if naming_convention_id:
            package_definition["naming_convention_id"] = naming_convention_id
        if naming_convention_dict:
            package_definition["naming_convention"] = naming_convention_dict
        if naming_options:
            package_definition["naming_convention_options"] = naming_options

        self._packages[pid] = {
            "type": PackageType.DOLBY,
            "definition": package_definition,
        }

        return self

    def with_dts_encode_package(
        self,
        name: str,
        process_blocks: List[str],
        encoding_preset: str | int | dict,
        output_frame_rate: FrameRate = FrameRate.ALL_FROM_ESSENCE,
        output_format: Format = Format.ALL_FROM_ESSENCE,
        naming_convention_preset: str | int | dict | None = None,
        naming_options: str | None = None,
        is_imax_enhanced: bool = False,
    ) -> 'WorkflowDefinitionBuilder':
        """Add a DTS or IMAX Enhanced package to the workflow.

        Args:
            name (str): Name of the package.
            process_blocks (List[str]): List of process block names to connect.
            encoding_preset (str | int | dict): DTS encoding preset name (str), ID (int),
                or definition (dict).
            output_frame_rate (FrameRate, optional): A FrameRate enum defining the output frame rate.
                Defaults to "all_from_essence"
            output_format (Format, optional): A Format enum defining the output format.
                Defaults to "all_from_essence"
            naming_convention_preset (str | int | dict, optional): Naming convention preset name (str), ID (int),
                or definition (dict). Defaults to None.
            naming_options (str, optional): Comma-separated key-value pairs for the naming convention. Defaults to None.
            is_imax_enhanced (bool, optional): Flag for IMAX enhanced package type. Defaults to False.

        Raises:
            TypeError: If naming_options is not a string in the correct format.
            ValueError: If the provided DTS encoding preset does not support the required format,
                or if the output venue for any connected process block is not 'nearfield'.

        Returns:
            WorkflowDefinitionBuilder: The builder instance for fluent chaining.

        """
        if naming_options is not None and \
            (not isinstance(naming_options, str) or not is_key_value_comma_string(naming_options)):
            raise TypeError("naming_options must be a comma-delimited string in KEY=VALUE format.")

        def format_filter(preset: dict) -> bool:
            return output_format in preset.get("formats", [])

        encode_profile_id, encode_profile_dict = self._resolve_preset(
            encoding_preset, PresetType.DTS, filter_lambda=format_filter
        )

        t1cc = False
        if encode_profile_dict:
            t1cc = encode_profile_dict.get("t1cc", False)
        elif encode_profile_id:
            presets = Preset.get_presets(PresetType.DTS)
            pf = [p for p in presets if p.get("encoding_preset_id") == encode_profile_id]
            if pf:
                t1cc = pf[0].get("definition", {}).get("t1cc", False)

        naming_convention_id = None
        naming_convention_dict = None
        if naming_convention_preset:
            naming_convention_id, naming_convention_dict = self._resolve_preset(naming_convention_preset, PresetType.NAMING)

        blist = self._get_process_block_ids(process_blocks)

        for block_id in blist:
            block = self._process_blocks[block_id]
            if block["output_settings"]["venue"] != VenueType.NEARFIELD:
                raise ValueError(f"DTS encode packages require a '{VenueType.NEARFIELD}' venue.")

            f_original, st = output_format, StemType.PRINTMASTER
            if t1cc and f_original != Format.ALL_FROM_ESSENCE and "imax" not in f_original:
                f_original += ";mode=imax_enhanced"

            fr = self._SAME_AS_INPUT if output_frame_rate == self._ALL_FROM_ESSENCE else output_frame_rate
            f = self._SAME_AS_INPUT if f_original == self._ALL_FROM_ESSENCE else f_original

            block["output_essences"][f"{st}_{fr}_{f.replace(';', '_').replace('=', '_')}"] = {"audio_format": f, "frame_rate": fr, "type": st}

        packtype = PackageType.IMAX_ENHANCED if is_imax_enhanced or t1cc else PackageType.DTS

        count = sum(1 for pkg in self._packages.values() if pkg.get("type") == packtype)
        pid = f"my-{packtype.replace('_', '-')}-package-{count + 1}"

        pfmt = output_format
        if pfmt in _IMAX_ENHANCED_FORMAT_MAPPINGS:
            pfmt = _IMAX_ENHANCED_FORMAT_MAPPINGS[pfmt]

        package_definition = {"name": name, "process_block_ids": blist, "format": pfmt, "frame_rate": output_frame_rate}

        if encode_profile_id:
            package_definition["encoding_profile_id"] = encode_profile_id
        if encode_profile_dict:
            package_definition["encoding_profile"] = encode_profile_dict
        if naming_convention_id:
            package_definition["naming_convention_id"] = naming_convention_id
        if naming_convention_dict:
            package_definition["naming_convention"] = naming_convention_dict
        if naming_options:
            package_definition["naming_convention_options"] = naming_options

        self._packages[pid] = {
            "type": packtype,
            "definition": package_definition,
        }

        return self

    def with_imax_enhanced_encode_package(
        self,
        name: str,
        process_blocks: List[str],
        encoding_preset: str | int | dict,
        output_frame_rate: FrameRate = FrameRate.ALL_FROM_ESSENCE,
        output_format: Format = Format.ALL_FROM_ESSENCE,
        naming_convention_preset: str | int | dict | None = None,
        naming_options: str | None = None,
    ) -> 'WorkflowDefinitionBuilder':
        """Add an IMAX Enhanced package, a specific type of DTS package.

        Args:
            name (str): Name of the package.
            process_blocks (List[str]): List of process block names to connect.
            encoding_preset (str | int | dict): Dolby encoding preset name (str), ID (int),
                or definition (dict). Defaults to None.
            output_frame_rate (FrameRate, optional): A FrameRate enum defining the output frame rate.
                Defaults to "all_from_essence"
            output_format (Format, optional): A Format enum defining the output format.
                Defaults to "all_from_essence"
            naming_convention_preset (str | int | dict, optional): Naming convention preset name (str), ID (int),
                or definition (dict). Defaults to None.
            naming_options (str, optional): Comma-separated key-value pairs for the naming convention. Defaults to None.

        Raises:
            TypeError: If the 'essences' parameter is not a tuple with the expected structure of (frame_rate, format),
                or if naming_options is not a string.
            ValueError: If the format provided in 'essences' is not a valid IMAX Enhanced format.

        Returns:
            WorkflowDefinitionBuilder: The builder instance for fluent chaining.

        """
        if naming_options is not None and \
            (not isinstance(naming_options, str) or not is_key_value_comma_string(naming_options)):
            raise TypeError("naming_options must be a comma-delimited string in KEY=VALUE format.")

        if output_format not in _VALID_IMAX_FORMATS:
            raise ValueError(
                f"Format '{output_format}' is not valid for IMAX Enhanced packages. "
                f"Valid formats are: {', '.join(_VALID_IMAX_FORMATS)}"
            )

        return self.with_dts_encode_package(
            name,
            process_blocks,
            encoding_preset,
            output_frame_rate,
            output_format,
            naming_convention_preset,
            naming_options,
            is_imax_enhanced=True,
        )

    def with_interleaved_package(
        self,
        name: str,
        process_blocks: List[str],
        output_frame_rate: FrameRate = FrameRate.ALL_FROM_ESSENCE,
        output_formats: List[Format] | None = None,
        output_stem_types: List[StemType] | None = None,
        streams: List[Dict[str, str]] | None = None,
        naming_convention_preset: str | int | dict | None = None,
        naming_options: str | None = None,
    ) -> 'WorkflowDefinitionBuilder':
        """Add an Interleaved WAV package to the workflow.

        Args:
            name (str): Name of the package.
            process_blocks (List[str]): List of process block names to connect.
            output_frame_rate (FrameRate, optional): A FrameRate enum defining the output frame rate.
                Defaults to "all_from_essence"
            output_formats (List[Format], optional): A list defining output formats.
                Defaults to "all_from_essence"
            output_stem_types (List[StemType], optional): A list defining output stem types.
                Defaults to "all_from_essence"
            streams (List[Dict[str, str]] | None) A list of interleaved channels mapping order for the streams.
                If None, it's auto-generated. Defaults to None.
                The Dict should be structured as: `{"format": str, "element": str, "channel": str}`.
                The list for example should look like this:
                `[{"format": "2.0", "element": "audio/pm", "channel": "L"}, {"format": "2.0", "element": "audio/pm", "channel": "R"}]`.
            naming_convention_preset (str | int | dict, optional): Naming convention preset name (str), ID (int),
                or definition (dict). Defaults to None.
            naming_options (str, optional): Comma-separated key-value pairs for the naming convention.
                Defaults to None.

        Raises:
            TypeError: If the 'essences' parameter is not a tuple with the expected
                structure of (frame_rate, [formats], [types]), or if naming_options is not a string.

        Returns:
            WorkflowDefinitionBuilder: The builder instance for fluent chaining.

        """
        if output_formats is None:
            output_formats = [Format.ALL_FROM_ESSENCE]
        if output_stem_types is None:
            output_stem_types = [StemType.ALL_FROM_ESSENCE]
        if naming_options is not None and \
            (not isinstance(naming_options, str) or not is_key_value_comma_string(naming_options)):
            raise TypeError("naming_options must be a comma-delimited string in KEY=VALUE format.")

        naming_convention_id = None
        naming_convention_dict = None
        if naming_convention_preset:
            naming_convention_id, naming_convention_dict = self._resolve_preset(naming_convention_preset, PresetType.NAMING)

        blist = self._get_process_block_ids(process_blocks)
        for block_id in blist:
            block = self._process_blocks[block_id]
            for f_original in output_formats:
                for st_original in output_stem_types:
                    fr = self._SAME_AS_INPUT if output_frame_rate == self._ALL_FROM_ESSENCE else output_frame_rate
                    f = self._SAME_AS_INPUT if f_original == self._ALL_FROM_ESSENCE else f_original
                    st = self._SAME_AS_INPUT if st_original == self._ALL_FROM_ESSENCE else st_original
                    block["output_essences"][f"{st}_{fr}_{f}"] = {
                        "audio_format": f,
                        "frame_rate": fr,
                        "type": st,
                    }

        if not streams:
            streams = []
            for st_original in sorted(output_stem_types):
                for f in output_formats:
                    if st_original == StemType.DME:
                        elements = ["audio/pm"]
                    if st_original == StemType.PRINTMASTER:
                        elements = ['audio/dx', 'audio/fx', 'audio/mx']
                    channels = get_channels(f)
                    if channels:
                        for e in elements:
                            for ch in channels:
                                streams.append({"format": f, "element": e, "channel": ch})

        count = sum(1 for pkg in self._packages.values() if pkg.get("type") == PackageType.INTERLEAVED)
        pid = f"my-interleaved-package-{count + 1}"

        package_definition = {
            "name": name,
            "frame_rate": output_frame_rate,
            "process_block_ids": blist,
            "streams": streams,
        }

        if naming_convention_id:
            package_definition["naming_convention_id"] = naming_convention_id
        if naming_convention_dict:
            package_definition["naming_convention"] = copy.deepcopy(naming_convention_dict)
        if naming_options:
            package_definition["naming_convention_options"] = naming_options

        self._packages[pid] = {"type": PackageType.INTERLEAVED, "definition": package_definition}

        return self

    def with_mov_package(
        self,
        name: str,
        process_blocks: List[str],
        output_frame_rate: FrameRate = FrameRate.ALL_FROM_ESSENCE,
        output_formats: List[Format] | None = None,
        output_stem_types: List[StemType] | None = None,
        streams: List[Dict[str, str]] | None = None,
        naming_convention_preset: str | int | dict | None = None,
        naming_options: str | None = None,
    ) -> 'WorkflowDefinitionBuilder':
        """Add a MOV package to the workflow.

        Args:
            name (str): Name of the package.
            process_blocks (List[str]): List of process block names to connect.
            output_frame_rate (FrameRate, optional): A FrameRate enum defining the output frame rate.
                Defaults to "all_from_essence"
            output_formats (List[Format], optional): A list defining output formats.
                Defaults to "all_from_essence"
            output_stem_types (List[StemType], optional): A list defining output stem types.
                Defaults to "all_from_essence"
            streams (List[Dict[str, str]] | None) A list of interleaved channels mapping order for the streams.
                If None, it's auto-generated. Defaults to None.
                The Dict should be structured as: `{"format": str, "element": str, "channel": str}`.
                The list for example should look like this:
                `[{"format": "2.0", "element": "audio/pm", "channel": "L"}, {"format": "2.0", "element": "audio/pm", "channel": "R"}]`.
            naming_convention_preset (str | int | dict, optional): Naming convention preset name (str), ID (int),
                or definition (dict). Defaults to None.
            naming_options (str, optional): Comma-separated key-value pairs for the naming convention.
                Defaults to None.

        Raises:
            TypeError: If the 'essences' parameter is not a tuple with the expected
                structure of (frame_rate, [formats], [types]), or if naming_options is not a string.

        Returns:
            WorkflowDefinitionBuilder: The builder instance for fluent chaining.

        """
        if output_formats is None:
            output_formats = [Format.ALL_FROM_ESSENCE]
        if output_stem_types is None:
            output_stem_types = [StemType.ALL_FROM_ESSENCE]
        if naming_options is not None and \
            (not isinstance(naming_options, str) or not is_key_value_comma_string(naming_options)):
            raise TypeError("naming_options must be a comma-delimited string in KEY=VALUE format.")

        naming_convention_id = None
        naming_convention_dict = None
        if naming_convention_preset:
            naming_convention_id, naming_convention_dict = self._resolve_preset(naming_convention_preset, PresetType.NAMING)

        blist = self._get_process_block_ids(process_blocks)
        for block_id in blist:
            block = self._process_blocks[block_id]
            for f_original in output_formats:
                for st_original in output_stem_types:
                    fr = self._SAME_AS_INPUT if output_frame_rate == self._ALL_FROM_ESSENCE else output_frame_rate
                    f = self._SAME_AS_INPUT if f_original == self._ALL_FROM_ESSENCE else f_original
                    st = self._SAME_AS_INPUT if st_original == self._ALL_FROM_ESSENCE else st_original
                    block["output_essences"][f"{st}_{fr}_{f}"] = {
                        "audio_format": f,
                        "frame_rate": fr,
                        "type": st,
                    }

        if not streams:
            streams = []
            for st_original in sorted(output_stem_types):
                for f in output_formats:
                    if st_original == StemType.DME:
                        elements = ["audio/pm"]
                    if st_original == StemType.PRINTMASTER:
                        elements = ['audio/dx', 'audio/fx', 'audio/mx']
                    channels = get_channels(f)
                    if channels:
                        for e in elements:
                            for ch in channels:
                                streams.append({"format": f, "element": e, "channel": ch})

        count = sum(1 for pkg in self._packages.values() if pkg.get("type") == PackageType.MOV)
        pid = f"my-mov-package-{count + 1}"

        package_definition = {
            "name": name,
            "frame_rate": output_frame_rate,
            "process_block_ids": blist,
            "streams": streams,
        }

        if naming_convention_id:
            package_definition["naming_convention_id"] = naming_convention_id
        if naming_convention_dict:
            package_definition["naming_convention"] = copy.deepcopy(naming_convention_dict)
        if naming_options:
            package_definition["naming_convention_options"] = naming_options

        self._packages[pid] = {"type": PackageType.MOV, "definition": package_definition}

        return self

    def with_multi_mono_package(
        self,
        name: str,
        process_blocks: List[str],
        output_frame_rates: List[FrameRate] | None = None,
        output_formats: List[Format] | None = None,
        output_stem_types: List[StemType] | None = None,
        naming_convention_preset: str | int | dict | None = None,
        naming_options: str | None = None,
        include_pt_session: bool = False,
    ) -> 'WorkflowDefinitionBuilder':
        """Add a Multi-mono WAV package to the workflow.

        Args:
            name (str): Name of the package.
            process_blocks (List[str]): List of process block names to connect.
            output_frame_rates (List[FrameRate], optional): A list defining output frame rates.
                Defaults to "all_from_essence"
            output_formats (List[Format], optional): A list defining output formats.
                Defaults to "all_from_essence"
            output_stem_types (List[StemType], optional): A list defining output stem types.
                Defaults to "all_from_essence"
            naming_convention_preset (str | int | dict, optional): Naming convention preset name (str), ID (int),
                or definition (dict). Defaults to None.
            naming_options (str, optional): Comma-separated key-value pairs for the naming convention. Defaults to None.
            include_pt_session (bool, optional): Whether to include a Pro Tools session. Defaults to False.

        Raises:
            TypeError: If the 'naming_options' parameter is set and not a comma-delimeted string.

        Returns:
            WorkflowDefinitionBuilder: The builder instance for fluent chaining.

        """
        if output_frame_rates is None:
            output_frame_rates = [FrameRate.ALL_FROM_ESSENCE]
        if output_formats is None:
            output_formats = [Format.ALL_FROM_ESSENCE]
        if output_stem_types is None:
            output_stem_types = [StemType.ALL_FROM_ESSENCE]
        if naming_options is not None and \
            (not isinstance(naming_options, str) or not is_key_value_comma_string(naming_options)):
            raise TypeError("naming_options must be a comma-delimited string in KEY=VALUE format.")

        naming_convention_id = None
        naming_convention_dict = None
        if naming_convention_preset:
            naming_convention_id, naming_convention_dict = self._resolve_preset(naming_convention_preset, PresetType.NAMING)

        blist = self._get_process_block_ids(process_blocks)
        venues = []
        for block_id in blist:
            block = self._process_blocks[block_id]
            venue_type = block.get("output_settings").get("venue")
            venue = self._ALL_FROM_ESSENCE if venue_type == self._SAME_AS_INPUT else venue_type
            venues.append(venue)

            for fr_original in output_frame_rates:
                for f_original in output_formats:
                    for t_original in output_stem_types:
                        fr = self._SAME_AS_INPUT if fr_original == self._ALL_FROM_ESSENCE else fr_original
                        f = self._SAME_AS_INPUT if f_original == self._ALL_FROM_ESSENCE else f_original
                        t = self._SAME_AS_INPUT if t_original == self._ALL_FROM_ESSENCE else t_original
                        block["output_essences"][f"{t}_{fr}_{f}"] = {
                            "audio_format": f,
                            "frame_rate": fr,
                            "type": t,
                        }

        count = sum(1 for pkg in self._packages.values() if pkg.get("type") == "multi_mono")
        pid = f"my-multi-mono-package-{count + 1}"

        package_definition = {
            "name": name,
            "frame_rates": output_frame_rates,
            "formats": output_formats,
            "elements": output_stem_types,
            "venues": list(set(venues)),
            "process_block_ids": blist,
            "include_pro_tools_session": include_pt_session,
        }

        if naming_convention_id:
            package_definition["naming_convention_id"] = naming_convention_id
        if naming_convention_dict:
            package_definition["naming_convention"] = copy.deepcopy(naming_convention_dict)
        if naming_options:
            package_definition["naming_convention_options"] = naming_options

        self._packages[pid] = {"type": PackageType.MULTI_MONO, "definition": package_definition}
        return self

    def with_adm_package(
        self,
        name: str,
        process_blocks: List[str],
        output_frame_rate: FrameRate = FrameRate.ALL_FROM_ESSENCE,
        output_stem_type: StemType = StemType.ALL_FROM_ESSENCE,
        naming_convention_preset: str | int | dict | None = None,
        naming_options: str | None = None,
    ) -> 'WorkflowDefinitionBuilder':
        """Add an ADM (Atmos) package to the workflow.

        Args:
            name (str): Name of the package.
            process_blocks (List[str]): List of process block names. Must contain exactly one.
            output_frame_rate (FrameRate, optional): A FrameRate enum defining the output frame rate.
                Defaults to "all_from_essence"
            output_stem_type (StemType, optional): A StemType enum defining the output stem type.
                Defaults to "all_from_essence"
            naming_convention_preset (str | int | dict, optional): Naming convention preset name (str), ID (int),
                or definition (dict). Defaults to None.
            naming_options (str, optional): Comma-separated key-value pairs for the naming convention. Defaults to None.

        Raises:
            TypeError: If the 'essences' parameter is not a tuple with the
                expected structure of (frame_rate, element_type), or if naming_options is not a string.
            ValueError: If the number of process blocks provided is not exactly one.

        Returns:
            WorkflowDefinitionBuilder: The builder instance for fluent chaining.

        """
        if naming_options is not None and \
            (not isinstance(naming_options, str) or not is_key_value_comma_string(naming_options)):
            raise TypeError("naming_options must be a comma-delimited string in KEY=VALUE format.")
        if len(process_blocks) != 1:
            raise ValueError("ADM packages require exactly one process block.")

        naming_convention_id = None
        naming_convention_dict = None
        if naming_convention_preset:
            naming_convention_id, naming_convention_dict = self._resolve_preset(naming_convention_preset, PresetType.NAMING)

        blist = self._get_process_block_ids(process_blocks)
        venues = []

        for block_id in blist:
            block = self._process_blocks[block_id]
            venue_type = block.get("output_settings").get("venue")
            venue = self._ALL_FROM_ESSENCE if venue_type == self._SAME_AS_INPUT else venue_type
            venues.append(venue)

            fmt = Format.ATMOS
            fr = self._SAME_AS_INPUT if output_frame_rate == self._ALL_FROM_ESSENCE else output_frame_rate
            st = self._SAME_AS_INPUT if output_stem_type == self._ALL_FROM_ESSENCE else output_stem_type
            block["output_essences"][f"{st}_{fr}_{fmt}"] = {
                "audio_format": fmt,
                "frame_rate": fr,
                "type": st,
            }

        count = sum(1 for pkg in self._packages.values() if pkg.get("type") == "adm")
        pid = f"my-adm-package-{count + 1}"

        package_definition = {
            "name": name,
            "frame_rate": output_frame_rate,
            "format": Format.ATMOS,
            "element": output_stem_type,
            "venue": venues[0],
            "process_block_ids": blist,
        }

        if naming_convention_id:
            package_definition["naming_convention_id"] = naming_convention_id
        if naming_convention_dict:
            package_definition["naming_convention"] = naming_convention_dict
        if naming_options:
            package_definition["naming_convention_options"] = naming_options

        self._packages[pid] = {
            "type": PackageType.ADM,
            "definition": package_definition,
        }

        return self

    def with_destination(self, name: str, io_location_id: str | None = None, s3_url: str | None = None, s3_auth: dict | None = None, options: dict | None = None) -> 'WorkflowDefinitionBuilder':
        """Add a destination node to the workflow.

        Args:
            name (str): A unique name for the destination.
            io_location_id (str): The ULID of a desired IO Location. Defaults to None.
            s3_url (str): The URL of the S3 destination (e.g., "s3://..."). Defaults to None.
            s3_auth (dict, optional): Authentication details. Defaults to None.
            options (dict, optional): URL options. Defaults to None.

        Returns:
            WorkflowDefinitionBuilder: The builder instance for fluent chaining.

        Raises:
            ValueError: If either io_location or s3_url is not supplied.
            ValueError: If both io_location and s3_url is supplied.

        """
        if s3_url is None and io_location_id is None:
            raise ValueError("Either an 'io_location_id' or 's3_url' must be supplied")

        if s3_url is not None and io_location_id is not None:
            raise ValueError("Either an 'io_location_id' or 's3_url' must be supplied, not both.")

        dest_def: dict[str, Any] = {"package_ids": []}
        if s3_url is not None and io_location_id is None:
            dest_type = "s3"
            dest_def["url"] = s3_url
            if s3_auth:
                dest_def["auth"] = s3_auth
            if options:
                dest_def["url_options"] = options

        if io_location_id is not None and s3_url is None:
            dest_type = "io_location"
            dest_def["io_location_id"] = io_location_id

        self._destinations[name] = {"type": dest_type, "definition": dest_def}
        return self

    def with_packages_sent_to_destination(self, dest_name: str, package_names: List[str]) -> 'WorkflowDefinitionBuilder':
        """Connect packages to a destination.

        Args:
            dest_name (str): The name of the destination to send packages to.
            package_names (List[str]): A list of package names to connect.

        Raises:
            ValueError: If the destination or any package is not found.

        Returns:
            WorkflowDefinitionBuilder: The builder instance for fluent chaining.

        """
        if dest_name not in self._destinations:
            raise ValueError(f"Destination '{dest_name}' not found in workflow.")

        package_ids = self._get_package_ids(package_names)
        self._destinations[dest_name]["definition"]["package_ids"].extend(package_ids)
        return self

    def get_package_list(self) -> List[dict]:
        """Return a flattened list of all packages in the workflow.

        Each item in the list is a dictionary containing the package's
        definition, its type, and its unique ID within the workflow.

        Returns:
            List[dict]: A list of package dictionaries.

        """
        package_list = []
        if not self._packages:
            return package_list

        for pid, pdata in self._packages.items():
            # Create a copy of the main definition
            package_info = copy.deepcopy(pdata.get("definition", {}))

            # Add the type and id for easy access
            package_info["type"] = pdata.get("type")
            package_info["id"] = pid

            package_list.append(package_info)

        return package_list

    def build(self) -> 'WorkflowDefinition':
        """Construct and return the final Workflow object.

        Returns:
            WorkflowDefinition: A new Workflow instance containing the built definition.

        """
        definition = {
            "name": self._name,
            "process_blocks": copy.deepcopy(self._process_blocks),
            "packages": copy.deepcopy(self._packages),
            "destinations": copy.deepcopy(self._destinations) or {},
            "workflow_parameters": self._get_default_workflow_params()
        }
        for k, v in self._wf_params.items():
            definition["workflow_parameters"][k] = v

        return WorkflowDefinition(definition)

    def _resolve_preset(
        self,
        preset_value: str | int | dict[str, Any],
        preset_type: PresetType,
        filter_lambda: Callable[[dict], bool] | None = None,
    ) -> tuple[int | None, dict | None]:
        """Resolve a preset from various input types.

        This helper method takes a preset identifier and fetches the corresponding
        preset data. The identifier can be a string (preset name), an integer
        (preset ID), or a dictionary (a direct definition). It can also apply
        an additional filter function when resolving by name.

        Args:
            preset_value (Any): The preset identifier (str, int, or dict).
            preset_type (PresetType): The type of preset to resolve.
            filter_lambda (Callable[[dict], bool], optional): A function to
                additionally filter presets when resolving by name. Defaults to None.

        Raises:
            ValueError: If a preset name is not found or is not unique.

        Returns:
            tuple[int | None, dict | None]: A tuple of (preset_id, preset_dict).

        """
        preset_id = None
        preset_dict = None

        key_map = {
            PresetType.NAMING: "id",
            PresetType.SUPER_SESSION: "super_session_preset_id",
            PresetType.DOLBY: "encoding_preset_id",
            PresetType.DTS: "encoding_preset_id",
            PresetType.LOUDNESS: "loudness_preset_id",
            PresetType.TIMECODE: "timecode_preset_id",
        }

        if isinstance(preset_value, str):
            presets = Preset.get_presets(preset_type)
            if not presets:
                raise ValueError(f"No presets of type '{preset_type.value}' found.")

            if filter_lambda:
                presets = [p for p in presets if filter_lambda(p)]
            pf = [p for p in presets if p.get("name") == preset_value]
            if not pf:
                raise ValueError(f"{preset_type.value.capitalize()} preset '{preset_value}' not found or did not match filter criteria.")
            if len(pf) > 1:
                raise ValueError(f"Multiple {preset_type.value} presets found with name '{preset_value}'.")

            preset_id = int(pf[0][key_map[preset_type]])

        elif isinstance(preset_value, int):
            presets = Preset.get_presets(preset_type)
            if not presets:
                raise ValueError(f"No presets of type '{preset_type.value}' found.")

            pf = [p for p in presets if p.get(key_map[preset_type]) == preset_value]
            if not pf:
                raise ValueError(f"{preset_type.value.capitalize()} preset '{preset_value}' not found or did not match filter criteria.")

            preset_id = preset_value

        elif isinstance(preset_value, dict):
            preset_dict = copy.deepcopy(preset_value)
        return preset_id, preset_dict

    def _get_process_block_ids(self, block_names: List[str]) -> List[str]:
        ids = []
        for name in block_names:
            found_id = next((pid for pid, pdata in self._process_blocks.items() if pdata["name"] == name), None)
            if not found_id:
                raise ValueError(f"Process block '{name}' not found in workflow.")
            ids.append(found_id)
        return ids

    def _get_package_ids(self, package_names: List[str]) -> List[str]:
        ids = []
        for name in package_names:
            found_id = next((pid for pid, pdata in self._packages.items() if pdata.get("definition", {}).get("name") == name), None)
            if not found_id:
                raise ValueError(f"Package '{name}' not found in workflow.")
            ids.append(found_id)
        return ids

    def _get_default_workflow_params(self) -> dict:
        return {
            "dme_stem_mapping": _DME_STEM_MAPPING.copy(),
            "enable_atmos_renders": _DEFAULT_ATMOS_RENDERS.copy(),
        }


class WorkflowDefinition:
    """Represents a finalized Coda workflow definition."""

    def __init__(self, definition: dict) -> None:
        """Initialize the Workflow object.

        Args:
            definition (dict): A complete workflow definition payload.

        Raises:
            ValueError: If the provided definition is empty or missing a 'name' key.

        """
        if not definition or "name" not in definition:
            raise ValueError("Cannot initialize Workflow with an invalid definition.")
        self.definition = definition
        self.name = definition["name"]

    def dict(self) -> dict:
        """Return the workflow definition as a dictionary.

        Returns:
            dict: The complete workflow definition payload.

        """
        return self.definition

    @staticmethod
    def from_preset(preset_name: str | None = None, preset_id: str | None = None) -> 'WorkflowDefinition':
        """Create a Workflow instance by importing a saved preset.

        Args:
            preset_name (str, optional): The name of the workflow preset to import. Defaults to None.
            preset_id (str, optional): The id of the workflow preset to import. Defaults to None.

        Raises:
            ValueError: If the preset cannot be found.

        Returns:
            WorkflowDefinition: A new Workflow instance based on the preset.

        """
        if preset_name is None and preset_id is None:
            raise ValueError("`preset_name` or `preset_id` must be supplied")

        wf_presets = Preset.get_presets(PresetType.WORKFLOWS)
        for j in wf_presets:
            if preset_name is not None and j["name"] == preset_name:
                return WorkflowDefinition(j["definition"])
            if preset_id is not None and j["workflow_id"] == preset_id:
                return WorkflowDefinition(j["definition"])

        raise ValueError("Unable to find workflow preset")

    @staticmethod
    def from_job(job_id: int, use_mne_definition: bool = False) -> 'WorkflowDefinition':
        """Create a Workflow instance from a completed job.

        Args:
            job_id (int): The ID of the completed job to import from.
            use_mne_definition (bool, optional): Whether to use the M&E workflow. Defaults to False.

        Raises:
            ValueError: If the job to import from is not in a 'COMPLETED' state.

        Returns:
            WorkflowDefinition: A new Workflow instance based on the job.

        """
        group_id = validate_group_id()
        print(f"importing workflow from job {job_id}", file=sys.stderr)
        ret = make_request(
            requests.get, f"/interface/v2/groups/{group_id}/jobs/{job_id}"
        )
        j = ret.json()

        if j.get("status") != "COMPLETED":
            raise ValueError(
                f"Cannot import workflow from job {job_id} because its status is '{j.get('status')}'. "
                "The job must be 'COMPLETED'."
            )

        wf_def_key = "mne_workflow_definition" if use_mne_definition and "mne_workflow_definition" in j else "workflow_definition"
        if use_mne_definition and wf_def_key == "workflow_definition":
            print("** WARNING ** Mne workflow definition was not found. using normal workflow", file=sys.stderr)

        return WorkflowDefinition(j[wf_def_key])
