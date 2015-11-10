import falcon
import backend
import json
import msgpack


def _tail_avg(timeseries, tidx=0, vidx=1):
    """
    This is a utility function used to calculate the average of the last three
    datapoints in the series as a measure, instead of just the last datapoint.
    It reduces noise, but it also reduces sensitivity and increases the delay
    to detection.
    """
    try:
        t = (timeseries[-1][vidx] + timeseries[-2]
             [vidx] + timeseries[-3][vidx]) / 3
        return t
    except IndexError:
        return timeseries[-1][vidx]


def backend_retreival(req):
    try:
        q_backend = req.get_param("backend", required=True)
        return backend._pull_backend(q_backend, req.params)
    except falcon.HTTPBadRequest:
        falcon.HTTPBadRequest(description="backend query parameter not given")


def _non_backend_call(req):
    try:
        if req.content_type == "application/json":
            timeseries = json.load(req.stream)
        elif req.content_type == "application/msgpack":
            timeseries = msgpack.load(req.stream)
        else:
            timeseries = json.load(req.stream)

        if not isinstance(timeseries, list):
            raise ValueError

        tidx = req.get_param_as_int("tidx", required=False)
        vidx = req.get_param_as_int("vidx", required=False)

        return timeseries, tidx, vidx

    except ValueError:
        raise falcon.HTTPUnsupportedMediaType(description="invalid steam or "
                                              "data is not a list")
