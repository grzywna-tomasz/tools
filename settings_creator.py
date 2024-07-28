import os
from icecream import ic

# All paths are from this tool to certain locations in target project
path_to_target_project = "../motor_controler/"
makefile_location = f"{path_to_target_project}makefile/"
build_directory = f"{path_to_target_project}Build/"
source_directory_main_path = f"{path_to_target_project}stm_autogen_files/"

# Finde how deep the makefile is in the directory structure
makefile_to_project_path = "/".join(["../" for index in range(0, makefile_location.replace(path_to_target_project, "").count("/"))])


def get_source_directories_used_headers():
    # Dirs where are source files
    source_dirs = []
    # Files where are dependecny information. This is used to fina all headers
    dependency_files = []
    # List of all headers used in project
    used_headers = []

    # Find dependancy files and source dirs
    for root, dirs, files in os.walk(build_directory):
        for filename in files:
            if filename[-2:] == ".o":
                # getting object files to catch assembly files as well
                source_dirs.append(f"{root.replace("\\", "/").replace(build_directory, "")}")
            if filename[-2:] == ".d":
                dependency_files.append(f"{root}/{filename}")

    # Do through content of dependency files and get the paths for all dependancies 
    for file in dependency_files:
        with open(file, "r") as reader:
            lines = reader.readlines()
            lines.pop(0)
            for line in lines:
                line = line.replace("\\", "").replace(makefile_to_project_path, "").strip()
                used_headers.append(line)
                source_dirs.append(line[:line.rfind("/")])

    # Remove the repetetive paths
    return set(source_dirs), set(used_headers)

def get_all_directories_all_headers():
# Get all directories form the main source directory
    all_dirs = []
    all_headers = []
    for root, dirs, files in os.walk(source_directory_main_path):
        for filename in files:
            all_dirs.append(root.replace("\\", "/").replace(path_to_target_project, "").strip("/"))
            if filename[-2:] == ".h":
                all_headers.append(f"{root.replace("\\", "/").replace(path_to_target_project, "")}/{filename}")
    return set(all_dirs), set(all_headers)

def get_list_without_nested_dirs(in_list):
    in_list.sort()
    cleaned_list = []
    for in_item in in_list:
        nested = False
        for cleaned_item in cleaned_list:
            if in_item.find(cleaned_item) != -1:
                nested = True
        if nested == False:
            cleaned_list.append(in_item)
    return cleaned_list

def get_exclude_dirs():
    exclude_list = []
    for directory in all_dirs_set:
        dir_not_in_include = True
        for include_dir in include_list:
            # Check if directory to be included is a part of include dir
            if include_dir.find(directory) != -1:
                dir_not_in_include = False
                pass
        if dir_not_in_include:
            exclude_list.append(directory)
    return exclude_list

def get_exclued_headers(all_headers, used_headers):
    unused_headers = []
    for header in all_headers:
        if header not in used_headers:
            unused_headers.append(header)
    return unused_headers


source_dirs_set, used_headers_set = get_source_directories_used_headers()
all_dirs_set, all_headers_set = get_all_directories_all_headers()

include_list = list(source_dirs_set)
include_list.sort()
exclude_list = get_exclude_dirs()
exclude_list.extend(get_exclued_headers(all_headers_set, used_headers_set))
# Remove all headers / directories that are nested in dir to be removed
exclude_list = get_list_without_nested_dirs(exclude_list)

print('"C_Cpp.default.includePath": [')
for item in include_list:
    print(f'"{item}",')
print("],")

print('"files.exclude": {')
for item in exclude_list:
    print(f'"{item}": true,')
print("},")
# This helps with "Go to definition" searches
print('"C_Cpp.exclusionPolicy": "checkFilesAndFolders"')