import os
import shutil


def copy_src_to_main():
    cwd = os.getcwd()
    source = os.path.join(cwd, 'src/server.py')
    destination = os.path.join(cwd, 'main.py')

    # copy to main
    shutil.copyfile(source, destination)


if __name__ == "__main__":
    # invoke copy file
    copy_src_to_main()
