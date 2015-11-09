import falcon
import skyline
import backend

api = falcon.API()

# Skyline Resources
skyline_MedianAbsoluteDeviation = skyline.MedianAbsoluteDeviation()
skyline_Grubbs = skyline.Grubbs()

# Backend Resources
backend_AvailableBackends = backend.AvailableBackends()

# Skyline routes
api.add_route('/v1/algos/skyline/medianabsolutedeviation',skyline_MedianAbsoluteDeviation)
api.add_route('/v1/algos/skyline/grubbs',skyline_Grubbs)

# Backend routes
api.add_route('/v1/backends',backend_AvailableBackends)