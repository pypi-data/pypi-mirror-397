from ctfsolver.managers.manager_folder import ManagerFolder


def main():
    """
    Description :
        Calls the function via
        ```bash
        python -m ctfsolver.folders
        ```

        And creates the folders for the file
    """
    s = ManagerFolder()
    s.clean_folders()


if __name__ == "__main__":
    main()
