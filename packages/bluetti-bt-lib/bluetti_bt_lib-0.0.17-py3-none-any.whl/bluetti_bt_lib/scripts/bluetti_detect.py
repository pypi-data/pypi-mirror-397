"""Bluetti detect command."""

import argparse
import asyncio
import logging

from ..bluetooth.device_recognizer import recognize_device


async def async_detect_device(address: str):
    print("Detecting device type")
    print()

    recognized = await recognize_device(address, asyncio.Future)

    if recognized is None:
        print("Unable to find device type information")
        return

    print()
    print(
        "Device type is '{}' with iot version {} and serial {}. Full name: {}".format(
            recognized.name, recognized.iot_version, recognized.sn, recognized.full_name
        )
    )
    if recognized.encrypted:
        print("This device uses encryption.")


def start():
    """Entrypoint."""
    parser = argparse.ArgumentParser(description="Detect bluetti devices")
    parser.add_argument("mac", type=str, help="Mac-address of the powerstation")
    args = parser.parse_args()

    if args.mac is None:
        parser.print_help()
        return

    logging.basicConfig(level=logging.DEBUG)

    asyncio.run(async_detect_device(args.mac))
