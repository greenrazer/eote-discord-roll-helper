import os 
import subprocess

import eote

if __name__ == "__main__":
	dir_path = os.path.dirname(os.path.realpath(__file__))
	os.chdir(dir_path)
	pipe = subprocess.Popen("pip install -r requirements.txt", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	eote.main()