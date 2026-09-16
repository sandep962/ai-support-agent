import argparse, json
from pathlib import Path
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", default="evaluation/golden_set.csv")
    ap.add_argument("--majority-label", default=None)
    args = ap.parse_args()

    df = pd.read_csv(args.golden)
    y = df["human_label"].astype(str)
    majority = args.majority_label or y.mode().iloc[0]
    pred = [majority] * len(y)

    p, r, f1, _ = precision_recall_fscore_support(
        y, pred, average="macro", zero_division=0
    )
    result = {
        "model": "majority_baseline",
        "majority_label": majority,
        "n": len(y),
        "accuracy": accuracy_score(y, pred),
        "macro_precision": p,
        "macro_recall": r,
        "macro_f1": f1,
    }
    Path("results").mkdir(exist_ok=True)
    Path("results/majority_intent.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
