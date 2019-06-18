import json
import inspect
import urllib.parse

from longitude.core.data_sources.base import DataSource


class DisabledCache:
    data_source = None

    def __init__(self, ds):
        if ds and not isinstance(ds, DataSource):
            raise TypeError('DisabledCache can only be applied to DataSource subclasses.')
        self.data_source = ds

    def __enter__(self):
        self.data_source.disable_cache()

    def __exit__(self, *args):
        self.data_source.enable_cache()


def method_not_supported(o):
    # We assume that this function is called from an object (o) directly from the not supported method
    # If so, the index 1 in the stack is the call previous to method_not_supported, so it holds the info about the
    # previous call (the not supported method!). Then we take the name, which is stored in the third index.
    method = inspect.stack()[1][3]

    o.logger.error("%s does not support %s" % (o.__class__.__name__, method))


def add_url_params(url, params):
    """ Add GET params to provided URL being aware of existing.

    :param url: string of target URL
    :param params: dict containing requested params to be added
    :return: string with updated URL

    >> url = 'http://stackoverflow.com/test?answers=true'
    >> new_params = {'answers': False, 'data': ['some','values']}
    >> add_url_params(url, new_params)
    'http://stackoverflow.com/test?data=some&data=values&answers=false'
    """
    # Unquoting URL first so we don't loose existing args
    url = urllib.parse.unquote(url)
    # Extracting url info
    parsed_url = urllib.parse.urlparse(url)
    # Extracting URL arguments from parsed URL
    get_args = parsed_url.query
    # Converting URL arguments to dict
    parsed_get_args = dict(urllib.parse.parse_qsl(get_args))
    # Merging URL arguments dict with new params
    parsed_get_args.update(params)

    # Bool and Dict values should be converted to json-friendly values
    # you may throw this part away if you don't like it :)
    parsed_get_args.update(
        {k: json.dumps(v) for k, v in parsed_get_args.items()
         if isinstance(v, (bool, dict))}
    )

    # Converting URL argument to proper query string
    encoded_get_args = urllib.parse.urlencode(parsed_get_args, doseq=True)
    # Creating new parsed result object based on provided with new
    # URL arguments. Same thing happens inside of urlparse.
    new_url = urllib.parse.ParseResult(
        parsed_url.scheme, parsed_url.netloc, parsed_url.path,
        parsed_url.params, encoded_get_args, parsed_url.fragment
    ).geturl()

    return new_url
