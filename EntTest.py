import pickle
import networkx as nx
import matplotlib.pyplot as plt
from fuzzywuzzy.process import dedupe
import pandas as pd
import json

#constant for filtering special characters
SPECIAL = "!@#$%^&*()-+?_=,<>/"

"""
function takes a list of [list of entities] and computes a dictionary with edge information encoded in a dictionary
"""
def create_edges_graph(ent):
    entitites_edges_map = {}
    for entity_list in ent:
        for ele in entity_list:
            for other in entity_list:
                if ele == other:
                    continue
                if ele in entitites_edges_map:
                    if other in entitites_edges_map[ele]:
                        entitites_edges_map[ele][other] += 1
                        entitites_edges_map[other][ele] += 1
                    else:
                        entitites_edges_map[ele][other] = 1
                        if other in entitites_edges_map:
                            entitites_edges_map[other][ele] = 1
                        else:
                            entitites_edges_map[other] = {ele: 1}
                else:
                    entitites_edges_map[ele] = {other: 1}
                    if other in entitites_edges_map:
                        entitites_edges_map[other][ele] = 1
                    else:
                        entitites_edges_map[other] = {ele: 1}
    return entitites_edges_map


"""
function takes a list of [list of entities] and computes a dictionary of the frequencies of entities
"""
def count_entities(entity_list_list):
    ent_dict = {}
    for entity_list in entity_list_list:

        for e in entity_list:

            if e in ent_dict:
                ent_dict[e] += 1
            else:
                ent_dict[e] = 1
    return ent_dict

"""
dic is the frequency dictionary, num is how many entries you want. returns that many entities
"""
def maxEntities(dic, num):
    return sorted(dic, key=dic.get, reverse=True)[:num], dic

"""
to help format for making network graphs in matplot lib
"""
def getFromTo(edge_dic):
    from_list = []
    to_list = []
    for key in edge_dic:
        for edge in edge_dic[key]:
            from_list.append(key)
            to_list.append(edge)

    return from_list, to_list

def create_nodes(freq, in_use_words):
    """
    create node list
    """
    l = []
    for word in in_use_words:

        d = {}
        d['id'] = word
        d['name'] = word
        d['size'] = freq[word]
        l.append(d)
    return l

def create_edges(edge_dic):
    """
    create edge list
    """
    l =[]
    used_pairs = {}
    for key in edge_dic:
        for edge in edge_dic[key]:
            if (key,edge) in used_pairs or (edge,key) in used_pairs or edge_dic[key][edge] <= 10:
                continue

            used_pairs[(key,edge)] = 1
            dic_temp = {'source': key, 'target': edge}
            l.append(dic_temp)

    return l

def create_json(edge_dic, ent, freq):
    """
    create json of edges and node info for use in js/tablaeau
    """
    dic = {"nodes":create_nodes(freq, ent), "links":create_edges(edge_dic)}
    with open("nodes_edges.json", "w") as outfile:
        json.dump(dic, outfile)


def apply_filter(ent):
    """
    filter out many entities
    """
    ent = [x for x in ent if x[0].count(' ') < 2 and not any(c.isdigit() for c in x[0]) and not any(c in SPECIAL for c in x[0]) and str(x[1]) in ["Type.PERSON", "Type.OTHER", "Type.ORGANIZATION"]]
    temp_dic = {}
    temp_ent = []
    for i in ent:
        temp_dic[i[0]] = i[1]
        temp_ent.append(i[0])
    temp_ent = list(dedupe(temp_ent, threshold=90))
    ent = [[x, temp_dic[x]] for x in temp_ent]
    return ent

def get_freq(ent):
    """
    simple frequency computer of entities
    """
    freq = {}
    for entity_list in ent:
        for l in entity_list:

            if l[0] in freq:
                freq[l[0]] += 1
            else:
                freq[l[0]] = 1
    return freq


def network(df, frequency_dic, edge_dic):
    """
    generate a network graph in matplotlib
    """
    # Build your graph
    G = nx.from_pandas_edgelist(df, 'from', 'to')
    d = nx.degree(G)
    pos = nx.spring_layout(G, k=3)
    nodelist = G.nodes
    widths = G.edges
    # Plot it
    # nx.draw(G, with_labels=True, node_size=[frequency_dic[v[0]] * 100 for v in d])
    nx.draw_networkx_nodes(G, pos,
                           nodelist,
                           node_size=[frequency_dic[v[0]] * 80 for v in d],
                           node_color='black',
                           alpha=1)

    nx.draw_networkx_edges(G, pos,
                           edgelist=widths,
                           width=[.05 * edge_dic[v][w] for (v, w) in widths],  # needs to change
                           edge_color='blue',
                           alpha=1)
    nx.draw_networkx_labels(G, pos,
                            labels=dict(zip(nodelist, nodelist)),
                            font_color='white')
    plt.box(False)
    plt.show()

def generate_freq_processed_ents():
    nyt_files = ['Entities_with_type22', 'Entities_with_type23']
    root = 'Entities_with_type'
    ent = []
    c = 0
    for f in nyt_files:

        fileobj = open(root + '/' + f + '.txt', 'rb')
        e_list = pickle.load(fileobj)
        e_list = [apply_filter(x) for x in e_list]
        if c == 0:
            ent = e_list
        else:
            ent = [item for sublst in zip(ent, e_list) for item in sublst]

        fileobj.close()

    # do steps to reduce size of lists....... then create dict and graph
    freq = get_freq(ent)

    fileobj = open('frequencies_AZ.txt', 'wb')
    pickle.dump(freq, fileobj)
    fileobj.close()
    fileobj = open('processed_entities_AZ.txt', 'wb')
    pickle.dump(ent, fileobj)
    fileobj.close()

    df = pd.DataFrame.from_dict(freq, orient='index', columns=['frequency'])
    df.sort_values('frequency', axis=0, inplace=True, ascending=False)
    df.to_csv('AZ_frequencies.csv')





def main():
    #read in entity and frequency objects
    generate_freq_processed_ents()
    fileobj = open('frequencies_AZ.txt', 'rb')
    freq = pickle.load(fileobj)
    fileobj.close()
    fileobj = open('processed_entities_AZ.txt', 'rb')
    ent = pickle.load(fileobj)
    fileobj.close()
    ele = list(freq.keys())

    df = pd.DataFrame(columns=['word', 'frequency'])
    df['word'] = ele
    df['frequency'] = [freq[x] for x in ele]
    df.sort_values('frequency', axis=0, inplace=True, ascending=False)


    count = 0
    for_use_words = []

    for w in df['word']:
        if count == 40:
            break
        print(w)
        x = input('press y to accept: ')
        if x == 'y':
            for_use_words.append(w)
            count += 1

    print(for_use_words)

    new_df = pd.DataFrame(columns=['word', 'frequency'])
    new_df['word'] = for_use_words
    new_df['frequency'] = [freq[x] for x in for_use_words]
    new_df.sort_values('frequency', axis=0, inplace=True, ascending=False)
    new_df.to_csv('AZ_frequenciestrial.csv')
    print(new_df)


    ent = [[k[0] for k in x] for x in ent]

    #for_use_words = list(df['word'][:100])

    #somehow need to intersect ent with the dataframe
    reduced = [list(set(x).intersection(for_use_words)) for x in ent]

    edge_dict = create_edges_graph(reduced)


    create_json(edge_dict, for_use_words, freq)


main()

