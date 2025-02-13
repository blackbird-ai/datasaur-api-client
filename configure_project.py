import sys, os
import json
import yaml
import string
import random
import time
from fire import Fire

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
from logger import logger

import shutil

def random_string():
    characters = string.ascii_letters + string.digits
    random_chars = random.choices(characters, k=4)
    random_string = "".join(random_chars)
    return random_string


def get_project_name(project_title):
    project_title = project_title.replace(" ", "-")
    project_name = f"{project_title}-{random_string()}"
    logger.info(f"PROJECT NAME: {project_name}")
    return project_name


def read_config_file(path):
    with open(path, "r") as stream:
        res = yaml.safe_load(stream)
    stream.close()
    return res


def main(
    document_path: str,
    project_template: str,
    positive_label: str = None,
    negative_label: str = None,
    project_title: str = "none",
    config_output: str = "./datasaur-api-client/create-project-async/project_configuration.json",
):
    # Read the JSON file
    with open(project_template, "r") as file:
        data = json.load(file)
    # # Read CONFIG
    logger.info(f"PROJECT TITLE: {project_title}")
    logger.info(f"POSITIVE LABEL: {positive_label}")
    logger.info(f"NEGATIVE LABEL: {negative_label}")

    logger.info(f"Document path: {document_path}")

    # Update the values for the specified keys
    data["variables"]["input"]["name"] = get_project_name(project_title)
    data["variables"]["input"]["documents"][0]["fileName"] = document_path.split(
        "/"
    )[-1]
    data["variables"]["input"]["documents"][0]["name"] = document_path.split("/")[-1]
    for i in data["variables"]["input"]["documentAssignments"]:
        i["documents"][0]["fileName"] = document_path.split("/")[-1]
    data["variables"]["input"]["documents"][0]["file"]["path"] = document_path
    # Write the updated data back to the JSON file
    with open(config_output,"w",) as file:
        json.dump(data, file, indent=4)
    json_string = json.dumps(data, indent=4)  # Convert dictionary to JSON string with indentation
    logger.info(f"HERE IS THE REFORMATTED DATASAUR PROJECT CONFIG {project_template}\n\n {json_string}")
    logger.info(f"END")



if __name__ == "__main__":
    logger.info("Datasaur Project Configuration")
    start_time = time.time()
    Fire(main)
    #### Calculate elapsed time
    elapsed_time = time.time() - start_time
    logger.info(f"Project configuration elapsed time: {elapsed_time:.2f} seconds")
