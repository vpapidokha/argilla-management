from google.cloud import storage

def download_file_from_gcs(project, bucket_name, file_name, local_path):
    client = storage.Client(project)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.download_to_filename(local_path)
    print(f"File {file_name} downloaded to {local_path}.")

def main():
    download_file_from_gcs("pulumi-experimental-vpa", "argilla-test", "records.json", "./imdb_records.json")

if __name__ == "__main__":
    main()
