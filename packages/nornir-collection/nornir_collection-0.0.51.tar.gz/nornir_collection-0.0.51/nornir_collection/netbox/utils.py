#!/usr/bin/env python3
"""
This module contains general functions and tasks related to NetBox.

The functions are ordered as followed:
- Asyncio Helper Functions
- Helper Functions
- Regular Functions
- Task Helper Functions
- Single Nornir tasks
- Nornir tasks in regular function
"""

import os
import argparse
import json
import httpx
import asyncio
from typing import Tuple, Union, Any, Dict, List
import __main__
import requests
import pynetbox
from nornir.core.task import Task, Result
from nornir_collection.utils import (
    CustomArgParse,
    CustomArgParseWidthFormatter,
    get_env_vars,
    print_task_name,
    task_info,
    task_result,
)


#### Asyncio Helper Functions ###############################################################################


async def _fetch_nb_paginated_chunks(client: httpx.AsyncClient, path: str) -> list[dict]:
    """
    Fetch paginated results from NetBox API in chunks asynchronously.
    Args:
        client (httpx.AsyncClient): The HTTPX async client.
        path (str): The API endpoint path.
    Returns:
        list[dict]: List of results from the paginated API.
    """
    PAGE_SIZE = 1000  # Tune per NetBox limits (1000 is default max limit)

    # Initialize results list
    results: list[dict] = []

    # Function to append query string to URL
    def _append_qs(path: str, qs: str) -> str:
        # Determine the correct separator based on existing query parameters
        return f"{path}{'&' if '?' in path else '?'}{qs}"

    # Fetch the first page to get the total count
    first_url = _append_qs(path, f"limit={PAGE_SIZE}&offset=0")
    resp = await client.get(first_url)
    resp.raise_for_status()
    payload = resp.json()
    results.extend(payload["results"])
    # Get the total number of items
    total = payload.get("count", len(payload["results"]))

    # Function to fetch a specific offset
    async def fetch_offset(offset: int) -> list[dict]:
        # Build the URL with limit and offset
        url = _append_qs(path, f"limit={PAGE_SIZE}&offset={offset}")
        r = await client.get(url)
        r.raise_for_status()
        # Return the results from the current page
        return r.json()["results"]

    # Fetch remaining pages concurrently if any are left beyond the first page
    offsets = range(PAGE_SIZE, total, PAGE_SIZE)
    if offsets:
        # Fetch all remaining pages concurrently
        chunk_results = await asyncio.gather(*(fetch_offset(o) for o in offsets))
        for chunk in chunk_results:
            results.extend(chunk)

    # Return the complete list of results
    return results


async def get_nb_resources_async(nb_url: str, endpoints: dict[str, str]) -> dict[str, list[dict]]:
    """
    Fetch multiple NetBox API resources asynchronously with pagination support.
    Args:
        nb_url (str): Base URL of the NetBox instance.
        endpoints (dict[str, str]): Dictionary of endpoint names and their paths.
    Returns:
        dict[str, list[dict]]: Dictionary of endpoint names and their fetched data.
    """
    # Set up HTTPX async client with headers
    headers = {
        "Authorization": f"Token {os.environ['NB_TOKEN']}",
        "Accept": "application/json",
    }

    # Create an async HTTPX client session and fetch all endpoints concurrently with pagination
    async with httpx.AsyncClient(base_url=nb_url, headers=headers, verify=False, timeout=30) as client:  # nosec
        # Create tasks for each endpoint
        tasks = {
            name: _fetch_nb_paginated_chunks(client, path.rstrip("&?")) for name, path in endpoints.items()
        }
        # Gather all tasks concurrently and collect results
        data = {name: await coro for name, coro in tasks.items()}

    # Return the collected data
    return data


#### Helper Functions #######################################################################################


def init_pynetbox(nb_url: str, ssl_verify=False) -> pynetbox.api:
    """
    This function instantiate a Pynetbox API object, print the result and returns the API object
    """
    task_text = "Initialize PyNetBox"
    print_task_name(text=task_text)

    # Load environment variables or raise a TypeError when is None
    env_vars = get_env_vars(envs=["NB_TOKEN"], task_text=task_text)

    # Instantiate the NetBox API
    session = requests.Session()
    session.verify = ssl_verify
    nb = pynetbox.api(url=nb_url, token=env_vars["NB_TOKEN"], threading=False)
    nb.http_session = session

    # Print success result
    print(task_info(text=task_text, changed=False))
    print(f"'{task_text}' -> Pynetbox.Api <Success: True>")
    print(f"-> Instantiate the PyNetBox API for '{nb_url}'")

    return nb


def init_args_for_nornir_config_filepath() -> str:
    """
    This function initialze arguments to specify which NetBox instance and Nornir config filepath to use.
    """
    task_text = "Argparse verify arguments"
    print_task_name(text=task_text)

    # Load environment variables or raise a TypeError when is None
    env_vars = get_env_vars(envs=["NR_CONFIG_PROD", "NR_CONFIG_TEST"], task_text=task_text)
    nr_config_prod = env_vars["NR_CONFIG_PROD"]
    nr_config_test = env_vars["NR_CONFIG_TEST"]

    # Define the arguments which needs to be given to the script execution
    argparser = CustomArgParse(
        prog=os.path.basename(__main__.__file__),
        description="Specify the NetBox PROD or TEST instance and Nornir config filepath to be used",
        epilog="One of the two mandatory arguments is required.",
        argument_default=argparse.SUPPRESS,
        formatter_class=CustomArgParseWidthFormatter,
    )
    # Add a argparser group for mutual exclusive arguments
    group = argparser.add_mutually_exclusive_group(required=True)
    # Add the test argument
    group.add_argument(
        "--prod",
        action="store_true",
        default=False,
        help=f"use the NetBox 'PROD' instance and Nornir config '{nr_config_prod}'",
    )
    # Add the test argument
    group.add_argument(
        "--test",
        action="store_true",
        default=False,
        help=f"use the NetBox 'TEST' instance and Nornir config '{nr_config_test}'",
    )
    # Verify the provided arguments and print the custom argparse error message in case of an error
    args = argparser.parse_args()

    # Set the NetBox instance and the Nornir config file based on the arguments
    nb_instance = "TEST" if args.test else "PROD"
    nr_config = nr_config_test if args.test else nr_config_prod

    # If argparser.parse_args() is successful -> no argparse error message
    print(task_info(text=task_text, changed=False))
    print(f"'{task_text}' -> ArgparseResponse <Success: True>")
    print(f"-> Run on the NetBox '{nb_instance}' instance and Nornir config '{nr_config}'")

    return nr_config


def init_args_for_ipam_update() -> str:
    """
    This function initialze arguments to specify which NetBox instance and Nornir config filepath to use.
    """
    task_text = "Argparse verify arguments"
    print_task_name(text=task_text)

    # Load environment variables or raise a TypeError when is None
    env_vars = get_env_vars(envs=["NR_CONFIG_PROD", "NR_CONFIG_TEST"], task_text=task_text)
    nr_config_prod = env_vars["NR_CONFIG_PROD"]
    nr_config_test = env_vars["NR_CONFIG_TEST"]

    # Define the arguments which needs to be given to the script execution
    argparser = CustomArgParse(
        prog=os.path.basename(__main__.__file__),
        description="Specify the NetBox PROD or TEST instance and Nornir config filepath to be used",
        epilog="One of the two mandatory arguments is required.",
        argument_default=argparse.SUPPRESS,
        formatter_class=CustomArgParseWidthFormatter,
    )
    # Add all NetBox arguments
    argparser.add_argument(
        "--prod",
        action="store_true",
        default=False,
        help=f"use the NetBox 'PROD' instance and Nornir config '{nr_config_prod}'",
    )
    argparser.add_argument(
        "--test",
        action="store_true",
        default=False,
        help=f"use the NetBox 'TEST' instance and Nornir config '{nr_config_test}'",
    )
    # Add the optional rebuild argument
    argparser.add_argument(
        "--nmap",
        action="store_true",
        default=False,
        help="enable additionally to IP-Fabric a NMAP scan (default: no NMAP scan)",
    )
    # Verify the provided arguments and print the custom argparse error message in case any error or wrong
    # arguments are present and exit the script
    args = argparser.parse_args()

    # Verify the NetBox instance and Nornir config filepath
    if not (hasattr(args, "prod") or hasattr(args, "test")):
        argparser.error("No NetBox instance specified, add --prod or --test")

    # Set the NetBox instance and the Nornir config file based on the arguments
    nb_instance = "TEST" if args.test else "PROD"
    nr_config = nr_config_test if args.test else nr_config_prod

    # If argparser.parse_args() is successful -> no argparse error message
    print(task_info(text=task_text, changed=False))
    print(f"'{task_text}' -> ArgparseResponse <Success: True>")
    print("-> Arguments:")
    print(f"  - Run on the '{nb_instance}' NetBox instance and Nornir config '{nr_config}'")
    if args.nmap:
        print("  - NMAP scan additionally to IP-Fabric is enabled (default: no NMAP scan)")
    else:
        print("  - NMAP scan additionally to IP-Fabric is disabled (default: no NMAP scan)")

    return nr_config, args


def get_nb_resources(url: str, params: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
    """
    TBD
    """
    # Define the resource list
    resources: List[Dict[str, Any]] = []
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Token {os.environ.get('NB_TOKEN')}",
    }
    # While there is a next page continue the loop
    while url:
        # Do the http request
        response = requests.get(  # nosec
            url=url, headers=headers, params=params, verify=False, timeout=(3.05, 27)
        )
        # Verify the response code
        if not response.status_code == 200:
            print(response.status_code)
            print(response.text)
            raise ValueError(f"Failed to get data from NetBox instance {url}")
        # Extract the json data from the http response
        resp = response.json()
        # Add the response to the resource list
        resources.extend(resp.get("results"))
        # Get the url of the next page
        url = resp.get("next")

    # Retrun the resources list
    return resources


def post_nb_resources(url: str, payload: List[Dict]) -> requests.Response:
    """
    TBD
    """
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Token {os.environ.get('NB_TOKEN')}",
    }
    # Do the http request and return the result
    return requests.post(  # nosec
        url=url, headers=headers, data=json.dumps(payload), verify=False, timeout=(3.05, 27)
    )


def patch_nb_resources(url: str, payload: List[Dict]) -> requests.Response:
    """
    TBD
    """
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Token {os.environ.get('NB_TOKEN')}",
    }
    # Do the http request and return the result
    return requests.patch(  # nosec
        url=url, headers=headers, data=json.dumps(payload), verify=False, timeout=(3.05, 27)
    )


def delete_nb_resources(url: str, payload: List[Dict]) -> requests.Response:
    """
    TBD
    """
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Token {os.environ.get('NB_TOKEN')}",
    }
    # Do the http request and return the result
    return requests.delete(  # nosec
        url=url, headers=headers, data=json.dumps(payload), verify=False, timeout=(3.05, 27)
    )


#### Regular Functions ######################################################################################


def nb_patch_data(
    task_text: str,
    url: str,
    payload: List[Dict],
    text: str = None,
    verbose: bool = False,
) -> Tuple[requests.Response, str]:
    """
    TBD
    """
    # Set the task text
    text = task_text if not text else text

    # PATCH request to update the NetBox device custom fields after successful config
    response = patch_nb_resources(url=url, payload=payload)

    # Verify the response code
    if response.status_code != 200:
        result = (
            f"{task_result(text=text, changed=False, level_name='ERROR')}\n"
            f"'{task_text}' -> NetBoxResponse: <Success: False>\n"
            + f"-> Response Status Code: {response.status_code}\n"
            + f"-> Response Text: {response.text}\n"
            + f"-> Payload: {payload}"
        )
    elif verbose:
        result = (
            f"{task_result(text=text, changed=True, level_name='INFO')}\n"
            f"'{task_text}' -> NetBoxResponse: <Success: True>\n"
            + f"-> Response Status Code: {response.status_code}\n"
            + f"-> Response Text: {response.text}\n"
            + f"-> Payload: {payload}"
        )
    else:
        result = (
            f"{task_result(text=text, changed=True, level_name='INFO')}\n"
            f"'{task_text}' -> NetBoxResponse: <Success: True>"
        )

    # Return the whole requests response and the result string
    return response, result


#### Task Helper Functions ##################################################################################


def _nb_patch_resources(task: Task, task_text: str, url: str, payload: list) -> Union[str, Result]:
    """
    Sends a PATCH request to update the resources of a device in NetBox.
    Args:
        task (Task): The Nornir task object.
        task_text (str): The description of the task.
        payload (list): A list of dictionaries containing the resources to be updated.
    Returns:
        tuple: A tuple containing the result string and a boolean indicating whether the task failed.
    """
    # PATCH request to update the Cisco Support Plugin desired release
    response = patch_nb_resources(url=url, payload=payload)

    # Verify the response code and return the result
    if response.status_code != 200:
        result = (
            f"'{task_text}' -> NetBoxResponse: <Success: False>\n"
            + f"-> Response Status Code: {response.status_code}\n"
            + f"-> Response Text: {response.text}\n"
            + f"-> Payload: {payload}"
        )
        # Return the Nornir result
        return Result(host=task.host, result=result, changed=False, failed=True)

    # Return the result string
    result = f"'{task_text}' -> NetBoxResponse: <Success: True>"
    return result


def _nb_create_payload_patch_device_serials(task: Task, task_text: str, serials: dict) -> Union[list, Result]:
    """
    Create a payload for patching device serial numbers in NetBox.
    Args:
        task (Task): The Nornir task object.
        task_text (str): The task description.
        serials (dict): A dictionary containing the serial numbers for the devices.
    Returns:
        Union[List, Result]: A list of dictionaries containing the device IDs and serial numbers,
        or a Nornir Result object if an error occurs.
    """
    try:
        # Create a list of dicts. Multiple dicts if its a virtual chassis
        payload = []

        # Add the device depending if its a virtual chassis in NetBox or not
        if "virtual_chassis" in task.host and task.host["virtual_chassis"] is not None:
            # Add the master
            payload.append({"id": task.host["virtual_chassis"]["master"]["id"], "serial": serials["1"]})

            # Add all members to the payload if available
            if "members" in task.host["virtual_chassis"]:
                # Start enumerate with 2 as 1 is the virtual chassis master
                for num, member in enumerate(task.host["virtual_chassis"]["members"], start=2):
                    payload.append({"id": member["id"], "serial": serials[str(num)]})
        else:
            # Add the device (no virtual chassis)
            payload.append({"id": task.host["id"], "serial": serials["1"]})

        # Return the payload
        return payload

    except KeyError as error:
        result = f"'{task_text}' -> PythonResponse <Success: False>\n-> Dictionary key {error} not found"
        # Return the Nornir result
        return Result(host=task.host, result=result, changed=False, failed=True)


#### Nornir Tasks ###########################################################################################


#### Nornir Tasks ###########################################################################################
