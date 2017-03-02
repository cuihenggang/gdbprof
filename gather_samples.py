import time
import os
import sys
import random

min_sleep = 1
max_sleep = 1

if len(sys.argv) != 3:
    print "usage %s <pid> <outputfile>" % sys.argv[0]
    sys.exit(0)

cmds = []
cmds.append("thread apply all bt")
cmds.append("detach")
cmds.append("quit")

cmds = ['-ex "%s" '%s for s in cmds]
cmds = ' '.join(cmds)

pid = sys.argv[1]
of = sys.argv[2]

cmd = 'gdb -batch %s  --pid %s >> %s && echo "" >> %s' %(cmds, pid, of, of)

ret = 0

while ret == 0:
    ret = os.system(cmd)
    stime = random.random() * (max_sleep - min_sleep) + min_sleep
    time.sleep(stime)

print "done"

