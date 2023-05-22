
from urllib.parse import urlparse, ParseResult
import re

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class UrlFeatureExtractor(TransformerMixin, BaseEstimator):
    _sheme_pat = re.compile(r"^\w*:?//.+")
    _ip_pat = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?$")
    _url_parts = ["scheme", "netloc", "path", "query"]

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return self.extract_features(X)

    def fit_transform(self, X, y=None):
        return self.transform(X)

    def extract_features(self, X: pd.DataFrame) -> pd.DataFrame:
        features = pd.DataFrame(
            index=X.index
        )
        features["len"] = X.url.str.len()
        features[self._url_parts] = self._extract_url_parts(X.url)
        features["is_ip"] = features.netloc.apply(self.is_ip)
        features["domain_level"] = features.netloc.str.count("\.") + 1
        features["domain_len"] = features.netloc.str.len()
        features["has_port"] = features.netloc.str.contains(r":\d+").astype(int)
        features["path_level"] = features.path.str.count("/")
        features["path_len"] = features.path.str.len()
        features["num_query_params"] = features["query"].str.count("&")
        features["query_len"] = features["query"].str.len()
        features["count_%"] = X.url.str.count("%")

        return features


    def _extract_url_parts(self, urls:pd.Series) -> pd.DataFrame:
        parsed_urls = urls.apply(self._parse_url)
        df =  parsed_urls.apply(pd.Series)
        df.columns = ["scheme", "netloc", "path", "params", "query", "fragment"]
        return df[self._url_parts]
    
    def _parse_url(self, url: str) -> ParseResult:
        try:
            if self._sheme_pat.match(url):
                return urlparse(url)
            else:
                return urlparse("//" + url)
        except Exception as e:
            return ParseResult("", "", "", "", "", "")

    def is_ip(self, netloc: str) -> int:
        return 1 if self._ip_pat.match(netloc) else 0

    def get_feature_names_out(self, names_in) -> list:
        return [
            "len",
            "scheme",
            "netloc",
            "path",
            "params",
            "query",
            "fragment",
            "is_ip",
            "domain_level",
            "domain_len",
            "has_port",
            "path_level",
            "path_len",
            "num_query_params",
            "query_len",
            "count_%",
        ]


def to_array(X):
    return X.toarray()
