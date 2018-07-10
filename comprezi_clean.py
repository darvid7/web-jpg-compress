import os
import comprezi

def remove_comprezi_files(file_full_path):
    # Only want to remove comprezi files.
    if not file_full_path.endswith("comprezi.jpg"):
        return
    os.remove(file_full_path)
    print("Removed %s" % file_full_path)

comprezi.search_dir(os.getcwd(), remove_comprezi_files)