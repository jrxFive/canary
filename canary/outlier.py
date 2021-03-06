import numpy as np
import falcon
import json

class Tukey(object):
    '''
        A timeseries is anomalous if any point is 1.5 times
        the interquartile range less than the first quartile or more than
        the third quartile.
    '''

    def on_get(self, req, resp):
        timeseries, tidx, vidx = utils.backend_retreival(req)
        self._run(req, resp, timeseries, tidx, vidx)

    def on_post(self, req, resp):
        timeseries, tidx, vidx = utils.backend_retreival(req)
        self._run(req, resp, timeseries, tidx, vidx)

    def _run(self, req, resp, timeseries, tidx, vidx):

        outlier_threshold = req.get_param_as_int("outlier_threshold",
                                                 required=False)

        if outlier_threshold:
            result = self._work(timeseries, tidx, vidx, outlier_threshold)
        else:
            result = self._work(timeseries, tidx=tidx, vidx=vidx)

        resp.body = json.dumps(result)
        resp.status = falcon.HTTP_200

    def _work(self, timeseries, tidx=0, vidx=1, outlier_threshold=1.5):
        series = np.array(timeseries)
        values = series[:,vidx]

        # Calculate quartiles and IQR
        q25, q75 = np.percentile(values, [25,75])
        iqr = q75 - q25

        # Lower and upper outlier boundaries
        low = q25 - (outlier_threshold * iqr)
        high = q75 + (outlier_threshold * iqr)

        # Indexes of outliers
        low_indexes = np.where(values < low)
        high_indexes = np.where(values > high)

        indexes = np.concatenate((low_indexes, high_indexes), axis=1)
        indexes = indexes.flatten()

        # Return timeseries of outliers
        return series[indexes].tolist()