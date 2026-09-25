from predictor.ranker import predict_event_with_ranker, train_ranker
from predictor.test_ensemble import _frame


def test_ranker_returns_complete_order():
    train = _frame(races=12, drivers=12)
    prediction = train[train["gp"] == "Race 11"].drop(columns="finish_pos")
    ranker = train_ranker(train, n_estimators=20)
    out = predict_event_with_ranker(ranker, prediction)
    assert sorted(out["pred_rank"].tolist()) == list(range(1, len(out) + 1))
    assert sorted(out["pred_rank_model_ensemble"].tolist()) == list(range(1, len(out) + 1))
