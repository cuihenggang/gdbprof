import sys

sep_threads= True
rev = True
# watch_threads = [8,7,6,5,4, 3, 2,1]
watch_threads = None
# watch_threads = [1]
min_lvl = 1
max_lvl = 100


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

def blocks_to_trace_counts(blocks):
    tc = {}
    for block in blocks:
        trace = []
        t = block[0].split()[1]
        if watch_threads != None and int(t) not in watch_threads:
            continue
        t= ("thread-%s" % t)
        for s in block[1:]:
            ss = s.split()
            if ss[1].startswith("0x"):
                # if len(ss) >= 7:
                #     trace.append("%s FROM %s" % (ss[3], ss[6]))
                # else:
                trace.append(ss[3])
            else:
                trace.append(ss[1])
        if (rev):
            trace.reverse()
        if sep_threads:
            trace.insert(0,t)
        trace = tuple(trace)
        if not tc.has_key(trace):
            tc[trace] = 0
        tc[trace] += 1
    return tc

# tree: map<name, pair<count, tree> >
def add_to_tree(block, tree, count):
    if len(block) == 0 :
        return
    head = block[0]
    tail = block[1:]
    if (not tree.has_key(head)) :
        tree[head] = [0, {}]
    tree[head][0] += count
    add_to_tree(tail, tree[head][1], count)

def print_tree(tree, lvl=0, tot=None, min_lvl=0, max_lvl=1000, min_pct=0):
    cks = [(tree[k][0], k) for k in tree.keys()]
    cks.sort()
    cks.reverse()
    ks = [ck[1] for ck in cks]
    for k in ks:
        tabs = "    "
        if (lvl >= min_lvl):
            tabs = "    "*(lvl - min_lvl)
        nr = tree[k][0]
        if (tot != None):
            # nr = int(100.0 *float(nr) / tot)
            nr = 100.0 *float(nr) / tot
            if nr < min_pct:
                return
            # nr = "%i%%" % nr
            nr = "%.2f%%" % nr
        if lvl >= min_lvl:
            print "%s%s: %s" % (tabs, nr, k)
        print_tree(tree[k][1], lvl+1, tot, 
                   min_lvl, max_lvl, min_pct)
        if lvl >= max_lvl:
            return


if len(sys.argv) < 2:
    print "usage: %s <tracefile>" % sys.argv[0]
    sys.exit(0)

blocks = []
f = open(sys.argv[1])
while (True):
    b = read_block(f)
    if len(b) > 0:
        if b[0].startswith("Thread"):
            blocks.append(b)
    else:
        break

print "number of samples: ", len(blocks)
tc = blocks_to_trace_counts(blocks)
tree ={}
tot = 0
for b in tc:
    tot += tc[b]
    add_to_tree(list(b), tree, tc[b])

print_tree(tree, tot=tot, min_pct=0, min_lvl=min_lvl, max_lvl=max_lvl)
