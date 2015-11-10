import falcon
import skyline
import outlier
import backend

api = falcon.API()

# Skyline Resources
skyline_MedianAbsoluteDeviation = skyline.MedianAbsoluteDeviation()
skyline_Grubbs = skyline.Grubbs()
skyline_FirstHourAverage = skyline.FirstHourAverage()
skyline_HistogramBins = skyline.HistogramBins()
skyline_LeastSquares = skyline.LeastSquares()
skyline_MeanSubtractionCumulation = skyline.MeanSubtractionCumulation()
skyline_StddevFromAverage = skyline.StddevFromAverage()
skyline_StddevFromMovingAverage = skyline.StddevFromMovingAverage()

# Outlier Resources
outlier_Tukey = outlier.Tukey()

# Backend Resources
backend_AvailableBackends = backend.AvailableBackends()

# Skyline routes
api.add_route('/v1/algos/skyline/medianabsolutedeviation',
              skyline_MedianAbsoluteDeviation)

api.add_route('/v1/algos/skyline/grubbs',
              skyline_Grubbs)

api.add_route('/v1/algos/skyline/firsthouraverage',
              skyline_FirstHourAverage)

api.add_route('/v1/algos/skyline/histogrambins',
              skyline_HistogramBins)

api.add_route('/v1/algos/skyline/leastsquares',
              skyline_LeastSquares)

api.add_route('/v1/algos/skyline/meansubtractioncumulation',
              skyline_MeanSubtractionCumulation)

api.add_route('/v1/algos/skyline/stddevfromaverage',
              skyline_StddevFromAverage)

api.add_route('/v1/algos/skyline/stddevfrommovingaverage',
              skyline_StddevFromMovingAverage)


# Outlier routes
api.add_route('/v1/algos/outliers/tukey', outlier_Tukey)

# Backend routes
api.add_route('/v1/backends', backend_AvailableBackends)
