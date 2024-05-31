from wikes_toolkit import WikESToolkit, V1

toolkit = WikESToolkit()
G = toolkit.load_graph(V1.First.SMALL_FULL)

root_nodes = G.root_entities()
nodes = G.entities()
edges = G.triples()
labels = G.predicates()
number_of_nodes = G.count_entities()
number_of_edges = G.count_triples()
node = G.fetch_entity('Q303')
neighbors = G.neighbors(node)
neighbors = G.neighbors('Q303')
ground_truth_summaries = G.ground_truth_summaries(root_nodes[0])
ground_truth_summaries = G.ground_truth_summaries('Q303')
G.mark_triple_as_summary(root_nodes[0], edges[0])
G.mark_triple_as_summary(root_nodes[0], ('Q303', 'P241', 'Q9212'))
G.mark_triple_as_summary('Q303', ('Q303', 'P264', 'Q898618'))
G.mark_triples_as_summaries(root_nodes[1], [G.neighbors(root_nodes[1])[0], G.neighbors(root_nodes[1])[1]])

for root in G.root_entities():
    print(f"Neighbors of [{root.wikidata_label}]:")
    for edge in G.neighbors(root):
        print(
            f"('{edge.subject_entity.wikidata_label}'= {edge.predicate.predicate_label} => {edge.object_entity.wikidata_label})")

    for _ in range(5):
        print("*"*40)

    print("Ground truth summaries:")
    for summary in G.ground_truth_summaries(root):
        print(
            f"('{summary.subject_entity.wikidata_label}'= {summary.predicate.predicate_label} => {summary.object_entity.wikidata_label})")
    G.mark_triples_as_summaries(root, G.neighbors(root))
    break
