# import unicodecsv
import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms import community

# Computed only once
# row = []
# with open('casts.csv', 'r') as f:
#    tmp = unicodecsv.reader(f, delimiter=';', encoding="utf-8")
#    for line in tmp:
#        # Filtering outliers
#        if(len(line[0]) > 1 and len(line[0]) < 6):
#            row.append(line)
# actorsAndMovies = {}
# for i in range(len(row)):
#    if(row[i][2] not in actorsAndMovies):
#        name = row[i][2]
#        tmp = []
#        for j in range(len(row)):
#            if(row[j][2] == row[i][2] and
#               row[j][1] not in tmp):
#                tmp.append(row[j][1])
#        actorsAndMovies[name] = tmp
# save = open("save.txt", "w")
# for actor in actorsAndMovies:
#    line = actor.encode('utf-8') + ";"
#    word = str(actorsAndMovies[actor]).encode('utf-8') + "\n"
#    save.write(line+word)

text = None
with open("save.txt", "r") as f:
    text = f.read()
    text = text.split("\n")
# We got a '' because of split("\n") so we delete this element
del text[-1]
tab = []
for line in text:
    line = line.split(";")
    # removing space betwen ":"
    line[1] = line[1].replace('u', '')
    line[1] = line[1].replace('[', '')
    line[1] = line[1].replace(']', '')
    tab.append(line)
# deleting first element because it is the actor " " so no meaning keeping this
del tab[0]
for i in range(len(tab)):
    tab[i][1] = tab[i][1].split(",")
    # we remove blank space after the comma
    tab[i][1] = [word.strip() for word in tab[i][1]]

# Creating the graph now
G = nx.Graph()
for i in range(len(tab)):
    G.add_node(tab[i][0], label=tab[i][0])
    for j in range(i+1, len(tab)):
        for movie in tab[j][1]:
            if(movie in tab[i][1]):
                G.add_edge(tab[i][0], tab[j][0], label=movie, weight=1)
print("Number of nodes: %s" % nx.number_of_nodes(G))
print("Number of edges: %s" % nx.number_of_edges(G))
print("Density: %s" % nx.density(G))
arrays = []
for component in nx.connected_components(G):
    arrays.append(list(component))
i = 0
for array in arrays:
    i += 1
print("Number of components: %s" % i)

centralities = [nx.degree_centrality, nx.eigenvector_centrality]
# closeness centrality, betweeness centrality don't work, it gets stuck
largest_cc = max(nx.connected_components(G), key=len)
subgraph = G.subgraph(largest_cc)
centralTab = {}
for centrality in centralities:
    topNode = []
    print(centrality.__name__)
    result = centrality(G)
    for k in result:
        valueWithIndex = [result[k], k]
        topNode = sorted(topNode, key=lambda value: value[0],
                         reverse=True)[:10]
        topNode.append(valueWithIndex)
    print(topNode)
    centralTab[centrality.__name__] = topNode
print(centralTab)

communities = {node: cid+1 for cid, community in
               enumerate(community.k_clique_communities(G, 3))
               for node in community}
sortedCommunities = sorted(communities.values())
nbPeopleInCommunity = []
counter = 0
for k in range(len(sortedCommunities)):
    value = sortedCommunities[k]
    counter += 1
    if(value != sortedCommunities[k+1]):
        nbPeopleInCommunity.append([value, counter])
        counter = 0
    if(value == sortedCommunities[-1]):
        for j in range(k, len(sortedCommunities)):
            counter += 1
        nbPeopleInCommunity.append([value, counter])
        break
topNb = sorted(nbPeopleInCommunity, key=lambda value: value[1],
               reverse=True)[:10]
print(topNb)


# Kevin Bacon himself has a Bacon number of 0.
# Those actors who have worked directly with Kevin Bacon
# have a Bacon number of 1.
# If the lowest Bacon number of any actor with whom X
# has appeared in any movie is N, X's Bacon number is N+1.


def findActorsFromMovie(movie, tab, kevinBaconTab, iterator):
    actors = []
    for i in range(len(tab)):
        if(movie in tab[i][1] and tab[i][0] in kevinBaconTab):
            if(kevinBaconTab[tab[i][0]] != iterator):
                actors.append(tab[i][0])
    return actors


kevinBaconTab = {}
allActors = {}
for i in range(len(tab)):
    allActors[tab[i][0]] = tab[i][1]
kevinBaconMovie = allActors["Kevin Bacon"]
for i in range(len(tab)):
    if(tab[i][0] == "Kevin Bacon"):
        kevinBaconTab[tab[i][0]] = 0
        allActors.pop('Kevin Bacon', None)
    else:
        for j in range(len(tab[i][1])):
            if(tab[i][1][j] in kevinBaconMovie):
                kevinBaconTab[tab[i][0]] = 1
                allActors.pop(tab[i][0], None)
iterator = 2
while(len(allActors) != 0):
    print(len(allActors))
    actorToDelete = []
    for actor in allActors:
        if(actor not in kevinBaconTab):
            for j in range(len(allActors[actor])):
                actors = findActorsFromMovie(allActors[actor][j], tab,
                                             kevinBaconTab, iterator)
                if(len(actors) != 0):
                    kevinBaconTab[actor] = iterator
                    actorToDelete.append(actor)
                    break
    for i in range(len(actorToDelete)):
        allActors.pop(actorToDelete[i], None)
    if(iterator == 6):
        break
    iterator += 1
# print(kevinBaconTab)
avg = 0
for actor in kevinBaconTab:
    avg += kevinBaconTab[actor]
avg /= float(len(kevinBaconTab))
print(avg)
highestActors = sorted(kevinBaconTab.items(), key=lambda x: x[1],
                       reverse=True)[:10]
print(highestActors)
lowestActors = sorted(kevinBaconTab.items(), key=lambda x: x[1])[:10]
print(lowestActors)

# Visualization
connected = sorted(nx.connected_components(G), key=len)
print(list(connected[len(connected)-2]))
subgraph = G.subgraph(list(connected[len(connected)-2]))
centralities = [nx.degree_centrality, nx.eigenvector_centrality]
plt.figure(figsize=(15, 5))
region = 120
pos = nx.spring_layout(subgraph)
for centrality in centralities:
    region += 1
    plt.subplot(region)
    plt.title(centrality.__name__)
    nx.draw(subgraph, pos, labels={v: str(v) for v in subgraph},
            cmap=plt.get_cmap("bwr"), node_color=[centrality(subgraph)[k]
            for k in
            centrality(subgraph)], node_size=20, font_size=8, linewidths=0.4,
            width=0.15)
plt.savefig("centralities.png")
# nx.write_gexf(G, "export.gexf")
subgraphForGephi = nx.Graph()
for i in range(50):
    subgraphForGephi.add_node(tab[i][0], label=tab[i][0])
    for j in range(i+1, len(tab)):
        for movie in tab[j][1]:
            if(movie in tab[i][1]):
                subgraphForGephi.add_edge(tab[i][0], tab[j][0],
                                          label=movie, weight=1)
nx.write_gexf(subgraphForGephi, "export1.gexf")
