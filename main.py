import argilla as rg

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

    delete_workspaces(client, workspaces_to_delete)
    delete_users(client, users_to_delete)

if __name__ == "__main__":
    main()
