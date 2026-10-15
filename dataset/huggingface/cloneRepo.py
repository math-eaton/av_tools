from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="segments/sidewalk-semantic", 
    repo_type="dataset", 
    local_dir="my_local_dataset_folder"
)
