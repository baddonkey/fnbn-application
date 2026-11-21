from abc import ABC
from pathlib import Path
import platform

class RegisterCommand(ABC):

    def __init__(self):
        pass

    def register(self):
        pass

class RegisterWindowsCommand(RegisterCommand):

    def __init__(self):
        super().__init__()

    def register(self):

        import winreg

        EXE = Path(r"C:\Tools\FNBN\main.exe")
        VERB_KEY = r"Software\Classes\*\shell\RunFnbn"

        if not EXE.is_absolute() or not EXE.is_file():
            raise SystemExit(
                f"Set EXE to the full path of fnbn.exe. Current value: {EXE}"
            )

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, VERB_KEY) as verb:
            winreg.SetValueEx(verb, "", 0, winreg.REG_SZ, "This file needs a better Name ...")
            winreg.SetValueEx(verb, "MultiSelectModel", 0, winreg.REG_SZ, "Document")

            with winreg.CreateKey(verb, "command") as command:
                winreg.SetValueEx(
                    command,
                    "",
                    0,
                    winreg.REG_SZ,
                    #f'"{EXE}" -f "%1" --dryrun False',
                    f'cmd.exe /d /v:off /s /c "echo Processing... & "{EXE}" -f "%1" --dryrun False & if errorlevel 1 pause"'
                )


class RegisterLinuxCommand(RegisterCommand):

    def __init__(self):
        super().__init__()


class RegisterOsxCommand(RegisterCommand):

    def __init__(self):
        super().__init__()


class RegisterCommandFactory:

    def _getInstance():
        osname = platform.system()
        match osname:
            case "Linux":
                return RegisterWindowsCommand()
            case "Windows":
                return RegisterWindowsCommand()
            case "Osx":
                return RegisterWindowsCommand()
            case _:
                print("Unknown OS")
                SystemExit(
                    f"Unknown OS {osname}. Not supported for command registration."
                )
