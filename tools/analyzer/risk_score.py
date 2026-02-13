from collections import Counter

def score_files(graph, dynamic, quarantined):
    score = Counter()

    for f, deps in graph.items():
        for d in deps:
            score[d] += 2

    for f, _, _ in dynamic:
        score[f] += 3

    for f in quarantined:
        score[f] += 5

    return score
