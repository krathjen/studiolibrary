"""

#python /krathjen/git/sandbox/site-packages/mutils/tests/runtests.py
python /krathjen/git/sandbox/site-packages/mutils/tests/runtests.py
python C:/Users/hovel/Dropbox/git/studiolibrary/src/studioLibrary/site-packages/mutils/tests/runtests.py
#


import sys
sys.path.append("")
import mutils.tests;
mutils.tests.run()

"""

import subprocess

if __name__ == "__main__":
    cmd = 'maya -batch -command "python(\\\"import sys;sys.path.append(\\\\\\"/norman/work/krathjen/git/sandbox/site-packages\\\\\\");import mutils.tests;mutils.tests.run()\\\")"'
    print "Starting Maya: %s" % cmd
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.wait()
