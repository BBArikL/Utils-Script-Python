import os
import pickle
import json
import shutil
import tarfile

if __name__ == "__main__":
    # See https://stackoverflow.com/questions/45078157/load-spydata-file
    TEMP_DIR = "./temp"
    paths = ["Algo.spydata", 'Interface.spydata']  # Files
    for path in paths:
        # Its just a special tar
        new_path = path.replace(".spydata", ".tar")
        shutil.copy(path, new_path)

        # Decompress
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR, ignore_errors=True)
        os.makedirs(TEMP_DIR, exist_ok=True)

        with tarfile.open(new_path) as decompressed:
            decompressed.extractall(TEMP_DIR)

        for file in os.listdir(TEMP_DIR):
            print(file)
            if file.endswith(".pickle"):
                # Unpickle file object
                with open(os.path.join(TEMP_DIR, file), 'rb') as f:
                    data_temp = pickle.load(f)  # Security concerns over unpickling objects is accepted
                    # You should know the files you are working with

                    print(type(data_temp))
                    print(data_temp)

                    try:
                        with open(path.replace(".spydata", ".json"), "wt") as fd:
                            json.dump(data_temp, fd)
                    except TypeError as exception:
                        print(f"Could not save {file}. Inappropriate type: {exception}")


    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR, ignore_errors=True)