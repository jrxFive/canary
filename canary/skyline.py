import pandas
import numpy as np
import scipy
import time
import falcon
import json

import backend
import utils


class MedianAbsoluteDeviation(object):
    """
    A timeseries is anomalous if the deviation of its latest datapoint with
    respect to the median is X times larger than the median of deviations.
    """
    # backend, ip, port, series, db=None, tags=None, start=None, end='-24h'

    def on_get(self, req, resp):
            timeseries, tidx, vidx = utils.backend_retreival(req)
            result = self._work(timeseries, tidx=tidx, vidx=vidx)

            resp.body = json.dumps(result)

    def on_post(self, req, resp):
        resp.status = falcon.HTTP_200

    def on_put(self, req, resp):
        resp.status = falcon.HTTP_200

    def _work(self, timeseries, deviation_threshold=6, tidx=0, vidx=1):

        series = pandas.Series([x[vidx] for x in timeseries])
        median = series.median()
        demedianed = np.abs(series - median)
        median_deviation = demedianed.median()

        # The test statistic is infinite when the median is zero,
        # so it becomes super sensitive. We play it safe and skip when this
        # happens.
        if median_deviation == 0:
            return False

        test_statistic = demedianed.iat[-1] / median_deviation

        # Completely arbitary...triggers if the median deviation is
        # 6 times bigger than the median
        if test_statistic > deviation_threshold:
            return True
        else:
            return False


class Grubbs(object):
    """
    A timeseries is anomalous if the Z score is greater than the Grubb's score.
    """

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        resp.status = falcon.HTTP_200

    def on_put(self, req, resp):
        resp.status = falcon.HTTP_200

    def _work(self, timeseries, tidx=0, vidx=1):

        series = scipy.array([x[vidx] for x in timeseries])
        stdDev = scipy.std(series)
        mean = np.mean(series)
        tail_average = _tail_avg(timeseries, tidx, vidx)
        z_score = (tail_average - mean) / stdDev
        len_series = len(series)
        threshold = scipy.stats.t.isf(.05 / (2 * len_series), len_series - 2)
        threshold_squared = threshold * threshold
        grubbs_score = ((len_series - 1) / np.sqrt(len_series)) * \
            np.sqrt(threshold_squared / (len_series - 2 + threshold_squared))

        return z_score > grubbs_score


class FirstHourAverage(object):
    """
    Calcuate the simple average over one hour, FULL_DURATION seconds ago.
    A timeseries is anomalous if the average of the last three datapoints
    are outside of three standard deviations of this value.
    """

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        resp.status = falcon.HTTP_200

    def on_put(self, req, resp):
        resp.status = falcon.HTTP_200

    def _work(self, timeseries, tidx=0, vidx=1, full_duration=86400):

        last_hour_threshold = time() - (full_duration - 3600)
        series = pandas.Series(
            [x[vidx] for x in timeseries if x[tidx] < last_hour_threshold])
        mean = (series).mean()
        stdDev = (series).std()
        t = _tail_avg(timeseries, tidx, vidx)

        return abs(t - mean) > 3 * stdDev


class StddevFromAverage(object):
    """
    A timeseries is anomalous if the absolute value of the average of the
    latestthree datapoint minus the moving average is greater than three
    standard deviations of the average. This does not exponentially
    weight the MA and so is better for detecting anomalies with respect
    to the entire series.
    """

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        resp.status = falcon.HTTP_200

    def on_put(self, req, resp):
        resp.status = falcon.HTTP_200

    def _work(self, timeseries, tidx=0, vidx=1):

        series = pandas.Series([x[vidx] for x in timeseries])
        mean = series.mean()
        stdDev = series.std()
        t = tail_avg(timeseries)

        return abs(t - mean) > 3 * stdDev
