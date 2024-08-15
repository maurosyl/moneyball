def compare_distributions(d1, d2):
    assert len(d1) == len(d2)
    l = len(d1)
    d1 = d1/sum(d1)
    d2 = d2 / sum(d2)

    accumul_prob2 = 0
    prob_12 = 0
    prob_equal = 0
    for i in range(0,l):
        prob_equal += d1[i]*d2[i]
        if i == 0:
            continue
        accumul_prob2 += d2[i-1]
        prob_12 += d1[i]*accumul_prob2
    prob_21 = 1 - prob_12 - prob_equal
    return prob_12, prob_equal, prob_21






