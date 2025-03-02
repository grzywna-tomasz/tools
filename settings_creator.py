import os
from icecream import ic

# All paths are from this tool to certain locations in target project
path_to_target_project = "../RevMaster/RvMstr/proper_project/"
build_dir = "GNU ARM v12.2.1 - Debug"
makefile_dir = "Makefile"
source_directory_main_dir = ""


makefile_location = f"{path_to_target_project.strip("/")}/{makefile_dir.strip("/")}/"
build_directory_path = f"{path_to_target_project.strip("/")}/{build_dir.strip("/")}/"
source_directory_main_path = f"{path_to_target_project.strip("/")}/{source_directory_main_dir.strip("/")}/"

# Finde how deep the makefile is in the directory structure
makefile_to_project_path = "/".join(["../" for index in range(0, makefile_location.replace(path_to_target_project, "").count("/"))])

backlash_char = '\\'

def get_source_directories_used_headers():
    # Dirs where are source files
    source_dirs = []
    # Files where are dependecny information. This is used to fina all headers
    dependency_files = []
    # List of all headers used in project
    used_headers = []

    full_path_prefix = os.path.abspath(build_directory_path).strip(build_dir).replace(backlash_char, "/")

    # Find dependancy files and source dirs
    for root, dirs, files in os.walk(build_directory_path):
        for filename in files:
            if filename[-2:] == ".o":
                # getting object files to catch assembly files as well
                
                source_dirs.append(f"{root.replace(backlash_char, '/').replace(build_directory_path, '')}")
            if filename[-2:] == ".d":
                dependency_files.append(f"{root}/{filename}")

    # Do through content of dependency files and get the paths for all dependancies 
    for file in dependency_files:
        with open(file, "r") as reader:
            lines = reader.readlines()
            # TODO remove objects the smarter way
            lines.pop(0)
            for line in lines:
                # Change backslash to slash, strip leading and trailing whitespaces and ":"
                line = line.replace(backlash_char, "/").strip("/").strip(":").strip()
                # split in case there are multiple files in one line
                more_lines = line.split()
                for line_ in more_lines:
                    line_ = line_.replace("//", "/")
                    line_ = line_.replace(makefile_to_project_path, "").strip()
                    # Remove full path from path if present
                    line_ = line_.replace(full_path_prefix, "")
                    used_headers.append(line_)
                    source_dirs.append(line_[:line_.rfind("/")])

    # Remove the repetetive paths
    return set(source_dirs), set(used_headers)

def get_all_directories_all_headers():
# Get all directories form the main source directory
    all_dirs = []
    all_headers = []
    for root, dirs, files in os.walk(source_directory_main_path):
        for filename in files:
            all_dirs.append(root.replace(backlash_char, "/").replace(path_to_target_project, "").strip("/"))
            if filename[-2:] == ".h":
                all_headers.append(f"{root.replace(backlash_char, '/').replace("//", "/").replace(path_to_target_project, '')}/{filename}".replace("//", "/"))
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

def get_smallest_exclude_path(actual, include_list):
    if actual.rfind("/") != -1:
        actual_cut = actual[:actual.rfind("/")]
        for include_dir in include_list:
            # Check if directory to be included is a part of include dir
            if include_dir.find(actual_cut) != -1:
                return actual, False
        smallest_path, status = get_smallest_exclude_path(actual_cut, include_list)
        return smallest_path, True
    else:
        return actual, False

def get_exclude_dirs():
    exclude_list = []
    for directory in all_dirs_set:
        smallest_dir, to_be_included = get_smallest_exclude_path(directory, include_list)
        if to_be_included:
            exclude_list.append(smallest_dir)
    return list(set(exclude_list))

def get_exclued_headers(all_headers, used_headers):
    unused_headers = []
    for header in all_headers:
        if header not in used_headers:
            unused_headers.append(header)
    return unused_headers

def print1(iterational):
    for item in iterational:
        print(item)

source_dirs_set, used_headers_set = get_source_directories_used_headers()
all_dirs_set, all_headers_set = get_all_directories_all_headers()

include_list = list(source_dirs_set)
include_list.sort()
exclude_list = get_exclude_dirs()
exclude_list.extend(get_exclued_headers(all_headers_set, used_headers_set))
# Remove all headers / directories that are nested in dir to be removed
exclude_list = get_list_without_nested_dirs(exclude_list)

out_str = '   "C_Cpp.default.includePath": [\n'
for item in include_list:
    out_str += f'        "{item}",\n'
out_str += "    ],\n"
out_str += '    "files.exclude": {\n'
for item in exclude_list:
    out_str += f'        "{item}": true,\n'
out_str += "    },\n"
# This helps with "Go to definition" searches
out_str += '    "C_Cpp.exclusionPolicy": "checkFilesAndFolders"'

with open("generated_settings.txt", "w") as writer:
    writer.write(out_str)