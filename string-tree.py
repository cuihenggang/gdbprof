import sys
import shlex
import copy

original_samples = []
samples =[]
settings ={'max-lines': '30' }
transformations = []


test_samples = [['a', 'b', 'd'],
                ['a', 'b', 'd'],
                ['a', 'b', 'e'],
                ['a', 'c'],
                ['a', 'c'],
                ['f', 'g']]

def read_block(f):
    lines = []
    block_found = False
    while (f) :
        line = f.readline()
        line = line.strip()
        if line == "":
            if block_found:
                break
            else:
                block_found = True
        else:
            block_found = True
            lines.append(line)
    return lines

def read_file(filename):
    f = open(filename)
    samples = []
    while True:
        b = read_block(f)
        if len(b) > 0:
            samples.append(b)
        else :
            break
    f.close()
    return samples


def build_tree(samples, tree=None):
    if tree == None:
        tree = {}
    for i in range(len(samples)):
        sample = samples[i]
        t = tree
        for node in sample:
            if not t.has_key(node):
                t[node] = [0, {}]
            t[node][0] += 1
            t = t[node][1]
    return tree

def print_tree(tree, lvl=0, tot=None, lines = None):
    if lines == None:
        lines = int(settings['max-lines'])
    # sort entries by count
    cks = [(tree[k][0], k) for k in tree.keys()]
    cks.sort()
    cks.reverse()

    if tot==None:
        tot = sum( [v[0] for v in tree.values()])
    ks = [ck[1] for ck in cks]
    ls = 0
    leftover = lines - len(ks)
    printed = 0
    for k in ks:
        if ls >= lines:
            break
        tabs = "    "*lvl
        nr = tree[k][0]
        nr = int(100.0 * float(nr) / tot)
        nr = "%i%%" % nr
        print "%s%s: %s" % (tabs, nr, k)
        ls += 1
        p = print_tree(tree[k][1], lvl+1, tot, lines = leftover)
        printed += p +1
        leftover -= p
    return printed

commands = []

def retransform():
    global original_samples
    global samples
    global transformations
    samples = copy.deepcopy(original_samples)
    for f,a in transformations:
        s = samples
        samples = []
        for sample in s:
            samples += f(sample, a)


def do_exit(args):
    sys.exit(0)
commands.append( (('exit','q'), do_exit) )

def do_help(args):
    for cmd in [c[0] for c in commands]:
        print ', '.join(cmd)
commands.append( (('help', '?', 'h'), do_help) )

def load_test(args):
    global original_samples
    global samples
    original_samples += copy.deepcopy(test_samples)
    retransform()
commands.append( (('load-test', ), load_test) )

def do_print(args):
    global samples
    retransform()
    print ''
    print_tree(build_tree(samples))
    print ''
commands.append( (('print', 'p'), do_print) )

def prefix_idx(sample, s):
    for i in range(len(sample)):
        if sample[i].startswith(s):
            return i
    raise "not found"

def trim_before(sample, args):
    s = copy.copy(sample)
    for arg in args:
        try:
            s = s[prefix_idx(s,arg):]
            break
        except:
            pass
    return [s]
def do_trim_before(args):
    global transformations
    transformations.append( (trim_before, args) )
commands.append( (('trim-before',), do_trim_before) )

def trim_after(sample, args):
    s = copy.copy(sample)
    for arg in args:
        try:
            idx = prefix_idx(s,arg) + 1
            if idx < (len(s)):
                s = s[:idx]
            break
        except:
            pass
    return [s]
def do_trim_after(args):
    global transformations
    transformations.append( (trim_after, args) )
commands.append( (('trim-after',), do_trim_after) )

def reverse_sample(sample, args):
    s = copy.copy(sample)
    s.reverse()
    return [s]
def do_reverse(args):
    global transformations
    transformations.append( (reverse_sample, args) )
commands.append( (('reverse',), do_reverse) )

def gdb_transform(sample, args):
    t = []
    s = []
    for ss in sample:
        ss = ss.split()
        if ss[0].startswith("Thread"):
            t.append("Thread %s" % ss[1])
        elif ss[1].startswith("0x"):
            s.append(ss[3])
        else:
            s.append(ss[1])
    s.reverse()
    s = t+s
    return [s]
def do_parse_gdb(args):
    global transformations
    transformations.append( (gdb_transform, args) )
commands.append( (('parse-gdb',), do_parse_gdb) )
                     

def remove_samples(sample, args):
    s = copy.copy(sample)
    remove = False
    for arg in args:
        for ss in s:
            if ss.startswith(arg):
                remove = True
                break
    if remove:
        return []
    else:
        return [s]
def do_remove_samples(args):
    global transformations
    transformations.append( (remove_samples, args) )
commands.append( (('remove-samples', ), do_remove_samples) )

def rename(sample, args):
    s = []
    fr = args[:-1]
    to = args[-1]
    for st in sample:
        found = False
        for f in fr:
            if st.startswith(f):
                found = True
                break
        if found:
            s.append(to)
        else:
            s.append(st)
    return [s]
def do_rename(args):
    global transformations
    if len(args) < 2:
        print "rename src1 [src2 ... srcN] dest"
    else:
        transformations.append( (rename, args) )
commands.append( (('rename',), do_rename) )

def do_load_file(args):
    global original_samples
    for arg in args:
        # try:
            original_samples += read_file(arg)
        # except:
        #     print 'could not load file: ', arg
commands.append( (('load-file',), do_load_file) )

def do_show(args):
    global settings
    if len(args) == 0:
        for k,v in settings.iteritems():
            print k, ': ', v
    else :
        for arg in args:
            if settings.has_key(arg):
                print arg, ': ', settings[arg]
            else:
                print arg, ' not found in settings'
commands.append( (('show',), do_show) )

def do_set(args):
    global settings
    if len(args) != 2:
        print 'set <key> <value>'
        return
    if not settings.has_key(args[0]):
        print args[0], ' not a valid setting'
        return
    settings[args[0]] = args[1]
commands.append( (('set',), do_set) )

if __name__ == '__main__':
    while not sys.stdin.closed:
        line = raw_input("> ")
        line = shlex.split(line)
        if len(line) == 0:
            continue
        cmd = line[0]
        args = []
        if len(line) > 1:
            args = line[1:]
        found = False
        for c, f in commands:
            if cmd in c:
                found = True
                f(args)
        if not found:
            print 'command %s not found, try "help"' %cmd
        
        
