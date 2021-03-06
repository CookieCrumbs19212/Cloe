import os
import argparse
import json
import subprocess
import platform
import sys

# Absolute path to the JSON file.
JSON_FILE_NAME = "zoom_meetings.json"
# Getting parent path and joining it with the JSON file name.
JSON_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), JSON_FILE_NAME)


def load_meeting_data():
    # If the zoom_meetings.json file does not exist, create it.
    if not os.path.exists(JSON_FILE_PATH):
        # Creating the file.
        with open(JSON_FILE_PATH, 'w') as f:
            print(f"{JSON_FILE_PATH} file created.")

        # Return an empty dictionary.
        return {}

    # Or if its empty, return an empty dictionary.
    elif os.path.getsize(JSON_FILE_PATH) == 0:
        # Return an empty dictionary.
        return {}

    # Else, if the JSON file exists, and it is not empty, return the meeting data.
    # Loading the JSON file containing the Zoom meeting information.
    with open(JSON_FILE_PATH, 'r') as json_file:
        meeting_data = json.load(json_file)

    return meeting_data


# Loading the meeting data from the zoom_meetings.json file. Only load once and it is available globally.
MEETING_DATA = load_meeting_data()


def dump_meeting_data_to_json():
    # Dump the dictionary into the json file.
    with open(JSON_FILE_PATH, 'w') as json_file:
        json.dump(MEETING_DATA, json_file, indent=4)


def add_meeting_entry(meeting_name: str,
                      meeting_id: str,
                      meeting_password: str = None) -> bool:
    """
    Function to add a new Zoom meeting entry into the zoom_meetings.json file.

    :param meeting_name: Name of the new Zoom meeting room
    :param meeting_id: Meeting ID for the new Zoom meeting
    :param meeting_password: Password for the new Zoom meeting: Optional
    :return: True if entry was added successfully
    """
    # Basic input validation. Checks if inputs are None or "".
    if meeting_name is False:
        print("\nInvalid value for meeting name parameter.\n")
        # Indicate operation failure.
        return False

    if meeting_id is False:
        print("\nInvalid value for meeting ID parameter.\n")
        # Indicate operation failure.
        return False

    # Check if the meeting_name contains any whitespaces. meeting names should not contain whitespaces.
    if ' ' in meeting_name:
        print("\nMeeting Names should not contain spaces. Use hyphens ('-') or underscores ('_') instead.\n")
        return False

    """ If the meeting name already exists """
    if meeting_name in MEETING_DATA.keys():
        response = input(f"\nMeeting Name \"{meeting_name}\" already exists."
                         "\nDo you want to overwrite the existing entry? [N/y]: ")

        if response.lower() not in ['y', 'yes']:
            print("\nAdd operation aborted.\n")
            return False
        else:
            print(f"\nOverwriting entry for meeting: \"{meeting_name}\"\n")

    # Creating a new dictionary entry for the meeting.
    MEETING_DATA[meeting_name] = {"meeting_id": meeting_id,
                                  "password": (meeting_password if meeting_password is not None else "")}

    # Dump the modified meeting data to the zoom_meetings.json file.
    dump_meeting_data_to_json()

    # Indicate successful operation.
    print(f"\nNew saved meeting \"{meeting_name}\" added successfully.\n")
    return True


def remove_meeting_entry(meeting_name: str = None) -> bool:
    """
    Remove a Zoom meeting entry from the zoom_meetings.json file.

    :param meeting_name: meeting name of the entry to be removed
    :return: True if entry was removed successfully
    """
    # Validation.
    if meeting_name is None:
        print("\nInvalid meeting name parameter.\n")
        return False

    # If the meeting name doesn't exist.
    if meeting_name not in MEETING_DATA.keys():
        print(f"\nMeeting entry with name \"{meeting_name}\" does not exist.\n")
        return False

    # Confirmation prompt.
    confirm = input(f"\nConfirm that you want to remove \"{meeting_name}\" from your saved meetings? [N/y]: ")

    # If user did not confirm operation.
    if confirm.lower() not in ['y', 'yes']:
        print("\nRemove operation aborted.\n")
        return False

    # If user confirmed remove operation.
    else:
        # Removing the entry.
        MEETING_DATA.pop(meeting_name)

        # Dump modified meeting data into zoom_meetings.json file.
        dump_meeting_data_to_json()

        # Indicate successful operation.
        print(f"\nMeeting entry \"{meeting_name}\" removed successfully.\n")
        return True


def print_meeting_names():
    print("\n-> Saved Meeting entries: \n")

    # Print out all the meeting names.
    for index, meeting_name in enumerate(MEETING_DATA.keys()):
        meeting_id = MEETING_DATA[meeting_name]['meeting_id']
        meeting_pw = MEETING_DATA[meeting_name]['password'] if MEETING_DATA[meeting_name]['password'] else '-nil-'

        # Print meeting details.
        print(f"{index}) {meeting_name}"
              f"\n\tMeeting ID: {meeting_id}"
              f"\n\tPassword  : {meeting_pw}\n")

    # Spacing
    print("\n")


def join_meeting(meeting_name: str = None, meeting_id: str = None, meeting_password: str = None):
    # If meeting_id is not provided, get it from MEETING_DATA using meeting_name.
    if meeting_id is None:
        meeting_id = MEETING_DATA[meeting_name]["meeting_id"]

    # If meeting_password is not provided, get it from MEETING_DATA using meeting_name.
    if meeting_password is None:
        meeting_password = MEETING_DATA[meeting_name]["password"]

    # Building the Zoom command. Only attaching the password section if the meeting has a password.
    command = f'zoommtg://zoom.us/join?confno={meeting_id}' + (f'&pwd={meeting_password}' if meeting_password else "")

    # Printing status message.
    print("\nLaunching Zoom...")

    # Check the operating system.
    current_os = platform.system().lower()
    if "linux" in current_os:
        # Running the shell command for Linux.
        process = subprocess.run(['xdg-open', command])

    elif "darwin" in current_os:
        # Running the shell command for macOS.
        process = subprocess.run(['open', command])

    elif "windows" in current_os:
        # Running the shell command for Windows.
        process = subprocess.run(['start', command])

    # If the operating system is unrecognized.
    else:
        print("\nFailed to launch Zoom. Unrecognized Operating System. \nExiting with non-zero exit code.\n")
        sys.exit(1)

    # Print success message if Zoom was launched successfully.
    if process.returncode == 0:
        print("\nYou have successfully joined the Zoom meeting.\n")
        sys.exit(0)

    # Print failure message.
    else:
        print("\nFailed to launch Zoom."
              "\nPlease ensure that you have installed and are logged into the Zoom Desktop Client.\n")
        # Exit with non-zero exit code.
        sys.exit(2)


def main():
    # Initialize an argument parser.
    parser = argparse.ArgumentParser(description="Python script to open Zoom meetings in the Zoom Desktop Client from "
                                                 "the terminal.")

    # Adding arguments.
    parser.add_argument("action", type=str, help="The action to perform (ls, join, add, rm)")
    parser.add_argument("raw_mid", type=str, nargs="?", help="Meeting ID to quick join a meeting")
    parser.add_argument("raw_mpw", type=str, nargs="?", help="Meeting password when quick joining a meeting (optional)")
    parser.add_argument("-n", "--mname", type=str, metavar="Meeting Name",
                        help="Name of the Zoom meeting")

    parser.add_argument("-I", "--mindex", type=int, metavar="Meeting Index",
                        help="Index of the Zoom meeting.")

    parser.add_argument("-i", "--mid", type=str, metavar="Meeting ID",
                        help="Meeting ID of the Zoom meeting")

    parser.add_argument("-p", "--mpw", type=str, metavar="Meeting Password",
                        help="Password to enter the Zoom meeting")

    # Parse the arguments.
    args = parser.parse_args()

    """
    The raw_mid and raw_mpw are used when you want to join a meeting directly without adding a meeting entry into
    Cloe first.
    
    How to use it:
    $ python3 ./cloe.py join 12345678 123000
                                |        |_ This is the meeting password (raw_mpw)
                                |_ This is the meeting id (raw_mid)    
    
    """

    """ Determine the action """

    # Print the names of all the stored meeting entries.
    if args.action == "ls":
        print_meeting_names()

    # Join a meeting.
    elif args.action == "join":
        # Check if mname was provided and that mname exists in the meeting list.
        if args.mname and args.mname in MEETING_DATA.keys():
            join_meeting(meeting_name=args.mname)

        # Check if mindex was provided and that it is in the valid range.
        elif args.mindex and 0 <= args.mindex < len(MEETING_DATA.keys()):
            join_meeting(list(MEETING_DATA.keys())[args.mindex])

        # To join a meeting directly without saving meeting details to the zoom_meetings.json.
        elif args.raw_mid:
            join_meeting(meeting_id=args.raw_mid, meeting_password=args.raw_mpw)

        # If both inputs were not valid.
        else:
            print("\nInvalid arguments."
                  "\nProvide a meeting ID and meeting password (optional) to quick join a Zoom meeting."
                  "\n Or provide either --mname or --mindex to join a saved Zoom meeting.\n")

    # Add a new meeting entry.
    elif args.action == "add":
        # Validate that all the required arguments were provided.
        if all([args.mname, args.mid]):
            add_meeting_entry(meeting_name=args.mname, meeting_id=args.mid, meeting_password=args.mpw)
        else:
            print("\nMissing arguments for add command. Provide arguments --mname, --mid and --mpw (if required).\n")

    # Remove a meeting entry.
    elif args.action == "rm":
        # Validate that the required argument was provided.
        if args.mname:
            remove_meeting_entry(meeting_name=args.mname)
        else:
            print("\nMissing arguments for rm command. Provide --mname argument.\n")

    # Invalid command
    else:
        print(f"\nUnknown command: {args.action}\n\n")


if __name__ == "__main__":
    main()
