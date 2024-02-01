from lib.utils.Colors import Colors

class Logger:
    def __init__(self) -> None:
        pass

    def log_info(self, new_section, msg) -> None:
        new_section_str = ""
        if (new_section == 1):
            new_section_str = "\n"

        print(Colors.CYAN + f"{new_section_str}[•] " + Colors.RESET + msg)
    
    def log_ask(self, new_section, msg) -> None:
        new_section_str = ""
        if (new_section == 1):
            new_section_str = "\n"

        print(Colors.YELLOW + f"{new_section_str}[?] {msg}" + Colors.RESET, end=" ")

    def log_err(self, new_section, msg) -> None:
        new_section_str = ""
        if (new_section == 1):
            new_section_str = "\n"

        print(Colors.RED + f"{new_section_str}[!] An error occured: {msg}")