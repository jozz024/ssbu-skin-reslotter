import os
import shutil
import sys

def usage():
    print("usage: python reslotter.py <mod_directory> <hashes_file> <fighter_name> <current_alt> <target_alt> <out_directory>")
    sys.exit(2)

def makeDirsFromFile(path):
    dirName = os.path.dirname(path)
    try:
        os.makedirs(dirName)
    except:
        pass

def fix_windows_path(path: str, to_linux: bool):
    if to_linux:
        return path.replace("\\", "/")
    else:
        return path.replace("/", os.sep)

def find_fighter_files(mod_directory):
    all_files = []
    # list through the dirs in the mod directory
    for folders in os.listdir(mod_directory):
        full_path = os.path.join(mod_directory, folders)
        if os.path.isdir(full_path):
            # if the entry in the folder is a directory, walk through its contents and append any files you find to the file list
            for root, dirs, files in os.walk(full_path):
                # if files isnt nothing we "iterate" through it to append the file to the file list
                for file in files:
                    full_file_path = os.path.join(root, file)
                    all_files.append(fix_windows_path(full_file_path, True)[len(os.path.join(os.getcwd(), mod_directory)) + 1:])
    return all_files

def get_all_needed_files(config, known_files, fighter_name, current_alt, target_alt):
    # make two varibles, one that holds the new slot's dir info, and one that holds the old slot's dir info
    new_dir_info = f"fighter/{fighter_name}/{target_alt}"
    old_dir_info = f"fighter/{fighter_name}/{current_alt}"
    new_config = {}
    # add the "new_dir_infos" config option and fill it with the new dir info
    new_config["new_dir_infos"] = [new_dir_info, ]

    # add the "new_dir_infos_base" config option and fill it with all of the dir infos we can source back to the og slot
    new_config["new-dir-infos-base"] = {
        f"{new_dir_info}/cmn": f"{old_dir_info}/cmn",
        f"{new_dir_info}/camera": f"{old_dir_info}/camera"
    }

    new_config["share-to-vanilla"] = {}
    # now get every file that correlates to the fighters old slot
    for file in known_files:
        if config["new_dir_files"][new_dir_info].__contains__(file):
            continue
        if file.startswith(f"fighter/{fighter_name}/"):
            lookfor = f"/{current_alt}/"
            replace = f"/{target_alt}/"
            if file.__contains__(lookfor) and file.__contains__("."):
                new_file = file.replace(lookfor, replace)
                config["new_dir_files"][new_dir_info].append(new_file)
                new_config["share-to-vanilla"][file] = new_file
        elif file.startswith("sound/bank/fighter"):
            lookfor = f"{fighter_name}_{current_alt}"
            replace = f"{fighter_name}_{target_alt}"
            if file.__contains__(lookfor):
                new_file = file.replace(lookfor, replace)
                config["new_dir_files"][new_dir_info].append(new_file)
                new_config["share-to-vanilla"][file] = new_file
            lookfor = f"{fighter_name}_cheer_{current_alt}"
            replace = f"{fighter_name}_cheer_{target_alt}"
            if file.__contains__(lookfor):
                new_file = file.replace(lookfor, replace)
                config["new_dir_files"][new_dir_info].append(new_file)
                new_config["share-to-vanilla"][file] = new_file

    config["new_dir_files"][new_dir_info] = sorted(config["new_dir_files"][new_dir_info])
    new_config.update(config)
    return new_config

def reslot_fighter_files(mod_directory, fighter_files, current_alt, target_alt, out_dir, fighter_name):
    reslotted_files = []
    for files in fighter_files:
        # since they do files and folders differently, we have to go through each directory separately
        if files.startswith(f"fighter/{fighter_name}"):
            lookfor = f"/{current_alt}/"
            replace = f"/{target_alt}/"
            new_file = files.replace(lookfor, replace)
            makeDirsFromFile(os.path.join(out_dir, new_file))
            shutil.copy(os.path.join(mod_directory, files), os.path.join(out_dir, new_file))
            reslotted_files.append(new_file)
        elif files.startswith("ui/replace/chara"):
            lookfor = f"{current_alt.strip('c').strip('C')}.bntx"
            replace = f"{target_alt.strip('c').strip('C')}.bntx"
            new_file = files.replace(lookfor, replace)
            if new_file.__contains__("_" + fighter_name + "_"):
                makeDirsFromFile(os.path.join(out_dir, new_file))
                shutil.copy(os.path.join(mod_directory, files), os.path.join(out_dir, new_file))
        elif files.startswith("ui/replace_patch/chara"):
            lookfor = f"{current_alt.strip('c').strip('C')}.bntx"
            replace = f"{target_alt.strip('c').strip('C')}.bntx"
            new_file = files.replace(lookfor, replace)
            if new_file.__contains__("_" + fighter_name + "_"):
                makeDirsFromFile(os.path.join(out_dir, new_file))
                shutil.copy(os.path.join(mod_directory, files), os.path.join(out_dir, new_file))
        elif files.startswith("sound/bank/fighter"):
            lookfor = f"_{current_alt}"
            replace = f"_{target_alt}"
            new_file = files.replace(lookfor, replace)
            if new_file.__contains__("_" + fighter_name + "_"):
                makeDirsFromFile(os.path.join(out_dir, new_file))
                shutil.copy(os.path.join(mod_directory, files), os.path.join(out_dir, new_file))
                reslotted_files.append(new_file)

    return reslotted_files, fighter_files

def make_config(reslotted_files, known_files, fighter_name, current_alt, target_alt):
    # make a variable that holds the dirinfo path for the new slot
    new_dir_info = f"fighter/{fighter_name}/{target_alt}"
    # we have to do config separately if it's an added slot because those require extra config options
    config = {
        "new_dir_files": {
            new_dir_info: []
        }
    }

    for file in reslotted_files:
        if file not in known_files:
            config["new_dir_files"][new_dir_info].append(file)
    return config

def main(mod_directory, fighter_name, current_alt, target_alt, out_dir):
    # get all of the files the mod modifies
    fighter_files = find_fighter_files(mod_directory)

    # make the out directory if it doesn't exist
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    # reslot the files we use
    reslot_fighter_files(mod_directory, fighter_files, current_alt, target_alt, out_dir, fighter_name)


if __name__ == "__main__":
    try:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    except IndexError:
        usage()