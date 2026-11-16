import asyncio
import email
import email.message
import shutil
import tempfile
from typing import Dict, Mapping, Optional, Tuple
import os
import urllib.request
import urllib.parse
import urllib.error

import core
import decky
from decky import logger
import utils
import metadata

SUBSCRIPTIONS_DIR = os.path.join(decky.DECKY_PLUGIN_SETTINGS_DIR, "subscriptions")

SubscriptionDict = Dict[str, str]
Subscription = Tuple[str, str]
HWID_MAX_DEVICES_REACHED_ERROR = "HWID_MAX_DEVICES_REACHED"
SUBSCRIPTION_REQUEST_FAILED_ERROR = "SUBSCRIPTION_REQUEST_FAILED"


class _SubscriptionRequestError(Exception):
    """A subscription refusal represented by a stable client-facing error code."""


def get_path(filename: str) -> str:
    return os.path.join(SUBSCRIPTIONS_DIR, filename + ".yaml")

def _user_agent(user_agent_override: Optional[str] = None) -> str:
    if user_agent_override is not None and user_agent_override.strip() != "":
        return user_agent_override.strip()
    return f"mihomo/{core.LAST_CORE_VERSION} " \
           f"clash.meta/{core.LAST_CORE_VERSION} " \
            "clash-verge/2.5.0 mihomo.party/v1.9.5 FlClash/v0.8.93 " \
           f"{metadata.PACKAGE_NAME}/{decky.DECKY_PLUGIN_VERSION}"


def _request_headers(
    user_agent_override: Optional[str] = None,
    hwid: Optional[str] = None,
) -> Dict[str, str]:
    headers = {"User-Agent": _user_agent(user_agent_override)}
    if hwid is not None and hwid.strip():
        headers["X-Hwid"] = hwid.strip()
    return headers


def _check_hwid_response(headers: Mapping[str, str]) -> None:
    def enabled(name: str) -> bool:
        return headers.get(name, "").strip().lower() == "true"

    if enabled("x-hwid-max-devices-reached"):
        logger.warning("subscription request refused: HWID device limit reached")
        raise _SubscriptionRequestError(HWID_MAX_DEVICES_REACHED_ERROR)
    if enabled("x-hwid-not-supported"):
        logger.error("subscription request refused: server did not receive a valid HWID")
        raise _SubscriptionRequestError(SUBSCRIPTION_REQUEST_FAILED_ERROR)
    if enabled("x-hwid-limit"):
        logger.error("subscription request refused: unspecified HWID restriction")
        raise _SubscriptionRequestError(SUBSCRIPTION_REQUEST_FAILED_ERROR)


def _fetch_subscription(
    request: urllib.request.Request,
    timeout: Optional[float],
) -> Tuple[email.message.Message, bytes]:
    try:
        with urllib.request.urlopen(
            request, timeout=timeout, context=utils.get_ssl_context()
        ) as response:
            # Providers can signal an HWID refusal with HTTP 200 and valid YAML.
            # Reject it before the body can be saved as a working subscription.
            _check_hwid_response(response.headers)
            logger.debug(f"subscription response status: {response.status}")
            if response.status is not None and response.status != 200:
                raise ValueError(f"Invalid status code: {response.status}")
            return response.headers, response.read()
    except urllib.error.HTTPError as error:
        try:
            _check_hwid_response(error.headers or {})
        finally:
            error.close()
        raise

def _deduplicate_name(now_subs: SubscriptionDict, filename: str) -> Optional[str]:
    def check_exist(name) -> bool:
        is_exist = False
        for sub_name in now_subs:
            if sub_name == name:
                is_exist = True
                break
        return is_exist
    if check_exist(filename):
        available = False
        for i in range(100):
            if not check_exist(f'{filename}_{i}'):
                filename = f'{filename}_{i}'
                available = True
                break
        if not available:
            return None
    return filename

def download_sub(
    url: str,
    now_subs: SubscriptionDict,
    timeout: Optional[float] = None,
    user_agent: Optional[str] = None,
    hwid: Optional[str] = None,
) -> Tuple[bool, Subscription | str]:
    """
    Download new subscription
    Args:
        url: Subscription url
        now_subs: Currently subscriptions list
        timeout: Download timeout
        user_agent: Override subscription request User-Agent
        hwid: Persistent device UUID sent as X-Hwid
    Returns:
        tuple(bool, Subscription | str)
        bool: Whether download success
        Subscription | str: Subscription detail or error message
    """
    logger.info(f"downloading subscription: {url}")
    if not os.path.exists(SUBSCRIPTIONS_DIR):
        os.mkdir(SUBSCRIPTIONS_DIR)
    try:
        req = urllib.request.Request(url, headers=_request_headers(user_agent, hwid))
        logger.debug(f"download_sub: request headers: {req.header_items()}")
        headers, data = _fetch_subscription(req, timeout)
    except _SubscriptionRequestError as e:
        return False, str(e)
    except Exception as e:
        logger.error(f"download_sub: failed with {e}")
        return False, f"Exception: {e}"

    # get file name
    msg = email.message.Message()
    msg.add_header('content-disposition', headers.get('content-disposition')) # type: ignore
    msg.add_header('content-type', headers.get('content-type')) # type: ignore
    filename = msg.get_filename()

    if filename is None or filename == '':
        url_parts = urllib.parse.urlparse(url)
        paths = url_parts.path.split('/')
        if len(paths) > 0:
            filename = paths[-1]
    if filename is None or filename == '':
        filename = utils.rand_thing()
    if filename.lower().endswith('.yml'):
        filename = filename[:-4]
    if filename.lower().endswith('.yaml'):
        filename = filename[:-5]

    filename = _deduplicate_name(now_subs, filename)
    if filename is None:
        logger.error(f'download_sub: failed to deduplicate name: {filename}')
        return False, 'No available filename'

    filename = utils.sanitize_filename(filename)
    path = get_path(filename)
    logger.info(f'saving to {path}')

    try:
        if os.path.exists(path):
            logger.warning(f'download_sub: file exists, removing ...')
            os.remove(path)
        with open(path, 'xb') as out_file:
            out_file.write(data)
    except Exception as e:
        logger.error(f"download_sub: io error: {e}")
        return False, f"IO error: {e}"
    
    valid = core.CoreController.check_config(path)
    if not valid:
        logger.error("download_sub: invalid config")
        try:
            os.remove(get_path(filename))
        except Exception as e:
            logger.error(f"download_sub: error removing file: {e}")
        return False, "Invalid config"
    
    return True, (filename, url)

def import_sub(file_name: str, data: bytes, now_subs: SubscriptionDict) -> Tuple[bool, Subscription | str]:
    """
    Import subscription from file data
    Args:
        file_name: Original file name
        data: File content
        now_subs: Currently subscriptions list
    Returns:
        tuple(bool, Subscription | str)
        bool: Whether import success
        Subscription | str: Subscription detail or error message
    """
    if not os.path.exists(SUBSCRIPTIONS_DIR):
        os.mkdir(SUBSCRIPTIONS_DIR)

    filename = file_name or utils.rand_thing()
    if filename.lower().endswith('.yml'):
        filename = filename[:-4]
    if filename.lower().endswith('.yaml'):
        filename = filename[:-5]

    filename = _deduplicate_name(now_subs, filename)
    if filename is None:
        logger.error(f'import_sub: failed to deduplicate name: {filename}')
        return False, 'No available filename'

    filename = utils.sanitize_filename(filename)
    path = get_path(filename)
    logger.info(f'import_sub: saving to {path}')

    try:
        if os.path.exists(path):
            logger.warning(f'import_sub: file exists, removing ...')
            os.remove(path)
        with open(path, 'xb') as out_file:
            out_file.write(data)
    except Exception as e:
        logger.error(f"import_sub: io error: {e}")
        return False, f"IO error: {e}"

    valid = core.CoreController.check_config(path)
    if not valid:
        logger.error("import_sub: invalid config")
        try:
            os.remove(get_path(filename))
        except Exception as e:
            logger.error(f"import_sub: error removing file: {e}")
        return False, "Invalid config"

    return True, (filename, f"local://{filename}")

async def update_sub(
    name: str,
    url: str,
    timeout: float,
    user_agent: Optional[str] = None,
    hwid: Optional[str] = None,
) -> Optional[str]:
    target_path = get_path(name)
    temp_path: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(
            "wb",
            prefix=f".{utils.sanitize_filename(name)}.",
            suffix=".tmp",
            dir=SUBSCRIPTIONS_DIR,
            delete=False,
        ) as temp_file:
            temp_path = temp_file.name

        req = urllib.request.Request(url, headers=_request_headers(user_agent, hwid))
        logger.debug(f"update_sub: request headers: {req.header_items()}")

        def download() -> None:
            _, data = _fetch_subscription(req, timeout)
            with open(temp_path, "wb") as out_file:
                out_file.write(data)

        await asyncio.to_thread(download)

        valid = core.CoreController.check_config(temp_path)
        if not valid:
            logger.error(f"update_sub: invalid config for {name}")
            raise ValueError("Invalid config")

        os.replace(temp_path, target_path)
        temp_path = None
    except _SubscriptionRequestError as e:
        return str(e)
    except Exception as e:
        logger.error(f"update_sub: update {name} with error {e}")
        return str(e)
    finally:
        if temp_path is not None:
            try:
                os.remove(temp_path)
            except FileNotFoundError:
                pass
            except Exception as e:
                logger.error(f"update_sub: error removing temp file {temp_path}: {e}")
    return None

def duplicate_sub(subs: SubscriptionDict, name: str) -> Optional[str]:
    if name not in subs:
        return None
    new_name = _deduplicate_name(subs, name)
    if new_name is None:
        logger.error("duplicate_sub: failed to deduplicate name")
        return None
    try:
        shutil.copyfile(get_path(name), get_path(new_name))
    except Exception as e:
        logger.error(f"duplicate_sub: error {e}")
        return None
    return new_name
