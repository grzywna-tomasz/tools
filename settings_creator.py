import os

# All paths are from this tool to certain locations in target project
path_to_target_project = "../motor_controler/"
makefile_location = f"{path_to_target_project}makefile/"
build_directory = f"{path_to_target_project}Build/"
source_directory_main_path = f"{path_to_target_project}stm_autogen_files/"


def get_source_directory_set():
    # Dirs where are source files
    source_dirs = []
    # Files where are dependecny information. This is used to fina all headers
    dependency_files = []

    # Find dependancy files and source dirs
    for root, dirs, files in os.walk(build_directory):
        for filename in files:
            if filename[-2:] == ".o":
                # getting object files to catch assembly files as well
                source_dirs.append(f"{root.replace("\\", "/").replace(build_directory, "")}")
            if filename[-2:] == ".d":
                dependency_files.append(f"{root}/{filename}")

    # Finde how deep the makefile is in the directory structure
    makefile_to_project_path = "/".join(["../" for index in range(0, makefile_location.replace(path_to_target_project, "").count("/"))])

    # Do through content of dependency files and get the paths for all dependancies 
    for file in dependency_files:
        with open(file, "r") as reader:
            lines = reader.readlines()
            lines.pop(0)
            for line in lines:
                source_dirs.append(line[:line.rfind("/")].replace(makefile_to_project_path, "").strip())

    # Remove the repetetive paths
    return set(source_dirs)

def get_ass_directory_set():
# Get all directories form the main source directory
    all_dirs = []
    for root, dirs, files in os.walk(source_directory_main_path):
        for filename in files:
            all_dirs.append(root.replace("\\", "/").replace(path_to_target_project, "").strip("/"))
    return set(all_dirs)

def get_exclude_dirs():
    exclude_list = []
    for directory in all_dirs_set:
        dir_not_in_include = True
        for include_dir in include_list:
            if include_dir.find(directory) != -1:
                dir_not_in_include = False
                pass
        if dir_not_in_include:
            exclude_list.append(directory)
    return exclude_list

source_dirs_set = get_source_directory_set()
all_dirs_set = get_ass_directory_set()

include_list = list(source_dirs_set)
exclude_list = get_exclude_dirs()

print('"C_Cpp.default.includePath": [')
for item in include_list:
    print(f'"{item}",')
print("],")

print('"files.exclude": {')
for item in exclude_list:
    print(f'"{item}": true,')
print("},")