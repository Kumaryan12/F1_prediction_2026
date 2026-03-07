import numpy as np
from scipy.stats import kendalltau, spearmanr

def order_to_pos(order):
    # order: list of driver ids/abbr; returns dict driver->position (1..n)
    return {d: i+1 for i, d in enumerate(order)}

def ndcg_at_k(true_order, pred_order, k=20):
    # relevance = inverse of true rank (higher = better)
    rel = {d: (len(true_order) - i) for i, d in enumerate(true_order)}
    def dcg(order):
        return sum(rel[d] / np.log2(i+2) for i, d in enumerate(order[:k]))
    ideal = dcg(true_order)
    return dcg(pred_order) / ideal if ideal > 0 else 0.0

def kendall_tau(true_order, pred_order):
    # compare permutations
    # convert both to index arrays on the union set
    idx = {d:i for i,d in enumerate(true_order)}
    a = np.array([idx[d] for d in pred_order if d in idx])
    b = np.arange(len(a))
    tau, _ = kendalltau(a, b)
    return float(tau)

def spearman_rho(true_order, pred_order):
    pos_t = order_to_pos(true_order)
    pos_p = order_to_pos(pred_order)
    common = [d for d in pos_t if d in pos_p]
    t = [pos_t[d] for d in common]
    p = [pos_p[d] for d in common]
    rho, _ = spearmanr(t, p)
    return float(rho)

def position_weighted_mae(true_pos, pred_pos):
    # penalize mistakes up front more
    wsum = err = 0.0
    for d, r in true_pos.items():
        if d not in pred_pos: continue
        w = 1.0 / r
        err += w * abs(pred_pos[d] - r)
        wsum += w
    return err / wsum if wsum > 0 else np.nan

def evaluate_full(true_order, pred_order):
    true_pos = order_to_pos(true_order)
    pred_pos = order_to_pos(pred_order)
    return {
        "kendall_tau": kendall_tau(true_order, pred_order),
        "spearman_rho": spearman_rho(true_order, pred_order),
        "ndcg@3": ndcg_at_k(true_order, pred_order, 3),
        "ndcg@10": ndcg_at_k(true_order, pred_order, 10),
        "ndcg@20": ndcg_at_k(true_order, pred_order, 20),
        "pw_mae": position_weighted_mae(true_pos, pred_pos),
    }
