import subprocess, datetime
import os

# py_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "../../python-3.8.8-embed-amd64/python.exe"))
py_path = "python"

def main():
    print('Starting SIC')
    f = open('errors.log', 'a')
    f.write(f'\n___________________________________________________________\n\n')
    f.write(f'Command output for SIC on {datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")} :\n')
    #p = subprocess.Popen('python main_window.py', stdout=f, stderr=f, shell=True) #no skipping
    # p = subprocess.Popen(py_path + ' main_window.py', stdout=f, stderr=f, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    p = subprocess.Popen(py_path + ' main_window.py', stdout=f, stderr=f, shell=True)

    print('SIC started')
    #f.close()

if __name__ == '__main__':
    main()