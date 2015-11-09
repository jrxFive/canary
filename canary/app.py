import falcon
import skyline
import outlier
import backend

api = falcon.API()

# Skyline Resources
skyline_MedianAbsoluteDeviation = skyline.MedianAbsoluteDeviation()
skyline_Grubbs = skyline.Grubbs()

# Outlier Resources
outlier_Tukey = outlier.Tukey()

# Backend Resources
backend_AvailableBackends = backend.AvailableBackends()

# Skyline routes
api.add_route('/v1/algos/skyline/medianabsolutedeviation',skyline_MedianAbsoluteDeviation)
api.add_route('/v1/algos/skyline/grubbs',skyline_Grubbs)

# Outlier routes
api.add_route('/v1/algos/outliers/tukey',outlier_Tukey)

# Backend routes
api.add_route('/v1/backends',backend_AvailableBackends)