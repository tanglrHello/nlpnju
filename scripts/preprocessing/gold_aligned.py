# coding=utf-8
import argparse
import os
import time
from collections import defaultdict

'''
1、concept对应多个不连续位置,如(x2_x8 / 帮忙-02), 取第一个下标x2作为对齐的位置
2、字索引,如"市场分析家",(x1_3_4 / 分析), "市场分析家"是一个token,下标为1,分析是其中的第3、4个字,这种情况将分析直接对应到原来整个词,即对齐到1上
3、对于添加的额外concept,暂时不做对齐,如果这个concept没有一个句子范围内的下标
  (有些concept会退化成标准concept,如'和'->'and',但是它仍然有一个有效的句内位置)
 【jamr原先的处理是:将其所有子节点的所在区间作为它对齐的位置(x后面的数字如果超出了token的个数,就是额外的concept)】
4、对于有环的情况,暂不特殊处理,还当做树来处理,出现几次就是几个节点
5、人工标注的对齐中,有边对齐信息,但是jamr不考虑这个对齐
6、原标注文件中有这样的行:":time()  (x8 / name :op1 "12:00")", op1这个边和12点这个concept都没有对齐信息,本程序不能处理这样的情况,这句可以修改为':time()  (x8 / "12:00")'
7、程序按照:来切分节点,如果concept中含有:,则该concept一定要用引号包围起来
8、关于节点的回指(已处理):
537:
(x37 / causation
      :arg1(x1)  (x3 / 想起-01
            :arg0()  (x2 / 他   //******************
)            :aspect()  (x4 / 了
)            :arg1()  (x11 / 星球
                  :mod()  (x10 / 小
)                  :arg1-of(x9)  (x8 / 遗弃-01
                        :arg0(x7)  (x45 / person
))                  :poss()  (x5 / x2
)                  :mod()  (x6 / 那
))            :arg2()  (x48 / and
                  :op1()  (x15 / 难过-01
                        :arg0()  (x13 / 心里
)                        :degree()  (x14 / 有点
))                  :op2()  (x22 / 提出-01
                        :arg0()  (x17 / x2     //****************** 在对齐的时候不能认为concept就是x2,要将其恢复成原始词汇
)                        :arg1()  (x26 / 请求-01
                              :cunit()  (x25 / 个
)                              :arg1(x20)  (x21 / 国王
)                              :arg2()  (x61 / and
                                    :op1()  (x30 / 想-02
                                          :arg0()  (x29 / x2
)                                          :arg1()  (x31 / 看-02
                                                :arg1()  (x32 / 日落
)                                                :arg0()  (x29 / x2
)))                                    :op2()  (x34 / 请求-01
                                          :arg1()  (x35 / x21
)))                              :quant()  (x24 / 1
)                              :arg0()  (x17 / x2
))                        :aspect()  (x23 / 了
)                        :manner(x19)  (x18 / 大胆
)                        :arg0()  (x17 / x2
)))))
已知这个回指不会出现环的情况

9、jamr对于新增concept的处理,在align.log文件中会有对齐信息,但是人工标注不对齐新增的concept(暂不处理)
例如jamr会有这个对齐信息: Span 3:  岁 => (temporal-quantity :unit 岁)
10、对concept中有括号的情况,在parse时需要特殊处理

原标注修改:
1、边的括号
279: :time()  (x8 / name :op1 "12:00") ——》 :time()  (x8 / "12:00")
556: time()  (x8_x9 / name :op1 "7:40"))) ——》 time()  (x8_x9 / "7:40")))
1131: :time()  (x12 / name :op1 "3:00")) ——》 :time()  (x12 / "3:00"))
      :time()  (x7 / name :op1 "4:00"))) ——》 :time()  (x7 / "4:00")))
1133: :time()  (x3 / name :op1 "4:00")) ——》 :time()  (x3 / "4:00"))


'''


class AmrAnnotation:
    def __init__(self):
        self.sid = ""   # type: str, looks like: 0.2.0.0
        self.snt_toks_str = ""   # type: str, looks like:  ::snt 这 对 我 来说 是 个 生 与 死 的 问题 。
        self.amr_tree_lines = []   # type: list of str, each string preserves the original indents in tree annotation


class AmrTreeNode:
    def __init__(self, concept, concept_id, rel_to_parent, tree_tokens_num):
        self.id = None
        self.concept = concept
        self.concept_id = concept_id   # totally same as that in annotation, indexing from 1, looks like: x25
        self.rel_to_parent = rel_to_parent
        self.tree_tokens_num = tree_tokens_num

        self.child_num = 0
        self.children = []

        self.aligned_pos = self.get_span(self.concept_id, tree_tokens_num)

    def add_child(self, child_node):
        child_node.id = self.id + "." + str(self.child_num)
        self.child_num += 1
        self.children.append(child_node)

    def get_span(self, concept_id, toks_num):
        indexes = concept_id.split('_')

        if len(indexes) == 0:
            return ""

        word_indexes = []
        for i in indexes:
            if i.startswith("x"):
                word_indexes.append(int(i[1:]))  # remove 'x' at the beginning

                # check for newly added concepts
                if int(i[1:]) > toks_num:
                    return ""
            elif i == "":
                raise Exception("invalid concept id")
            else:
                pass  # ignore index for characters inside a word, such as x12_1_3

        assert len(word_indexes) > 0

        is_continuous = self.check_index_continuous(word_indexes)
        if is_continuous:
            span_first_index = word_indexes[0] - 1
            span_last_index = word_indexes[-1]
        else:  # not continuous indexes for a concept, make the first index as the major index
            span_first_index = word_indexes[0] - 1
            span_last_index = word_indexes[0]
        return str(span_first_index) + "-" + str(span_last_index)

    @staticmethod
    def check_index_continuous(word_indexes):
        is_continuous = False
        last_index = word_indexes[0]
        for i in word_indexes[1:]:
            if i != last_index + 1:
                break
            else:
                last_index = i
        else:
            is_continuous = True
        return is_continuous


class AmrEdge:
    def __init__(self, source_node, dest_node, rel):
        self.source_node = source_node
        self.dest_node = dest_node
        self.rel = rel


class AmrTree:
    def __init__(self, amr_annotation):
        self.amr_annotation = amr_annotation
        self.root = None
        self.nodes = []
        self.edges = []
        self.alignments = []

    def parse(self):
        assert len(self.amr_annotation.amr_tree_lines) > 0
        toks_num = len(self.amr_annotation.snt_toks_str.split()) - 1  # ignore the first tok '::snt'

        # get plane tree
        plane_tree = "".join(line.strip() for line in self.amr_annotation.amr_tree_lines)
        nodes_str = self.split_annotation(plane_tree)

        # get root
        root_str = nodes_str[0]
        assert "(" == root_str[0]
        root_str = root_str[1:].strip()
        concept_id = root_str.split("/")[0].strip()
        concept = root_str.split("/")[1].strip()

        # tree has only one root node
        only_root_flag = False
        if concept[-1] == ")":
            concept = concept[:-1]
            only_root_flag = True

        root = AmrTreeNode(concept, concept_id, "", toks_num)
        root.id = '0'
        self.root = root

        if only_root_flag:
            return

        concept_dict = defaultdict(list, [])

        node_stack = [root]
        node_stack_record = [root]
        # process non-root nodes
        for node_annotation in nodes_str[1:]:
            # extract relation/raw_concept_id/concept
            assert "(" in node_annotation      # node_annotation: 'arg0()  (x39 / 大人)))'
            first_left_bracket_index = node_annotation.index("(")  # the left bracket for alignment of relation
            second_left_bracket_index = node_annotation.index("(", first_left_bracket_index)

            rel_to_parent = node_annotation[:second_left_bracket_index].strip()  #rel_info: 'arg0'

            node_info = node_annotation[second_left_bracket_index + 1:]  # node_info: 'x39 / 大人)))'

            assert node_info.count("/") == 1
            concept_info = node_info.split("/")     # node_info: ['x39 ', ' 大人)))']
            concept_id = concept_info[0].strip()  # concept_id: 'x39'
            concept_and_bracket = concept_info[1].strip()    #concept_and_bracket: '大人)))'

            # right_bracket: ')))', subtracted by the number of '(' contained in concept
            right_bracket_num = concept_and_bracket.count(")") - concept_and_bracket.count("(")
            if right_bracket_num != 0:
                concept = concept_and_bracket[:-right_bracket_num]   # concept: '大人'
            else:
                concept = concept_and_bracket.strip()

            # insert node into AmrTree
            new_node = AmrTreeNode(concept, concept_id, rel_to_parent, toks_num)
            concept_dict[concept_id].append(new_node)

            parent_node = node_stack[-1]
            parent_node.add_child(new_node)
            node_stack.append(new_node)
            node_stack_record.append(new_node)

            # new node is not leaf node
            if right_bracket_num == 0:
                pass

            # new node is leaf node, pop corresponding ancestor nodes out
            for i in range(right_bracket_num):
                del node_stack[-1]

        # co-reference recover, for nodes like x12 / x5
        '''
        for concept_id in concept_dict:
            for node in concept_dict[concept_id]:
                concept = node.concept
                while self.is_concept_id_style(concept):   # while concept looks like x12
                    # if there is a node x15 / x12, then referenced_node_concept_id is x12
                    referenced_node_concept_id = concept
                    referenced_node = concept_dict[referenced_node_concept_id][0]
                    concept = referenced_node.concept
                node.concept = concept
        '''

        for concept_id in concept_dict:
            for node in concept_dict[concept_id]:
                concept = node.concept
                if self.is_concept_id_style(concept):
                    aligned_pos = node.aligned_pos
                    if aligned_pos == "":
                        while self.is_concept_id_style(concept):  # while concept looks like x12
                            # if there is a node x15 / x12, then referenced_node_concept_id is x12
                            referenced_node_concept_id = concept
                            referenced_node = concept_dict[referenced_node_concept_id][0]
                            concept = referenced_node.concept
                    else:
                        first_index = int(aligned_pos.split("-")[0])
                        last_index = int(aligned_pos.split("-")[1])
                        toks = self.amr_annotation.snt_toks_str.split()[1:]
                        concept = "".join(toks[first_index:last_index])
                    node.concept = concept
        assert len(node_stack) == 0

    @staticmethod
    def is_concept_id_style(string):
        if len(string) == 1:
            return False

        return string[0] == 'x' and string[1:].isdigit()

    # especially for concepts containing ':'
    # can't deal with all situations, can be improved*********
    @staticmethod
    def split_annotation(plane_tree):
        node_strs = []
        current_node_str = ""
        concept_inside_single_quote = False
        concept_inside_double_quote = False
        concept_inside_bookmark_quote = False

        for c in plane_tree:
            if c.decode('utf-8', errors='ignore') == u'《':
                concept_inside_bookmark_quote = True
            elif c == '》':
                concept_inside_bookmark_quote = False

            elif c == '"':
                concept_inside_double_quote = not concept_inside_double_quote
            elif c == "'":
                concept_inside_single_quote = not concept_inside_single_quote

            elif c == ":":
                if not concept_inside_single_quote and not concept_inside_double_quote and not concept_inside_bookmark_quote:
                    node_strs.append(current_node_str)
                    current_node_str = ""
                else:
                    current_node_str += c
            else:
                current_node_str += c

        node_strs.append(current_node_str)

        assert concept_inside_double_quote == False
        assert concept_inside_single_quote == False
        assert concept_inside_bookmark_quote == False

        return node_strs

    def get_nodes(self):
        if self.nodes:
            return self.nodes

        assert self.root is not None
        self.dfs_traverse_for_nodes(self.root)
        return self.nodes

    def dfs_traverse_for_nodes(self, current_root):
        self.nodes.append(current_root)
        for child in current_root.children:
            self.dfs_traverse_for_nodes(child)

    def get_edges(self):
        if self.edges:
            return self.edges

        assert self.root is not None
        self.dfs_traverse_for_edges(self.root)
        return self.edges

    def dfs_traverse_for_edges(self, current_root):
        for child in current_root.children:
            self.edges.append(AmrEdge(current_root, child, child.rel_to_parent))
            self.dfs_traverse_for_edges(child)

    def get_alignments(self):
        nodes = self.get_nodes()
        span_list = []

        nodes_align = dict()

        warning_list = []   # recording nodes without valid alignment infomation
        for node in nodes:
            if node.aligned_pos == '':
                warning_list.append(node.concept)
                continue

            if node.aligned_pos not in nodes_align:
                nodes_align[node.aligned_pos] = []
            nodes_align[node.aligned_pos].append(node)


        alignments = []
        sentence_toks = self.amr_annotation.snt_toks_str.split()[1:]
        for span in nodes_align:
            span_nodes = nodes_align[span]

            # get corresponding word series
            start_index = int(span.split('-')[0])
            end_index = int(span.split('-')[1])
            span_words = sentence_toks[start_index:end_index]
                # it's said that all occurences of the same concept id(that means the same span) correspond
                # to exactly the same concept in annotation.
                # so we take the first node of this span to get its corresponding concept
            span_concept = span_nodes[0].concept
            span_list.append((span_words, span_concept))

            # span_alignment looks like: 21-22|0.3.2.2+0.3.2.2.1
            span_alignment = span + "|"
            for node in span_nodes:
                span_alignment += node.id + "+"
            span_alignment = span_alignment[:-1]
            alignments.append(span_alignment)

        return alignments, span_list, warning_list

    def check_cycle(self):
        node_positions = set()
        nodes = self.get_nodes_info()
        for node in nodes:
            if node.is_concept:
                node_pos = node.aligned_pos
                if node_pos in node_positions:
                    return True
                else:
                    node_positions.add(node_pos)
        return False

    def save_align_info(self, aligned_file, aligned_log_file):
        assert self.root != None

        # write ::id line
        aligned_file.write("# " + self.amr_annotation.sid + "\n")
        aligned_log_file.write("# " + self.amr_annotation.sid + "\n")

        # write ::snt and :: tok line
        aligned_file.write("# " + self.amr_annotation.snt_toks_str + "\n")
        aligned_log_file.write("# " + self.amr_annotation.snt_toks_str + "\n")
        toks = self.amr_annotation.snt_toks_str.split()[1:]
        aligned_file.write("# ::tok " + " ".join(toks) + "\n")
        aligned_log_file.write("# ::tok " + " ".join(toks) + "\n")

        alignments, span_list, warning_list = self.get_alignments()

        # write WARNING and Span infos into aligned_log_file
        for concept in warning_list:
            aligned_log_file.write("WARNING: Unaligned concept " + concept + "\n")

        # write span infos (words and concept alignment) into aligned_log_file
        for i, info in enumerate(span_list):
            aligned_log_file.write("Span " + str(i+1) + ":  " + " ".join(info[0]) + " => " + info[1] + "\n")

        # write alignments
        aligned_file.write("# ::alignments ")
        aligned_log_file.write("# ::alignments ")
        for align in alignments:
            aligned_file.write(align + " ")
            aligned_log_file.write(align + " ")

        time_info = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        aligned_file.write("::annotator Aligner gold ::date " + time_info + '\n')
        aligned_log_file.write("::annotator Aligner gold ::date " + time_info + '\n')

        # write nodes
        for node in self.get_nodes():
            aligned_file.write("# ::node")
            aligned_log_file.write("# ::node")
            aligned_file.write("\t" + node.id)
            aligned_log_file.write("\t" + node.id)
            aligned_file.write("\t" + node.concept)
            aligned_log_file.write("\t" + node.concept)
            aligned_file.write("\t" + node.aligned_pos + "\n")
            aligned_log_file.write("\t" + node.aligned_pos + "\n")

        # write root
        aligned_file.write("# ::root\t0\t")
        aligned_log_file.write("# ::root\t0\t")
        aligned_file.write(self.root.concept)
        aligned_log_file.write(self.root.concept)
        aligned_file.write("\n")
        aligned_log_file.write("\n")

        # write edges
        for edge in self.get_edges():
            aligned_file.write("# ::edge")
            aligned_log_file.write("# ::edge")
            aligned_file.write("\t" + edge.source_node.concept)
            aligned_log_file.write("\t" + edge.source_node.concept)
            aligned_file.write("\t" + edge.rel)
            aligned_log_file.write("\t" + edge.rel)
            aligned_file.write("\t" + edge.dest_node.concept)
            aligned_log_file.write("\t" + edge.dest_node.concept)
            aligned_file.write("\t" + edge.source_node.id)
            aligned_log_file.write("\t" + edge.source_node.id)
            aligned_file.write("\t" + edge.dest_node.id + "\n")
            aligned_log_file.write("\t" + edge.dest_node.id + "\n")

        # write amr_tree in string format
        for line in self.amr_annotation.amr_tree_lines:
            aligned_file.write(line)
            aligned_log_file.write(line)

        # write blank line between two sentences
        aligned_file.write("\n")
        aligned_log_file.write("\n")


def generate_align_info_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-gold_align_amr_file", type=str, dest="gold_align_amr_file", required=True)
    args = parser.parse_args()

    amr_file_path = args.gold_align_amr_file

    # extract alignment info and generate alignment files
    amr_file = open(amr_file_path)
    aligned_file = open(amr_file_path + ".aligned", "w")
    aligned_log_file = open(amr_file_path + ".aligned.log", "w")

    for amr_annotation in extract_amr_annotation_from_file(amr_file):
        amr_tree = AmrTree(amr_annotation)
        if len(amr_tree.amr_annotation.amr_tree_lines) > 0:
            amr_tree.parse()
            amr_tree.save_align_info(aligned_file, aligned_log_file)

    amr_file.close()
    aligned_file.close()


def extract_amr_annotation_from_file(amr_file):
    single_amr_annotation = AmrAnnotation()
    first_id_line = True

    for line in amr_file.readlines():
        if line.startswith("#"):
            line = line[1:].strip()

            if line.startswith("::id"):
                if first_id_line:
                    pass
                else:
                    yield single_amr_annotation
                    single_amr_annotation = AmrAnnotation()

                single_amr_annotation.sid = line
                first_id_line = False

            elif line.startswith("::snt"):
                single_amr_annotation.snt_toks_str = line
        else:
            if line.strip() != "":
                single_amr_annotation.amr_tree_lines.append(line)

    yield single_amr_annotation


generate_align_info_main()
