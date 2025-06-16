class ManageProgramsScreen:
    def __init__(self):
        self.programs = []

    def display_programs(self):
        print("Displaying all programs:")
        for program in self.programs:
            print(f"- {program}")

    def add_program(self, program_name):
        self.programs.append(program_name)
        print(f"Program '{program_name}' added.")

    def remove_program(self, program_name):
        if program_name in self.programs:
            self.programs.remove(program_name)
            print(f"Program '{program_name}' removed.")
        else:
            print(f"Program '{program_name}' not found.")


class CreateEditProgramScreen:
    def __init__(self):
        self.current_program = None

    def create_program(self, program_name):
        self.current_program = program_name
        print(f"Created program: {program_name}")

    def edit_program(self, new_program_name):
        if self.current_program:
            print(f"Program '{self.current_program}' updated to '{new_program_name}'")
            self.current_program = new_program_name
        else:
            print("No program selected to edit.")


class ManageUsersScreen:
    def __init__(self):
        self.users = []

    def display_users(self):
        print("Displaying all users:")
        for user in self.users:
            print(f"- {user}")

    def add_user(self, user_name):
        self.users.append(user_name)
        print(f"User '{user_name}' added.")

    def remove_user(self, user_name):
        if user_name in self.users:
            self.users.remove(user_name)
            print(f"User '{user_name}' removed.")
        else:
            print(f"User '{user_name}' not found.")


class CreateEditUserScreen:
    def __init__(self):
        self.current_user = None

    def create_user(self, user_name):
        self.current_user = user_name
        print(f"Created user: {user_name}")

    def edit_user(self, new_user_name):
        if self.current_user:
            print(f"User '{self.current_user}' updated to '{new_user_name}'")
            self.current_user = new_user_name
        else:
            print("No user selected to edit.")