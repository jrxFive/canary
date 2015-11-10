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

    def on_get(self, req, resp):

        timeseries, tidx, vidx = utils.backend_retreival(req)
        self._run(req, resp, timeseries, tidx, vidx)

    def on_post(self, req, resp):

        timeseries, tidx, vidx = utils._non_backend_call(req)
        self._run(req, resp, timeseries, tidx, vidx)

    def _run(self, req, resp, timeseries, tidx, vidx):

        deviation_threshold = req.get_param_as_int("deviation_threshold",
                                                   required=False)

        if deviation_threshold:
            result = self._work(timeseries, tidx, vidx, deviation_threshold)
        else:
            result = self._work(timeseries, tidx=tidx, vidx=vidx)

        resp.body = json.dumps(result)
        resp.status = falcon.HTTP_200

    def _work(self, timeseries, tidx=0, vidx=1, deviation_threshold=6):

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

        timeseries, tidx, vidx = utils.backend_retreival(req)
        self._run(req, resp, timeseries, tidx, vidx)

    def on_post(self, req, resp):

        timeseries, tidx, vidx = utils._non_backend_call(req)
        self._run(req, resp, timeseries, tidx, vidx)

    def _run(self, req, resp, timeseries, tidx, vidx):

        result = self._work(timeseries, tidx=tidx, vidx=vidx)

        resp.body = json.dumps(result)
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

        timeseries, tidx, vidx = utils.backend_retreival(req)
        self._run(req, resp, timeseries, tidx, vidx)

    def on_post(self, req, resp):

        timeseries, tidx, vidx = utils._non_backend_call(req)
        self._run(req, resp, timeseries, tidx, vidx)

    def _run(self, req, resp, timeseries, tidx, vidx):

        full_duration = req.get_param_as_int("full_duration",
                                             required=False)

        if full_duration:
            result = self._work(timeseries, tidx, vidx, full_duration)
        else:
            result = self._work(timeseries, tidx=tidx, vidx=vidx)

        resp.body = json.dumps(result)
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

        timeseries, tidx, vidx = utils.backend_retreival(req)
        self._run(req, resp, timeseries, tidx, vidx)

    def on_post(self, req, resp):

        timeseries, tidx, vidx = utils._non_backend_call(req)
        self._run(req, resp, timeseries, tidx, vidx)

    def _run(self, req, resp, timeseries, tidx, vidx):

        result = self._work(timeseries, tidx=tidx, vidx=vidx)

        resp.body = json.dumps(result)
        resp.status = falcon.HTTP_200

    def _work(self, timeseries, tidx=0, vidx=1):

        series = pandas.Series([x[vidx] for x in timeseries])
        mean = series.mean()
        stdDev = series.std()
        t = tail_avg(timeseries)

        return abs(t - mean) > 3 * stdDev


class StddevFromMovingAverage(object):
    """
    A timeseries is anomalous if the absolute value of the average of
    the latest three datapoint minus the moving average is greater than
    three standard deviations of the moving average. This is better for
    finding anomalies with respect to the short term trends.
    """

    def on_get(self, req, resp):

        timeseries, tidx, vidx = utils.backend_retreival(req)
        self._run(req, resp, timeseries, tidx, vidx)

    def on_post(self, req, resp):

        timeseries, tidx, vidx = utils._non_backend_call(req)
        self._run(req, resp, timeseries, tidx, vidx)

    def _run(self, req, resp, timeseries, tidx, vidx):

        com = req.get_param_as_int("com",
                                   required=False)

        if com:
            result = self._work(timeseries, tidx, vidx, com)
        else:
            result = self._work(timeseries, tidx=tidx, vidx=vidx)

        result = self._work(timeseries, tidx=tidx, vidx=vidx)

        resp.body = json.dumps(result)
        resp.status = falcon.HTTP_200

    def _work(self, timeseries, tidx=0, vidx=1, com=50):

        series = pandas.Series([x[vidx] for x in timeseries])
        expAverage = pandas.stats.moments.ewma(series, com=com)
        stdDev = pandas.stats.moments.ewmstd(series, com=com)

        return abs(series.iat[-1] - expAverage.iat[-1]) > 3 * stdDev.iat[-1]


class MeanSubtractionCumulation(object):
    """
    A timeseries is anomalous if the value of the next datapoint in the
    series is farther than three standard deviations out in cumulative terms
    after subtracting the mean from each data point.
    """

    def on_get(self, req, resp):

        timeseries, tidx, vidx = utils.backend_retreival(req)
        self._run(req, resp, timeseries, tidx, vidx)

    def on_post(self, req, resp):

        timeseries, tidx, vidx = utils._non_backend_call(req)
        self._run(req, resp, timeseries, tidx, vidx)

    def _run(self, req, resp, timeseries, tidx, vidx):

        com = req.get_param_as_int("com",
                                   required=False)

        if com:
            result = self._work(timeseries, tidx, vidx, com)
        else:
            result = self._work(timeseries, tidx=tidx, vidx=vidx)

        result = self._work(timeseries, tidx=tidx, vidx=vidx)

        resp.body = json.dumps(result)
        resp.status = falcon.HTTP_200

    def _work(self, timeseries, tidx=0, vidx=1, com=15):

        series = pandas.Series([x[vidx] if x[vidx] else 0 for x in timeseries])
        series = series - series[0:len(series) - 1].mean()
        stdDev = series[0:len(series) - 1].std()
        expAverage = pandas.stats.moments.ewma(series, com=com)

        return abs(series.iat[-1]) > 3 * stdDev


class LeastSquares(object):
    """
    A timeseries is anomalous if the average of the last three datapoints
    on a projected least squares model is greater than three sigma.
    """

    def on_get(self, req, resp):

        timeseries, tidx, vidx = utils.backend_retreival(req)
        self._run(req, resp, timeseries, tidx, vidx)

    def on_post(self, req, resp):

        timeseries, tidx, vidx = utils._non_backend_call(req)
        self._run(req, resp, timeseries, tidx, vidx)

    def _run(self, req, resp, timeseries, tidx, vidx):

        result = self._work(timeseries, tidx=tidx, vidx=vidx)

        resp.body = json.dumps(result)
        resp.status = falcon.HTTP_200

    def _work(self, timeseries, tidx=0, vidx=1):

        x = np.array([t[tidx] for t in timeseries])
        y = np.array([t[vidx] for t in timeseries])
        A = np.vstack([x, np.ones(len(x))]).T
        results = np.linalg.lstsq(A, y)
        residual = results[1]
        m, c = np.linalg.lstsq(A, y)[0]
        errors = []
        for i, value in enumerate(y):
            projected = m * x[i] + c
            error = value - projected
            errors.append(error)

        if len(errors) < 3:
            return False

        std_dev = scipy.std(errors)
        t = (errors[-1] + errors[-2] + errors[-3]) / 3

        return abs(t) > std_dev * 3 and round(std_dev) != 0 and round(t) != 0


class HistogramBins(object):
    """
    A timeseries is anomalous if the average of the last three datapoints falls
    into a histogram bin with less than 20 datapoints you'll need to tweak
    that number depending on your data.

    Returns: the size of the bin which contains the tail_avg. Smaller bin size
    means more anomalous.
    """

    def on_get(self, req, resp):

        timeseries, tidx, vidx = utils.backend_retreival(req)
        self._run(req, resp, timeseries, tidx, vidx)

    def on_post(self, req, resp):

        timeseries, tidx, vidx = utils._non_backend_call(req)
        self._run(req, resp, timeseries, tidx, vidx)

    def _run(self, req, resp, timeseries, tidx, vidx):

        bins = req.get_param_as_int("bins", required=False)

        if bins:
            result = self._work(timeseries, tidx=tidx, vidx=vidx, bins=bins)
        else:
            result = self._work(timeseries, tidx=tidx, vidx=vidx)

        resp.body = json.dumps(result)
        resp.status = falcon.HTTP_200

    def _work(self, timeseries, tidx=0, vidx=1, bins=15):

        series = scipy.array([x[vidx] for x in timeseries])
        t = utils._tail_avg(timeseries, tidx, vidx)
        h = np.histogram(series, bins=bins)
        bins = h[1]
        for index, bin_size in enumerate(h[0]):
            if bin_size <= 20:
                # Is it in the first bin?
                if index == 0:
                    if t <= bins[0]:
                        return True
                # Is it in the current bin?
                elif t >= bins[index] and t < bins[index + 1]:
                        return True

        return False
