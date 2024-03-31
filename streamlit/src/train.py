import os

from sklearn.model_selection import train_test_split
from sklift.datasets import fetch_x5, clear_data_dir
import pandas as pd
from sklift.viz import plot_uplift_curve
import boto3
import joblib
import tempfile


class UpliftPipeline:
    def __init__(self, features_path, train_path):
        self.features_path = features_path
        self.train_path = train_path

    @property
    def data_loaded(self):
        return os.path.exists(self.features_path) and os.path.exists(self.train_path)

    def load_model(self, key):
        session = boto3.session.Session()
        s3 = session.client(
            service_name="s3",
            endpoint_url="https://storage.my_s3_storage.com",
        )

        with tempfile.TemporaryFile() as fp:
            s3.download_fileobj(Fileobj=fp, Bucket="BUCKET_NAME", Key=key)
            fp.seek(0)
            model = joblib.load(fp)

        self.model = model

    def load_data(self):
        clear_data_dir()
        dataset = fetch_x5()

        data, target, treatment = dataset.data, dataset.target, dataset.treatment

        random_indexes = target.sample(frac=0.8).index.values

        data["clients"] = data["clients"].iloc[random_indexes].reset_index()
        data["train"] = data["train"].iloc[random_indexes].reset_index()
        target = target.iloc(random_indexes).reset_index()
        treatment = treatment.iloc(random_indexes).reset_index()

        df_clients = data["clients"].set_index("client_id")
        df_train = pd.concat([data["train"], treatment, target], axis=1).set_index(
            "client_id"
        )

        df_features = df_clients
        df_features["first_issue_time"] = (
            pd.to_datetime(df_features["first_issue_date"]) - pd.Timestamp("1970-01-01")
        ) // pd.Timedelta("1s")
        df_features["first_redeem_time"] = (
            pd.to_datetime(df_features["first_redeem_date"])
            - pd.Timestamp("1970-01-01")
        ) // pd.Timedelta("1s")
        df_features["issue_redeem_delay"] = (
            df_features["first_redeem_time"] - df_features["first_issue_time"]
        )
        df_features = df_features.drop(
            ["first_issue_date", "first_redeem_date"], axis=1
        )

        df_features.to_parquet(self.features_path)
        df_train.to_parquet(self.train_path)

    def make_train_test_split(self, test_size):
        self.df_features = pd.read_parquet(self.features_path)
        self.df_train = pd.read_parquet(self.train_path)
        indices_learn, indices_valid = train_test_split(
            self.df_train.index, test_size=test_size, random_state=123
        )
        indices_test = pd.Index(set(self.df_features.index) - set(self.df_train.index))

        self.X_train = self.df_features.loc[indices_learn, :]
        self.y_train = self.df_train.loc[indices_learn, "target"]
        self.treat_train = self.df_train.loc[indices_learn, "treatment_flg"]

        self.X_val = self.df_features.loc[indices_valid, :]
        self.y_val = self.df_train.loc[indices_valid, "target"]
        self.treat_val = self.df_train.loc[indices_valid, "treatment_flg"]

        self.X_test = self.df_features.loc[indices_test, :]

    def train_model(self, init_model, **kwargs):
        self.model = init_model.fit(
            self.X_train,
            self.y_train,
            self.treat_train,
            **kwargs,
        )

    def evaluate_model(self):
        uplift_preds = self.model.predict(self.X_val)

        return plot_uplift_curve(
            y_true=self.y_val,
            uplift=uplift_preds,
            treatment=self.treat_val,
            perfect=False,
        ).figure_
