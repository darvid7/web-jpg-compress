import os
import io
import sys
from PIL import Image
import shutil
import traceback

JPG_NORMAL_THRESHOLD = 100000 # 100kb.
JPG_BACKROUND_THRESHOLD = 400000 # 400kb.


IGNORE = {
    ".", "..", ".DS_Store", ".git", ".idea", "__pycache__"
}

def has_alpha_value(pil_image):
    return len(pil_image.split()) > 3

def compress_jpg(threshold, file_full_path):
    try:
        print("\nProcessing %s" % file_full_path)
        current_size_on_disk = os.path.getsize(file_full_path)
        if current_size_on_disk <= threshold:
            print("%s is small enough as is, comprezi won't touch it" % file_full_path)
            return
        img = Image.open(file_full_path)
        if has_alpha_value(img):
            # Convert rgba to rgb.
            print("%s has alpha layer" % file_full_path)
            img = img.convert('RGB')
        quality = 70 # Between 1 and 100, 1 being worst quality.

        print("current size on disk: %s" % current_size_on_disk)
        while True:
            # It might be quicker to make a new BytesIO object than clear one, 
            # it seems to be the case for StringIO.
            # https://stackoverflow.com/questions/4330812/how-do-i-clear-a-stringio-object
            buffer = io.BytesIO()
            img.save(buffer, "JPEG", quality=quality, optimize=True)
            size_on_disk = buffer.tell()
            print("compressing: %s" % size_on_disk)
            if size_on_disk <= threshold:
                break
            quality -= 1
            if quality < 1:
                # Resize image dimensions to reduce size.
                diems = img.size
                half = (diems[0]//2, diems[1]//2)
                img = img.resize(half)
                print("resized")
                # Reset quality.
                quality = 70
        compressed_file_name = file_full_path[:-4] # Slice off last 4 chars which are ".jpg".
        compressed_file_name = "".join([compressed_file_name, "_comprezi", ".jpg"])
        # Write compressed image.
        with open(compressed_file_name, "wb") as handle:
            handle.write(buffer.getvalue())
        _, wrote_file = compressed_file_name.rsplit(os.path.sep, 1)
        print("wrote %s, size on disk: %s" % (wrote_file, size_on_disk))
    except Exception as e:
        print("[comprezi error] error processing: %s" % file_full_path)
        print(e)
        traceback.print_exc()

        sys.exit(-1)

def possible_image(file_full_path):
      # Might be an image.
    if file_full_path.endswith("comprezi.jpg"): # Ignore files created by comprezi.
        return
    if file_full_path.endswith("_background.jpg"):
        compress_jpg(JPG_BACKROUND_THRESHOLD, file_full_path)
    elif file_full_path.endswith(".jpg"):
        compress_jpg(JPG_NORMAL_THRESHOLD, file_full_path)


def search_dir(current_dir, callback):
    """Kinda emulates unix find, when a file is reached calls callback with 
    full path of that file."""
    for filename in os.listdir(current_dir):
        if filename in IGNORE:
            continue
        file_full_path = os.path.join(current_dir, filename)
        if os.path.isdir(file_full_path):
            search_dir(file_full_path, callback)
        else:
            callback(file_full_path)

def main():
    print("comprezi will compress your jpgs!")
    search_dir(os.getcwd(), possible_image)

if __name__ == "__main__":
    main()


