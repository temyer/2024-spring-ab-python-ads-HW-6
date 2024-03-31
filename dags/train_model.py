from sklift.models import SoloModel, TwoModels
from catboost import CatBoostClassifier
from sklift.datasets import fetch_x5
import pandas as pd
import boto3
import joblib
import tempfile


def get_data():
    print("Downloading data...")
    dataset = fetch_x5()
    print("Data downloaded successfully")

    data, target, treatment = dataset.data, dataset.target, dataset.treatment

    df_clients = data["clients"].set_index("client_id")
    df_train = pd.concat([data["train"], treatment, target], axis=1).set_index(
        "client_id"
    )

    df_features = df_clients
    df_features["first_issue_time"] = (
        pd.to_datetime(df_features["first_issue_date"]) - pd.Timestamp("1970-01-01")
    ) // pd.Timedelta("1s")
    df_features["first_redeem_time"] = (
        pd.to_datetime(df_features["first_redeem_date"]) - pd.Timestamp("1970-01-01")
    ) // pd.Timedelta("1s")
    df_features["issue_redeem_delay"] = (
        df_features["first_redeem_time"] - df_features["first_issue_time"]
    )
    df_features = df_features.drop(["first_issue_date", "first_redeem_date"], axis=1)

    random_indexes = df_features.sample(frac=0.8).index.values

    X_train = df_features.loc[random_indexes, :]
    y_train = df_train.loc[random_indexes, "target"]
    treat_train = df_train.loc[random_indexes, "treatment_flg"]

    print("Data processed successfully")

    return X_train, y_train, treat_train


def train_solo_model(data, params):
    print("Training solo model...")

    init_model = SoloModel(estimator=CatBoostClassifier(**params))

    X_train, y_train, treat_train = data

    model = init_model.fit(
        X_train, y_train, treat_train, estimator_fit_params={"cat_features": ["gender"]}
    )

    print("Solo model training has been finished")

    return model


def train_two_model(data, params):
    print("Training two model...")

    init_model = TwoModels(
        estimator_trmnt=CatBoostClassifier(**params),
        estimator_ctrl=CatBoostClassifier(**params),
        method="vanilla",
    )

    X_train, y_train, treat_train = data

    model = init_model.fit(
        X_train, y_train, treat_train, estimator_fit_params={"cat_features": ["gender"]}
    )

    print("Two model training has been finished")

    return model


def log_model_to_s3(model, key):
    print("Logging model %s to s3" % key)

    session = boto3.session.Session()
    s3 = session.client(
        service_name="s3",
        endpoint_url="https://storage.my_s3_storage.com",
    )

    with tempfile.TemporaryFile() as fp:
        joblib.dump(model, fp)
        fp.seek(0)
        s3.put_object(Body=fp.read(), Bucket="BUCKET_NAME", Key=key)

    print("Model logged successfully to %s" % key)


def main():
    params = {
        "iterations": 20,
        "thread_count": 2,
        "random_state": 42,
        "silent": True,
    }

    data = get_data()

    solo_model = train_solo_model(data, params)
    two_model = train_two_model(data, params)

    log_model_to_s3(solo_model, "solo_model")
    log_model_to_s3(two_model, "two_model")
