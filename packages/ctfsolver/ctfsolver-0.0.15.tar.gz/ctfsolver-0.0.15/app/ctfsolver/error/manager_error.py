"""
manager_error.py

Provides the ManagerError class for handling exceptions with colored output and optional verbose tracebacks.

Classes:
    ManagerError: Handles exceptions by printing colored error messages or full tracebacks, and provides a utility to wrap function execution with error handling.

Usage:
    Use ManagerError to manage error reporting in CLI applications, with support for verbose output and graceful handling of unexpected exceptions and keyboard interrupts.


Example:
    error_manager = ManagerError(verbose=True)
    error_manager.try_function(main_function)

"""

import sys
import traceback
from colorama import Fore, Style, init

# Initialize colorama for cross-platform color support
init(autoreset=True)


class ManagerError:
    """
    Handles exceptions with colored output and optional verbose tracebacks for CLI applications.

    This class provides methods to manage error reporting, including printing colored error messages,
    displaying full tracebacks when verbose mode is enabled, and gracefully handling unexpected exceptions
    and keyboard interrupts.

    Attributes:
        verbose (bool): If True, displays full traceback on error; otherwise, shows a colored error message.

    Methods:
        handle(exception: Exception, exit_code: int = 1):
            Handles an exception by printing a colored error message or full traceback, then exits with the given code.

        try_function(function: callable, *args, **kwargs):
            Executes a function, catching and handling exceptions and keyboard interrupts gracefully.
    """

    def __init__(self, *args, **kwargs):
        """
        Args:
            verbose (bool): If True, show full traceback, otherwise show a colored error.
        """
        self.verbose = kwargs.get("verbose", False)

    def handle(self, exception: Exception, exit_code: int = 1):
        """
        Handles exceptions by printing error information in color and exiting the program.

            exception (Exception): The exception instance to handle.
            exit_code (int, optional): The exit code to use when exiting the program. Defaults to 1.

        Returns:
            None

        Raises:
            SystemExit: Exits the program with the specified exit code.
        """
        if self.verbose:
            # Show full traceback
            print(Fore.RED + "An error occurred:\n" + Style.RESET_ALL)
            traceback.print_exc()
        else:
            # Show only the error type and message in color
            print(
                f"{Fore.RED}[ERROR]{Style.RESET_ALL} "
                f"{Fore.YELLOW}{type(exception).__name__}: {exception}{Style.RESET_ALL}"
            )

        sys.exit(exit_code)

    def try_function(self, function: callable, *args, **kwargs):
        """
        Executes a given function with provided arguments, handling exceptions.
        Args:
            function (callable): The function to execute.
            *args: Variable length argument list to pass to the function.
            **kwargs: Arbitrary keyword arguments to pass to the function.
        Returns:
            None
        Raises:
            Handles all exceptions using the `handle` method.
            Prints a message if interrupted by the user (KeyboardInterrupt).

        """

        try:
            return function(*args, **kwargs)
        except Exception as e:
            self.handle(e)
        except KeyboardInterrupt:
            print("Process interrupted by user.")
