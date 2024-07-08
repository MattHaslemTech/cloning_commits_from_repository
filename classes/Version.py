class Version:
    def __init__(self, name, version_number):
        name_mod = name.replace("project.", "")

        self.name = name_mod
        self.version_number = version_number


    def debug_print(self):
        print(f"\tVersion: {self.name} - {self.version_number}")