#!/usr/bin/env python3
import argparse
# import json
import csv
import requests
import sys

import json


def convert_to_json(input_str):
    print(input_str)
    try:
        # it converts without any quote sting eg. {title: Rocks!, body: rocks., userId: 1}
        if input_str:
            formatted_str = (
                input_str.replace("'", "")
                .replace("{", '{"')
                .replace("}", '"}')
                .replace(": ", '": "')
                .replace(", ", '", "')
            )
            try:
                json_obj = json.loads(formatted_str)
                return json_obj
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid input string for JSON conversion: {e}")
        else:
            return input_str
    except Exception as e:
        print("Error",e)
        raise ValueError(f"Invalid input string for JSON conversion: {e}")


class RestfulClient:
    BASE_URL = "https://jsonplaceholder.typicode.com"  # Example base URL

    def __init__(self, method, endpoint, data=None, output=None):
        self.method = method.lower()
        self.endpoint = endpoint
        self.data = convert_to_json(data)
        self.output = output

        print(self.data,"self.data")

    def execute(self):
        url = f"{self.BASE_URL}{self.endpoint}"
        response = self.send_request(url)
        self.handle_response(response)

    def send_request(self, url):
        try:
            if self.method == "get":
                response = requests.get(url)
            elif self.method == "post":

                response = requests.post(url, json=self.data)
            else:
                raise ValueError(f"unsupported method: {self.method}")
            return response
        except requests.RequestException as e:
            print(f"request failed: {e}", file=sys.stderr)
            sys.exit(1)

    def handle_response(self, response):
        print(f"HTTP status Code: {response.status_code}")
        if not response.ok:
            print(f"Error: {response.text}", file=sys.stderr)
            sys.exit(1)

        content = response.json()
        if self.output:
            if self.output.endswith(".json"):
                self.write_json(content)
            elif self.output.endswith(".csv"):
                self.write_csv(content)
            else:
                print("unsupported output file format. Use .json or .csv", file=sys.stderr)
                sys.exit(1)
        else:
            print(json.dumps(content, indent=2))

    def write_json(self, content):
        # Write json file
        with open(self.output, "w") as f:
            json.dump(content, f, indent=2)
        print(f"Response written to {self.output}")

    def write_csv(self, content):
        # Write CSV file
        if not isinstance(content, list):
            content = [content]
        if len(content) == 0:
            print("Empty response. Nothing to write to CSV.", file=sys.stderr)
            return

        with open(self.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=content[0].keys())
            writer.writeheader()
            writer.writerows(content)
        print(f"Response written to {self.output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple RESTful API Client")
    parser.add_argument("method", choices=["get", "post"], help="Request method")
    parser.add_argument("endpoint", help="Request endpoint URI fragment")
    parser.add_argument("-d", "--data", help="Data to send with request", required=False)
    parser.add_argument("-o", "--output", help="Output to .json or .csv file (default: dump to stdout)", required=False)

    args = parser.parse_args()

    # print(args.data,"----------")

    client = RestfulClient(args.method, args.endpoint, data=args.data, output=args.output)
    client.execute()


