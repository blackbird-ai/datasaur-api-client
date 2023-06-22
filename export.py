import json
import os
import time
import requests
import fire

from io import BytesIO
import zipfile
import pandas as pd
import io

from urllib.parse import urlparse
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

POOLING_INVERVAL = 0.5  # 0.5s


def save_file_to_tsv(content=None, output_file=None):
    data_stream = BytesIO(content)
    # Open the ZIP archive
    with zipfile.ZipFile(data_stream, "r") as archive:
        file_list = archive.namelist()
        for file in file_list:
            print(file)
            if (file.endswith("tsv")) and ("DOCUMENT" in file):
                # Read the contents of a specific file
                specific_file_content = archive.read(file)
                data = specific_file_content.decode("utf-8")
                data_stream = io.StringIO(data)
                df = pd.read_csv(data_stream, sep="\t")
                df.to_csv(output_file, sep="\t", index=False)
                print("Success downloading the file. Output file:" + output_file)


def export_project(
    base_url: str,
    client_id: str,
    client_secret: str,
    project_id: str,
    export_format: str,
    export_file_name: str = None,
    output_dir: str = None,
    output_file: str = None,
    export_file: str = "./datasaur-api-client/export.json",
    delivery_file: str = "./datasaur-api-client/get_export_delivery_status.json",

):
    url = base_url + "/graphql"
    access_token = get_access_token(base_url, client_id, client_secret)
    operations = get_operations(file_name=export_file)

    operations["variables"]["input"]["fileName"] = export_file_name
    operations["variables"]["input"]["projectIds"] = [project_id]
    operations["variables"]["input"]["format"] = export_format

    response = post_request(url, access_token, operations)
    if "json" in response.headers["content-type"]:
        json_response = json.loads(response.text.encode("utf8"))
        print(json.dumps(json_response, indent=1))

        if len(json_response["data"]["result"]["fileUrl"]) > 0:
            export_id = json_response["data"]["result"]["exportId"]
            poll_export_delivery_status(url, access_token, export_id, delivery_path=delivery_file)

            file_url = json_response["data"]["result"]["fileUrl"]
            file_response = requests.request("GET", file_url)
            if output_file:
                directory = os.path.dirname(output_file)
                os.makedirs(directory, exist_ok=True)
                save_file_to_tsv(content=file_response.content, output_file=output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                file_response_url = urlparse(file_url)
                file_name = os.path.basename(file_response_url.path)
                output_file = output_dir + "/" + file_name
                open(output_file, "wb").write(file_response.content)
                print("Success downloading the file. Output file:" + output_file)
    else:
        print(response)


def poll_export_delivery_status(url, access_token, export_id, delivery_path="./datasaur-api-client/get_export_delivery_status.json"):
    operations = get_operations(file_name=delivery_path)
    operations["variables"]["exportId"] = export_id
    while True:
        time.sleep(POOLING_INVERVAL)
        response = post_request(url, access_token, operations)
        if "json" in response.headers["content-type"]:
            json_response = json.loads(response.text.encode("utf8"))
            delivery_status = json_response["data"]["exportDeliveryStatus"][
                "deliveryStatus"
            ]
            if delivery_status == "QUEUED":
                print("Waiting for exported file to be ready...")
            elif delivery_status == "DELIVERED":
                print("Exported file is ready")
                break
            elif delivery_status == "FAILED":
                print("Failed to export file")
                break
        else:
            print(response)
            break


def get_access_token(base_url, client_id, client_secret):
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(
        token_url=base_url + "/api/oauth/token",
        client_id=client_id,
        client_secret=client_secret,
    )
    return token["access_token"]


def get_operations(file_name=None):
    with open(file_name, "r") as file:
        return json.loads(file.read())


def post_request(url, access_token, operations):
    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json",
    }
    return requests.request("POST", url, headers=headers, data=json.dumps(operations))


if __name__ == "__main__":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    fire.Fire(export_project)
