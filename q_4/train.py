import argparse
import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--data",
        default="spam_dataset.csv"
    )

    parser.add_argument(
        "--out",
        default="model.joblib"
    )

    args = parser.parse_args()

    # Load dataset
    df = pd.read_csv(args.data)

    X = df["text"]
    y = df["label"]

    # Train/test split for evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # Required assignment model:
    # TF-IDF Vectorizer + Multinomial Naive Bayes
    model = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("classifier", MultinomialNB())
    ])

    # Train
    model.fit(X_train, y_train)

    # Evaluate
    preds = model.predict(X_test)

    accuracy = accuracy_score(y_test, preds)
    f1 = f1_score(
        y_test,
        preds,
        pos_label="spam"
    )

    print(
        f"accuracy={accuracy:.4f}  "
        f"f1={f1:.4f}"
    )

    # Retrain on all 1000 rows before saving
    model.fit(X, y)

    # Save model
    joblib.dump(model, args.out)

    print(f"Saved model to {args.out}")


if __name__ == "__main__":
    main()