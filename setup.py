import subprocess
import sys

def install_libraries(libs):
    subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", *libs])

if __name__ == '__main__':
    libs = ['requests', 'pyqt5', 'pprint', 'peewee']
    install_libraries(libs)

    files = [
        'contacts.db',
    ]

    for file in files:
        open(file, 'a').close()