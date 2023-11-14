import fire
from os import environ
from src.project import Project
from src.job import Job
import time
## 

def create_project(
    base_url,
    client_id,
    client_secret,
    team_id,
    documents_path="./datasaur-api-client/create-project-async/documents",
    operations_path="./datasaur-api-client/create-project-async/project_configuration.json",
):
    # try:
    Project.create(
        base_url,
        client_id,
        client_secret,
        team_id=str(team_id),
        operations_path=operations_path,
        documents_path=documents_path,
    )
    # except Exception as e:
    #     raise SystemExit(e)


def get_job_status(base_url, client_id, client_secret, job_id):
    try:
        Job.get_status(
            base_url,
            client_id,
            client_secret,
            job_id=str(job_id),
            operations_path="src/get_job_status.json",
        )
    except Exception as e:
        raise SystemExit(e)


if __name__ == "__main__":
    environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    print("Creating Datasaur project...")
    start_time = time.time()
    fire.Fire()
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    print(f"Total elapsed time: {elapsed_time:.2f} seconds")
