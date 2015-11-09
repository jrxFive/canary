import numpy as np
import falcon
import json

class Tukey(object):
    '''
        A timeseries is anomalous if the last data point is 1.5 times
        the interquartile range less than the first quartile or more than
        the third quartile.
    '''

    def on_get(self, req, resp):
        timeseries, tidx, vidx = utils.backend_retreival(req)
        result = self._work(timeseries, tidx=tidx, vidx=vidx)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(result)

    def on_post(self, req, resp):
        resp.status = falcon.HTTP_200

    def on_put(self, req, resp):
        resp.status = falcon.HTTP_200

    def _work(self, timeseries, outlier_threshold=1.5, tidx=0, vidx=1):
        series = np.array([x[vidx] for x in timeseries])

        # Calculate quartiles and IQR
        q25, q75 = np.percentile(series, [25,75])
        iqr = q75 - q25

        # Lower and upper outlier boundaries
        low = q25 - (outlier_threshold * iqr)
        high = q75 + (outlier_threshold * iqr)

        # Indexes of outliers
        low_indexes = np.where(series < low)
        high_indexes = np.where(series > high)

        indexes = np.concatenate((low_indexes, high_indexes), axis=1)

        length = np.shape(series)[0]

        # Return true if the last index in series is anomalous
        return np.in1d(length - 1, indexes)[0]