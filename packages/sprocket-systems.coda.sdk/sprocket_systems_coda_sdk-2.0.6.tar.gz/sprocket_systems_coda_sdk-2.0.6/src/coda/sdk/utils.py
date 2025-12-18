import os
import requests
import re
import urllib3

from typing import TYPE_CHECKING, List, Dict, Any, Callable

from .constants import (
    ENV_CODA_API_GROUP_ID,
    ENV_CODA_API_URL,
    ENV_CODA_API_TOKEN,
    ENV_CODA_API_INSECURE_SKIP_VERIFY,
    DEFAULT_API_URL,
    INSECURE_SKIP_VERIFY_VALUES,
)

if TYPE_CHECKING:
    from ..tc_tools import (
        time_seconds_to_vid_frames,
        vid_frames_to_tc,
        tc_to_time_seconds,
    )

_CHANNEL_CONFIGURATIONS: dict = {
    "MONO": ["C"],
    "2.0": ["L", "R"],
    "3.0": ["L", "C", "R"],
    "LCRS": ["L", "C", "R", "S"],
    "5.0": ["L", "C", "R", "Ls", "Rs"],
    "5.0.2": ["L", "C", "R", "Ls", "Rs", "Ltm", "Rtm"],
    "7.0": ["L", "C", "R", "Lss", "Rss", "Lsr", "Rsr"],
    "7.1": ["L", "R", "C", "LFE", "Lss", "Rss", "Lsr", "Rsr"],
    "5.1": ["L", "R", "C", "LFE", "Ls", "Rs"],
    "5.1.2": ["L", "C", "R", "Ls", "Rs", "Ltm", "Rtm", "LFE"],
    "5.0.4": ["L", "C", "R", "Ls", "Rs", "Ltf", "Rtf", "Ltr", "Rtr"],
    "7.0.2": ["L", "C", "R", "Lss", "Rss", "Lsr", "Rsr", "Lts", "Rts"],
    "5.1.4": ["L", "C", "R", "Ls", "Rs", "Ltf", "Rtf", "Ltr", "Rtr", "LFE"],
    "7.1.2": ["L", "C", "R", "Lss", "Rss", "Lsr", "Rsr", "Lts", "Rts", "LFE"],
    "7.0.4": ["L", "C", "R", "Lss", "Rss", "Lsr", "Rsr", "Ltf", "Rtf", "Ltr", "Rtr"],
    "7.1.4": ["L", "C", "R", "Lss", "Rss", "Lsr", "Rsr", "Ltf", "Rtf", "Ltr", "Rtr", "LFE"],
    "7.0.6": ["L", "C", "R", "Lss", "Rss", "Lsr", "Rsr", "Ltf", "Rtf", "Ltm", "Rtm", "Ltr", "Rtr"],
    "9.0.4": ["L", "C", "R", "Lss", "Rss", "Lsr", "Rsr", "Ltf", "Rtf", "Ltr", "Rtr", "Lw", "Rw"],
    "7.1.6": ["L", "C", "R", "Lss", "Rss", "Lsr", "Rsr", "Ltf", "Rtf", "Ltm", "Rtm", "Ltr", "Rtr", "LFE"],
    "9.1.4": ["L", "C", "R", "Lss", "Rss", "Lsr", "Rsr", "Ltf", "Rtf", "Ltr", "Rtr", "Lw", "Rw", "LFE"],
    "9.0.6": ["L", "C", "R", "Lss", "Rss", "Lsr", "Rsr", "Ltf", "Rtf", "Ltm", "Rtm", "Ltr", "Rtr", "Lw", "Rw"],
    "9.1.6": ["L", "C", "R", "Lss", "Rss", "Lsr", "Rsr", "Ltf", "Rtf", "Ltm", "Rtm", "Ltr", "Rtr", "Lw", "Rw", "LFE"],
    "IMAX5": ["L", "C", "R", "Ls", "Rs"],
    "IMAX6": ["L", "C", "R", "Ls", "Rs", "Ctf"],
    "IMAX12": ["L", "C", "R", "Lss", "Rss", "Lsr", "Rsr", "Ltf", "Rtf", "Ltr", "Rtr", "Ctf"],
}


def get_channels(channel_format: str) -> List[str] | None:
    """Get the standard channel labels for a given audio format.

    This function looks up a channel format string (e.g., "5.1") in a
    predefined dictionary and returns the corresponding list of standard
    channel labels (e.g., ["L", "R", "C", "LFE", "Ls", "Rs"]).

    Args:
        channel_format (str): The audio format (e.g., "5.1", "7.1").

    Returns:
        List[str] | None: A list of channel labels, or None if the format is unknown.

    """
    return _CHANNEL_CONFIGURATIONS.get(channel_format)


def user_info() -> str:
    """Retrieve information about the authenticated user.

    Makes an authenticated GET request to the Coda API's '/interface/v2/users/me'
    endpoint to fetch details for the current user, determined by the API token.

    Returns:
        str: The JSON response from the API as a string.

    """
    ret = make_request(requests.get, "/interface/v2/users/me")
    return ret.json()


def validate_group_id() -> str:
    """Get the Coda Group ID from environment variables.

    Retrieves the Coda Group ID from the 'CODA_API_GROUP_ID' environment
    variable. This ID is required for most API operations that are scoped
    to a specific group.

    Raises:
        ValueError: If the 'CODA_API_GROUP_ID' environment variable is not set.

    Returns:
        str: The Coda Group ID.

    """
    group_id = os.getenv(ENV_CODA_API_GROUP_ID)
    if group_id is not None:
        return group_id
    raise ValueError("Error: CODA_API_GROUP_ID is not set.")


def make_request(
    func: Callable[..., requests.Response],
    route: str,
    payload: Dict[str, Any] | None = None,
) -> requests.Response:
    """Make an authenticated request to the Coda API.

    This is a general-purpose helper function for interacting with the Coda API.
    It constructs the full request URL, adds the necessary authentication
    headers, and executes the request using the provided function (e.g.,
    requests.get, requests.post).

    Args:
        func (Callable[..., requests.Response]): The requests function to call
            (e.g., requests.get, requests.post, requests.put).
        route (str): The API endpoint route (e.g., "/interface/v2/users/me").
        payload (Dict[str, Any], optional): A JSON serializable dictionary to
            be sent as the request body. Defaults to None.

    Raises:
        ValueError: If the 'CODA_API_TOKEN' environment variable is not set.

    Returns:
        requests.Response: The Response object from the `requests` library.

    """
    url = os.getenv(ENV_CODA_API_URL, DEFAULT_API_URL)
    url += route
    token = os.getenv(ENV_CODA_API_TOKEN)
    if token:
        verify = True
        if os.getenv(ENV_CODA_API_INSECURE_SKIP_VERIFY, '').lower() in INSECURE_SKIP_VERIFY_VALUES:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            verify = False
        auth = {"Authorization": f"Bearer {token}"}
        return func(url, json=payload, headers=auth, verify=verify)
    raise ValueError("Error: CODA_API_TOKEN is not set.")


def timing_info(
    inputs: Dict[str, Any],
    venue: str | None = None,
    fps: str | None = None,
    ffoa: str | None = None,
    lfoa: str | None = None,
    start_time: str | None = None,
) -> Dict[str, Any] | None:
    """Calculate various timing-related values for a set of inputs.

    This function processes a job's input definition to extract or calculate
    key timing metrics. It determines start time, duration, frame rate, and other
    values from the source essence definitions. It can also accept overrides for
    these values. The results are returned in a dictionary, including both
    second-based and timecode-based representations.

    Note:
        This function dynamically imports from `..tc_tools` for timecode
        conversions.

    Args:
        inputs (Dict[str, Any]): The workflow input dictionary, typically containing
            keys like 'sources', 'venue', and 'source_frame_rate'.
        venue (str, optional): Overrides the venue specified in the inputs. Defaults to None.
        fps (str, optional): Overrides the frame rate specified in the inputs. Defaults to None.
        ffoa (str, optional): Overrides the FFOA timecode specified in the inputs. Defaults to None.
        lfoa (str, optional): Overrides the LFOA timecode specified in the inputs. Defaults to None.
        start_time (str, optional): Overrides the start time. Not currently used in the function.

    Returns:
        Dict[str, Any] | None: A dictionary containing calculated timing information,
        or None if the input dictionary is empty.

    """
    from ..tc_tools import (
        time_seconds_to_vid_frames,
        vid_frames_to_tc,
        tc_to_time_seconds,
    )

    if not inputs:
        return None
    tinfo = {}
    if venue:
        tinfo["venue"] = venue
    else:
        tinfo["venue"] = inputs["venue"]
    if not fps:
        tinfo["source_frame_rate"] = inputs["source_frame_rate"]
        fps = tinfo["source_frame_rate"]
    else:
        tinfo["source_frame_rate"] = fps
    if not ffoa:
        tinfo["ffoa_timecode"] = inputs["ffoa_timecode"]
    else:
        tinfo["ffoa_timecode"] = ffoa
    if not lfoa:
        tinfo["lfoa_timecode"] = inputs["lfoa_timecode"]
    else:
        tinfo["lfoa_timecode"] = lfoa
    startt = -1
    srate = -1
    filelen = -1
    sources = inputs["sources"]
    for s in sources:
        definition = s.get("definition", {})
        if definition:
            if "programme_timing" in definition:
                srate = definition["sample_rate"]
                filelen = definition["frames"] / srate
                startt = (
                    definition["programme_timing"][
                        "audio_programme_start_time_reference"
                    ]
                    / srate
                )
                break
            if "resources" in definition:
                startt = (
                    definition["resources"][0]["bext_time_reference"]
                    / definition["resources"][0]["sample_rate"]
                )
                srate = definition["resources"][0]["sample_rate"]
                filelen = definition["resources"][0]["frames"] / srate
                break

    tinfo["start_time_sec"] = startt
    tinfo["file_duration_sec"] = filelen
    tinfo["file_duration"] = ""
    if fps != "":
        tinfo["file_duration"] = vid_frames_to_tc(
            time_seconds_to_vid_frames(filelen, fps), fps
        )
        tinfo["start_timecode"] = ""
    if fps != "":
        tinfo["start_timecode"] = vid_frames_to_tc(
            time_seconds_to_vid_frames(startt, fps), fps
        )
    tinfo["end_timecode"] = ""
    if fps != "":
        tinfo["end_timecode"] = vid_frames_to_tc(
            time_seconds_to_vid_frames(startt + filelen, fps) - 1, fps
        )
    tinfo["ffoa_seconds"] = -1
    tinfo["lfoa_seconds"] = -1
    if fps != "":
        tinfo["ffoa_seconds"] = tc_to_time_seconds(tinfo["ffoa_timecode"], fps)
        tinfo["lfoa_seconds"] = tc_to_time_seconds(tinfo["lfoa_timecode"], fps)
    tinfo["sample_rate"] = srate

    return tinfo


def is_key_value_comma_string(s: str) -> bool:
    """Validate a string formatted as KEY=VALUE,KEY=VALUE,...

    The pattern expects:
    - Uppercase letters, numbers, and underscores for KEYS.
    - Letters, numbers, hyphens, and underscores for VALUES.
    - Key-value pairs separated by a single comma.
    - No leading/trailing commas, and no empty keys or values.

    Returns:
        bool: true if matched

    """
    # Regex breakdown:
    # ^                 # Start of the string
    # ([A-Z0-9_]+)      # Group 1: KEY - one or more uppercase letters, numbers, or underscores
    # =                 # Literal equals sign
    # ([a-zA-Z0-9_-]+)  # Group 2: VALUE - one or more letters, numbers, hyphens, or underscores
    # (                 # Start of non-capturing group for subsequent pairs
    #   ,[A-Z0-9_]+=    # Comma followed by KEY=
    #   [a-zA-Z0-9_-]+  # VALUE
    # )*                # Zero or more of the subsequent pairs
    # $                 # End of the string

    pattern = r"^([A-Z0-9_]+=[a-zA-Z0-9_-]+)(,[A-Z0-9_]+=[a-zA-Z0-9_-]+)*$"

    return re.fullmatch(pattern, s) is not None
