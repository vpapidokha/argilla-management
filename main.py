import argilla as rg
import os
import json

argilla_api_url = "http://localhost:6900"
argilla_api_key = "argilla.apikey"

def new_argilla_connection(api_url, api_key):
    client = rg.Argilla(
        api_url=api_url,
        api_key=api_key,
    )

    print("Argilla client is created successfully!")
    return client

def create_workspaces(client, workspaces_to_create):
    present_workspaces = client.workspaces.list()
    present_workspaces_names = []
    created_workspaces_names = []

    for workspace in present_workspaces:
        present_workspaces_names.append(workspace.name)

    for workspace_name in workspaces_to_create:
        if workspace_name in present_workspaces_names:
            print(f"Workspace {workspace_name} already exists!")
            pass
        else:
            print(f"Creating workspace {workspace_name}...")
            workspace = rg.Workspace(name=workspace_name)
            workspace.create()
            print(f"Workspace {workspace_name} is created!")

    for workspace in client.workspaces:
        created_workspaces_names.append(workspace.name)

    print(f"Workspaces list after creation: {created_workspaces_names}")

def delete_workspaces(client, workspaces_to_delete):
    for workspace in client.workspaces: # We can't delete a workspace with linked datasets
        if workspace.name in workspaces_to_delete:
            workspace.delete()
            print(f"Workspace {workspace.name} is deleted!")

def create_users(client, users_to_create):
    present_users = client.users.list()
    present_users_names = []
    users_names = []

    for user in present_users:
        present_users_names.append(user.username)

    for user_name in users_to_create:
        if user_name in present_users_names:
            print(f"User {user_name} already exists!")
            pass
        else:
            print(f"Creating user {user_name}...")
            user = rg.User(
                username=user_name,
                role=users_to_create[user_name]["role"],
                password=users_to_create[user_name]["password"],
            )

            user.create()
            for workspace in users_to_create[user_name]["workspaces"]:
                target_workspace = client.workspaces(workspace)
                user.add_to_workspace(target_workspace)

            print(f"User {user_name} is created!")

    for user in client.users:
        users_names.append(user.username)

    print(f"Users list after creation: {users_names}")

def delete_users(client, users_to_delete):
    users_names = []
    for user in users_to_delete:
        client.users(user).delete()

    for user in client.users:
        users_names.append(user.username)

    print(f"Users list after creation: {users_names}")

def import_dataset_from_disk(client, dataset_name, workspace_name, directory_path):
    print(f"Importing dataset '{dataset_name}' from '{directory_path}' to workspace '{workspace_name}'...")
    rg.Dataset.from_disk(
            path=directory_path,
            name=dataset_name,
            workspace=workspace_name,
            client=client,
            with_records=True
    )

    print(f"Dataset '{dataset_name}' imported successfully.")

def export_dataset_to_disk(client, dataset_name, workspace_name, directory_path):
    create_directory(directory_path)
    client.datasets(name=dataset_name, workspace=workspace_name).to_disk(directory_path)
    print(f"Dataset '{dataset_name}' exported to '{directory_path}'.")

def delete_dataset(client, dataset_name, workspace_name):
    client.datasets(name=dataset_name, workspace=workspace_name).delete()
    print(f"Dataset '{dataset_name}' is deleted.")

def create_directory(directory_path):
    try:
        os.mkdir(directory_path)
        print(f"Directory '{directory_path}' created successfully.")
    except FileExistsError:
        print(f"Directory '{directory_path}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{directory_path}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

def format_records_from_file(records_file_path):
    with open(records_file_path, "r") as f:
        data = json.load(f)

    records = [
        rg.Record(
            id = item["id"],
            fields = item["fields"],
        )
        for item in data
    ]
    return records

def create_dataset_with_records(client, records, dataset_name, workspace_name):
    settings = rg.Settings(
        guidelines="These are some guidelines.",
        fields=[
            rg.TextField(
                name="text",
            ),
        ],
        questions=[
            rg.LabelQuestion(
                name="label",
                labels=["label_1", "label_2", "label_3"]
            ),
        ],
    )

    dataset = rg.Dataset(
        name=dataset_name,
        workspace=workspace_name,
        client=client,
        settings=settings,
    )

    dataset.create()
    dataset.records.log(records)
    print(f"Records uploaded to dataset " + dataset_name)

def delete_dataset(client, dataset_name, target_workspace_name):
    client.datasets(name=dataset_name, workspace=target_workspace_name).delete()
    print(f"Dataset '{dataset_name}' is deleted.")

def main():
    workspaces_to_create = ["my_workspace", "project1", "project2"]
    workspaces_to_delete = workspaces_to_create
    users_to_create = { # username: {role, workspace}
        "admin": {
            "role": "admin",
            "workspaces": ["my_workspace", "project1", "project2"],
            "password": "12345678",
        },
        "user1": {
            "role": "annotator",
            "workspaces": ["my_workspace"],
            "password": "12345678",
        },
        "user2": {
            "role": "annotator",
            "workspaces": ["project1"],
            "password": "12345678",
        },
    }
    users_to_delete = users_to_create

    client = new_argilla_connection(argilla_api_url, argilla_api_key)

    create_workspaces(client, workspaces_to_create)
    create_users(client, users_to_create)

    dataset_name = "imdb-test"
    target_workspace_name = "my_workspace"
    records_file_path = "./imdb_records.json"
    records = format_records_from_file(records_file_path)
    create_dataset_with_records(client, records, dataset_name, target_workspace_name)
    delete_dataset(client, dataset_name, target_workspace_name)

    # export_dataset_to_disk(client, "imdb", "my_workspace", "./imdb")
    # delete_dataset(client, "imdb", "my_workspace")
    # import_dataset_from_disk(client, "imdb", "my_workspace", "./imdb")

    delete_workspaces(client, workspaces_to_delete)
    delete_users(client, users_to_delete)

if __name__ == "__main__":
    main()
