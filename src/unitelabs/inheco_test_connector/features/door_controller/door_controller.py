import asyncio
import random
import typing
from typing import Optional, Annotated
import time

import clr


from unitelabs.cdk import sila


class DoorController(sila.Feature):
    """Control door of the Inheco Single Plate Incubator."""

    def __init__(self):
        super().__init__(
            originator="casey",
            category="door",
            version="1.0",
            maturity_level="Draft",
        )

        # Connect to the device (TODO: move this elsewhere?!?)
        dll_path= r"C:\\Program Files\\INHECO\\Incubator-Control\\ComLib.dll"
        clr.AddReference(dll_path)
        from IncubatorCom import Com

        self.incubator_com = Com()

        # TODO: make a method here for this!
        self.open_connection()


    @sila.UnobservableCommand()
    async def open_connection(
        self, 
    ) -> int:
        """
        Opens the connection to the incubator(s) over the specified COM port.
        There may be several incubator devices in a stack on the same COM port.

        Returns:
            response (int): Response code from the ComLib DLL. 77 = success, 170 = fail.
        """
        self.port = "COM5"  # HARDCODED FOR TESTING
        response = self.incubator_com.openCom(self.port)
        if response == 77:
            print("COM connection opened successfully")  # noqa T201
        else:
            print("Failed to open the Inheco incubator COM connection.")
            raise Exception("Failed to open the Inheco incubator COM connection.")
        return response

    @sila.UnobservableCommand()
    async def close_connection(self) -> str:
        """
        Closes any existing open connection. No response expected on success or fail.
        """
        self.incubator_com.closeCom()
        return "Connection Closed!"

    @sila.UnobservableCommand()
    async def initialize_device(self, stack_floor: int) -> str:
        """
        Initializes the Inheco device through the open connection.

        Args:
            stack_floor (int): Stack floor of the Inheco incubator device.
        """
        self._send_message("AID", stack_floor=stack_floor, read_delay=3)
        return f"Device initialized at stack floor {stack_floor} "

    # DOOR CONTROL METHODS
    @sila.UnobservableCommand()
    async def open_door(self, stack_floor: int) -> str:
        """
        Opens the door.

        Args:
            stack_floor (int): Stack floor of the Inheco incubator device.
        """
        self._send_message(
            "AOD",
            stack_floor=stack_floor,
            read_delay=6,
        )  # wait 6 seconds before reading COM response
        return "Door opened!"

    @sila.UnobservableCommand()
    def close_door(self, stack_floor: int) -> str:
        """
        Closes the door.

        Args:
            stack_floor (int): Stack floor of the Inheco incubator device.
        """
        self._send_message(
            "ACD",
            stack_floor=stack_floor,
            read_delay=7,
        )
        return "Door closed!"

    def _send_message(
            self,
            message_string: str,
            device_id: Optional[int] = 2,
            stack_floor: Optional[int] = 0,
            read_delay: Optional[float] = 0.5,
        ) -> str:
            """
            Formats and sends message to Inheco device, then collects device response.

            Args:
                message_string: (str) Message to send to Inheco device.
                device_id: (int) ID of the Inheco device that will receive the message, default 2.
                stack_floor: (int) Level of the Inheco device. Need to specify in case several devices are stacked, default 0.
                read_delay: (float) Seconds to wait before reading COM response, default .5 seconds.

            Returns:
                formatted_response (str): Response from the COM port without extra characters.
            """

            # with self.lock:
            # Convert message length, device ID, and stack floor to bytes.
            bytes_message_length = len(message_string) & 0xFF
            bytes_device_id = device_id & 0xFF
            bytes_stack_floor = stack_floor & 0xFF

            # Convert them message to byte array.
            bytes_message = bytes([ord(c) for c in message_string])

            # Format the message, send over COM port and collect response.
            self.incubator_com.sendMsg(
                bytes_message, bytes_message_length, bytes_device_id, bytes_stack_floor
            )

            time.sleep(read_delay)

            # Read the COM port response.
            response = self.incubator_com.readCom()
            formatted_response = self._format_response(response)

            return formatted_response

    def _format_response(self, response: str) -> str:
            """
            Extracts the important message details from longer COM response message.

            Args:
                response: (str) Raw response from the COM port after a message is sent.

            Returns:
                formatted_response: (str) Response from the COM port without extra characters.

            Note:
                - The extra characters relate to device ID. They are not needed.
            """
            try:
                # Remove extra characters.
                formatted_response = response[1:]
                formatted_response = formatted_response[:-4]

            except Exception as e:
                print(e)
                raise e

            # Check for '#' response, meaning invalid command was sent.
            if formatted_response == "#":
                raise Exception("Invalid command sent, '#' response received.")

            return formatted_response


