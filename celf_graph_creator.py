import os, nltk
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.tag import pos_tag
import networkx as nx
import sys

# Helper functions:
def filter_words(key):
    return True if key.startswith('NN') or key.startswith('J') or key.startswith('VB') else False


# Reading all the files from the directory
dataset_dir = '../data/SemEval2010/test/'

print os.path.dirname(dataset_dir)
total_count = 0
read_count = 0
for subdir, dirs, files in os.walk(dataset_dir):
    # iterate over all files in train/test directory
    for file in files:
#==============================================================================
#         if not file.endswith('.txt'):
#             continue
#         if file.endswith('-justTitle.txt'):
#             print "JUST TITLE"
#             continue
#==============================================================================
#         f = open(subdir+'/'+file, 'r', encoding='utf-8')
        fopen = open(subdir+'/'+file, 'r')#, encoding="utf-8")
        text = fopen.read().decode('utf-8')

#==============================================================================
#         f = codecs.open(subdir+'/'+file, "r", "utf-8" )
#         text = f.read()
#==============================================================================
        print "Processing: ",file
        # tokenizing the text and filtering nouns / verbs etc
        tokens = nltk.word_tokenize(text)
        tokens_non_stop = [word for word in tokens if word not in stopwords.words('english')]

        filt_text = map(lambda key: key[0], filter(lambda key: filter_words(key[1]), pos_tag(tokens_non_stop)))
        
        # creating local maps for nodes and edges
        dict_text = defaultdict(int)
        for t in filt_text:
            dict_text[t] += 1
        edges, nodes, nodes_number = [], {}, {}
        c = 0
        for d in dict_text:
            if d in nodes:
                continue
            nodes[d] = c
            nodes_number[c] = d
            c += 1
            
        # create bi-directional edges for graph-of-words as required by CELF and CELF++
        k = min(10, len(filt_text)-1) ## window size
        for i in range(len(filt_text)-k):
            for j in range(i+1, i+k+1):
                wt = j-i  ## this is the weight of the edge (distance between words)
                edges.append((nodes[filt_text[i]], nodes[filt_text[j]]))
                edges.append((nodes[filt_text[j]], nodes[filt_text[i]]))
        total_count+=1
        celf_file_name = '../data/CELF_data_SemEval2010/'+'celf_'+file
        celf_file = open(celf_file_name, 'w')
#        try:
        G = nx.Graph()
#        print edges
        G.add_edges_from(edges)
        
            # calculate degree of each node, as this is needed by CELF

        G_degree = {}
        for node in G:
            G_degree[node] = G.degree(node)
        for line in edges:
                celf_file.write("%s\n" % (str(line[0])+" "+str(line[1])+" "+str(1.0/G_degree[line[1]])))
        read_count  += 1
        print "Processed: ", celf_file_name
        celf_file.close()
#==============================================================================
#         except:
#             e = sys.exc_info()[0]
#             print "Exception: ",e
#             print "Failed to process file: ",celf_file_name
#==============================================================================
            
print "Done!"
print "Total files processed: ", total_count
print "Files processed successfully: ",read_count


