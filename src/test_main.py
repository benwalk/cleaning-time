import json
import unittest
import main

fixture = [
    ("e3e70682-c209-4cac-629f-6fbed82c07cd", 2.91691406956171),
    ("16a92bf5-0e5d-4372-a801-1d4e2895be65", 2.51412196030228),
    ("9c4fc12a-dd2f-415a-a112-d7ff5aee0de0", 2.63486499590766)
]

def event(method, body):
    return {
      "httpMethod": method,
      "body": str(body)
    }

def response(status, body):
    return {
        'statusCode': str(status),
        'body': str(body),
        'headers': {
            'Content-Type': 'application/json'
        }
    }

class TestMain(unittest.TestCase):

    def test_get(self):
        event = {
          "httpMethod": "GET",
        }
        result = main.handler(event, 'c')
        self.assertEqual(result['statusCode'], '200')

    def test_invalid_method(self):
        event = {
            "httpMethod": "PUT"
        }
        result = main.handler(event, 'c')
        self.assertEqual(result['statusCode'], '400')

    def test_post_with_zero_ids(self):
        event = {
          "httpMethod": "POST",
          "body": str(json.dumps({
              "ids": []
          }))
        }
        expected = response(400, 'Must provide at least one ID.')
        result = main.handler(event, 'c')
        self.assertEqual(result, expected)

    def test_post_with_one_id(self):
        event = {
          "httpMethod": "POST",
          "body": str(json.dumps({
              "ids": list(map(lambda x: x[0], fixture[:1]))
          }))
        }
        expected = response(200, json.dumps({
            'total': sum(list(map(lambda x: x[1], fixture[:1]))),
            'max': fixture[0][1],
            'min': fixture[0][1]
        }))

        result = main.handler(event, 'c')
        self.assertEqual(result, expected)


    def test_post_with_two_ids(self):
        event = {
          "httpMethod": "POST",
          "body": str(json.dumps({
              "ids": list(map(lambda x: x[0], fixture[:2]))
          }))
        }
        expected = response(200, json.dumps({
            'total': sum(list(map(lambda x: x[1], fixture[:2]))),
            'max': fixture[0][1],
            'min': fixture[1][1]
        }))
        result = main.handler(event, 'c')
        self.assertEqual(result, expected)

    def test_post_with_three_ids(self):
        event = {
          "httpMethod": "POST",
          "body": str(json.dumps({
              "ids": list(map(lambda x: x[0], fixture[:3]))
          }))
        }
        expected = response(200, json.dumps({
            'total': sum(list(map(lambda x: x[1], fixture[:3]))),
            'max': fixture[0][1],
            'min': fixture[1][1]
        }))
        result = main.handler(event, 'c')
        self.assertEqual(result, expected)

    def test_post_with_multiple_pages(self):
        event = {
            "httpMethod": "POST",
            "body": str(json.dumps({
              "ids": list(map(lambda x: x[0], fixture[:3]))
            })),
            "queryStringParameters": {
                "pageSize": 1
            }
        }
        expected = response(200, json.dumps({
            'total': sum(list(map(lambda x: x[1], fixture[:3]))),
            'max': fixture[0][1],
            'min': fixture[1][1]
        }))
        result = main.handler(event, 'c')
        self.assertEqual(result, expected)

    def test_post_with_invalid_ids(self):
        ids = list(map(lambda x: x[0], fixture[1:3]))
        ids.append('fake')
        event = {
            "httpMethod": "POST",
            "body": str(json.dumps({
              "ids": ids
            }))
        }
        result = main.handler(event, 'c')
        self.assertEqual(result['statusCode'], '400')

if __name__ == '__main__':
    unittest.main()
