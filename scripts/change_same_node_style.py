import re
from collections import defaultdict

file = open("ctb_train.txt")
new_file = open("ctb_train.txt.new", "w")
text = file.read();
file.close()
sentence_infos = text.split("\n\n")

node_pattern = re.compile(r"\(x.*? / .*?[\n)]")
for s in sentence_infos:
    # find duplicate ids
    node_set = set()
    duplicate_nodes = defaultdict(int)
    nodes = node_pattern.findall(s)

    all_id = set()

    for node in nodes:
        node = node[:-1]
        if node not in node_set:
            node_set.add(node);
        else:
            duplicate_nodes[node] += 1
            print s.split("\n")[0]
            print node

        id = node.split("/")[0][1:-1]
        all_id.add(id)

    # replace duplicate ids in annotation
    tokes = s.split("\n")[1]
    tokes_num = len(tokes.split())
    current_index = tokes_num
    for node in duplicate_nodes:
        last_occurence = s.index(node)
        for i in range(duplicate_nodes[node]):
            old_id = node.split("/")[0][1:-1]
            new_id = ""
            while True:
                new_id = "x" + str(current_index)
                if new_id not in all_id:
                    break
                else:
                    current_index += 1

            new_node = "(" + new_id + " / " + old_id
            all_id.add(new_id)

            next_occurrence = s.index(node, last_occurence + 1)

            s = s[:next_occurrence] + new_node + s[next_occurrence + len(node):]

            last_occurence = next_occurrence

    # write back
    new_file.write(s + "\n\n")

new_file.close()

