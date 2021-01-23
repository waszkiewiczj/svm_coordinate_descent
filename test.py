#!/usr/local/bin/python
import sys
import getopt
import sklearn.datasets as skd
import sklearn.model_selection as skms
import sklearn.metrics as skm
import numpy as np
import pandas as pd

from coordinate_descent_svc import CoordinateDescentSVC, lbfgsbSVM


methods_dict = {
    "coordinate-descent": CoordinateDescentSVC,
    "lbfgsb": lbfgsbSVM
}


def test_method(method_name, samples, features, seed=None):
    assert method_name in methods_dict.keys(), "unknown method"
    assert type(samples) == int and samples > 0, "samples must be positive integer"
    assert type(features) == int and features > 0, "features must be positive integer"

    X, y = skd.make_classification(
        n_classes=2,
        n_samples=samples,
        n_features=features,
        random_state=seed
    )
    X_train, X_test, y_train, y_test = skms.train_test_split(X, y, train_size=0.8)
    results = []

    def callback(m):
        loss = m.loss(m.w, X_train, y_train) / len(X_train)
        loss_prime = np.sum(m.loss_prime(m.w, X_train, y_train) ** 2)
        acc1 = skm.accuracy_score(y_train, m.predict(X_train))
        acc2 = skm.accuracy_score(y_test, m.predict(X_test))
        results.append({
            "loss": loss,
            "loss_prime": loss_prime,
            "train_acc": acc1,
            "test_acc": acc2
        })
        print(f"loss: {loss:4.3f}, loss_prime: {loss_prime:8.2f}, train_acc: {acc1:4.3f}, test_acc: {acc2:4.3f}")

    method = methods_dict.get(method_name)(callback=callback)
    method.fit(X_train, y_train)
    results_df = pd.DataFrame(results)
    return results_df


def usage():
    msg = """
Usage: test [OPTION]
Test performance of selected method over selected data set.
    -f,    --features=NUMBER    Number of test data features
    -s,    --samples=NUMBER     Number of test data samples
    -m,    --method=NAME        Name of the method
    -r,    --random-seed=NUMBER Seed used to generate data
    -o,    --output=FILENAME    Name of output CSV file
"""
    print(msg)


def main():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hf:s:m:r:o:",
            ["help", "features=", "samples=", "method=", "random-seed=", "output="]
        )
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    method_name = features = samples = seed = output = None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-f", "--features"):
            features = int(a)
        elif o in ("-s", "--samples"):
            samples = int(a)
        elif o in ("-m", "--method"):
            method_name = a
        elif o in ("-r", "--random-seed"):
            seed = int(a)
        elif o in ("-o", "--output"):
            output = a
        else:
            assert False, "unhandled option"
    assert features, "features must be provided"
    assert samples, "samples must be provided"
    assert method_name, "method must be provided"
    results_df = test_method(method_name, samples, features, seed)
    if output:
        assert type(output) == str and output.endswith(".csv"), "output must be path to CSV file"
        results_df.to_csv(output)


if __name__ == "__main__":
    main()
