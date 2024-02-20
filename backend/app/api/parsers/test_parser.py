# Desc: Parser for test files


import os
import time

def get_files(folder):
    files = []
    for file in os.listdir(folder):
        if file.endswith('.mscz'):
            files.append(file)
            print(file)
            print(file.split(".")[0])
            abs_path=os.path.abspath(folder)
            path=abs_path+"/"+file
            os.system('mscore -o ./XML_files/'+file.split(".")[0]+'.xml '+path)
            #time.sleep(5)
    return files

if __name__ == "__main__":
    files=get_files('Musescore-DB')





