import codecs
import requests
import json


"""
Fetches our "backend" data from a public API for Vacasa Clean objects.

See https://housekeeping.vacasa.io/#tag/cleans for more details.
"""
def fetch_cleans(ids=[], pageSize=None):
    url = 'https://housekeeping.vacasa.io/cleans'
    headers = { 'Content-Type': 'application/vnd.api+json' }
    payload = {
        'filter[id][in]': ",".join(ids)
    }

    if pageSize:
        payload['page[size]'] = pageSize

    return requests.get(url, headers=headers, params=payload)

"""
Format a response object (for Lambda).
"""
def response(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err if err else res,
        'headers': {
            'Content-Type': 'application/json',
        },
    }

"""
Entry point for the app.

Example `event` object shape (from API Gateway):
https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html
"""
def handler(event, context):

    operation = event['httpMethod'] if 'httpMethod' in event else None

    # instructions page
    if operation == 'GET':
        page = ""
        with codecs.open("instructions.html", "r") as f:
            page = f.read()

        res = {
            'statusCode': '200',
            'body': page,
            'headers': {
                'Content-Type': 'text/html',
            }
        }
        return res

    # cleaning time results
    elif operation == 'POST':

        # validate input
        query = event['queryStringParameters'] if 'queryStringParameters' in event else None
        payload = json.loads(event['body']) if 'body' in event else None
        ids = payload['ids'] if payload and 'ids' in payload else None

        if not ids:
            return response("Must provide at least one ID.")

        # undocumented: used for testing
        pageSize = query['pageSize'] if query and 'pageSize' in query else None

        min_time = 0
        max_time = 0
        total_time = 0

        # page 1
        first_page = fetch_cleans(ids, pageSize)

        # iterate while there are more pages
        next_page = first_page
        while next_page:

            # validate and parse fetch response
            if next_page.status_code != 200:
                return response("Error with the cleans API. Try again later.")
            else:
                next_page = next_page.json()

            # make sure it has what we expect
            data = next_page['data'] if 'data' in next_page else None
            links = next_page['links'] if 'links' in next_page else None
            meta = next_page['meta'] if 'meta' in next_page else None
            if not data or not links or not meta:
                return response("Unable to parse clean data. Sorry.")

            # accumulate time, check min & max
            for clean in data:
                attributes = clean['attributes'] if 'attributes' in clean else None
                time = attributes['predicted_clean_time'] if attributes and 'predicted_clean_time' in attributes else None
                if time:
                    total_time += time
                if time and time > max_time:
                    max_time = time
                if time and (time < min_time or min_time == 0):
                    min_time = time

            # pull next page
            if 'next' in links and links['next']:
                next_page = requests.get(links['next'])
            else:
                next_page = None

            # The cleans API exhibits odd behavior when an invalid ID is present
            # in the filter: _no_ filtering takes place and _all_ results are
            # returned. I realize that with how this is code is written that
            # one could set pageSize really high to get around this check, but
            # I'm more concerned about my AWS bill as processing all 2M+ results
            # iteratively is going to run that lambda for *quite* awhile.
            if meta['page'] > 5:
                msg = "I fear you've provided an invalid clean ID. Please \
                double check and try again. If you have in fact provided more \
                than 125 _valid_ ids, forgive me for cutting you short. Please \
                consider our premium subscription plan which will allow you to \
                query all 2,632,141 results."
                return response(msg)

        times = {
            "total": total_time,
            "max": max_time,
            "min": min_time
        }
        return response(None, json.dumps(times))

    # this is not the method you're looking for
    else:
        return response('Unsupported method "{}"'.format(operation))
