import falcon
import skyline

api = falcon.API()

skyline_MedianAbsoluteDeviation = skyline.MedianAbsoluteDeviation()
skyline_Grubbs = skyline.Grubbs()

api.add_route('/v1/algos/skyline/medianabsolutedeviation',skyline_MedianAbsoluteDeviation)
api.add_route('/v1/algos/skyline/grubbs',skyline_Grubbs)
