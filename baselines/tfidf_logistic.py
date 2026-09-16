import argparse, json
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support, classification_report,
    confusion_matrix
)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", default="data/silver_train.csv")
    ap.add_argument("--golden", default="evaluation/golden_set.csv")
    args = ap.parse_args()

    train = pd.read_csv(args.train)
    gold = pd.read_csv(args.golden)

    train = train.dropna(subset=["customer_text","human_label"])
    gold = gold.dropna(subset=["customer_text","human_label"])

    X_train = train["customer_text"].astype(str)
    y_train = train["human_label"].astype(str)
    X_test = gold["customer_text"].astype(str)
    y_test = gold["human_label"].astype(str)

    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True,
            ngram_range=(1,2),
            min_df=2,
            max_df=0.98,
            sublinear_tf=True
        )),
        ("lr", LogisticRegression(
            max_iter=2000,
            class_weight="balanced"
        ))
    ])

    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    p, r, f1, _ = precision_recall_fscore_support(
        y_test, pred, average="macro", zero_division=0
    )
    report = classification_report(y_test, pred, output_dict=True, zero_division=0)
    labels = sorted(y_test.unique().tolist())
    cm = confusion_matrix(y_test, pred, labels=labels)

    result = {
        "model": "tfidf_logistic_regression",
        "train_rows": len(train),
        "golden_rows": len(gold),
        "accuracy": accuracy_score(y_test, pred),
        "macro_precision": p,
        "macro_recall": r,
        "macro_f1": f1,
        "labels": labels,
        "confusion_matrix": cm.tolist(),
        "classification_report": report
    }

    Path("results").mkdir(exist_ok=True)
    Path("results/tfidf_logistic_intent.json").write_text(
        json.dumps(result, indent=2)
    )
    print(json.dumps({
        k: result[k] for k in
        ["model","train_rows","golden_rows","accuracy",
         "macro_precision","macro_recall","macro_f1"]
    }, indent=2))

if __name__ == "__main__":
    main()
