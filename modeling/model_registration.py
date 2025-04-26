import mlflow
from mlflow.exceptions import RestException
from mlflow.tracking import MlflowClient

# 0. Configuration
EXPERIMENT_NAME      = "Taxi_Demand_Per_Cluster"
REGISTERED_MODEL_FMT = "TaxiDemandCluster_{cluster_id}"
ARTIFACT_PATH_FMT    = "model_cluster_{cluster_id}"
TARGET_STAGE         = "Production"   # or "Production"

# 1. Initialize client and find experiment
client = MlflowClient()
exp = client.get_experiment_by_name(EXPERIMENT_NAME)
if exp is None:
    raise ValueError(f"Experiment '{EXPERIMENT_NAME}' not found.")
exp_id = exp.experiment_id

# 2. List all runs, newest first
runs = client.search_runs(
    experiment_ids=[exp_id],
    filter_string="",
    order_by=["attributes.start_time DESC"]
)

# 3. Pick the most recent run for each cluster
best_run_by_cluster = {}
for run in runs:
    run_name = run.data.tags.get("mlflow.runName", "")
    if not run_name.startswith("cluster_"):
        continue
    cluster_id = run_name.split("_", 1)[1]
    if cluster_id not in best_run_by_cluster:
        best_run_by_cluster[cluster_id] = run

# 4. Register each cluster model version and transition stage
for cluster_id, run in best_run_by_cluster.items():
    run_id = run.info.run_id
    artifact_path = ARTIFACT_PATH_FMT.format(cluster_id=cluster_id)
    model_uri = f"runs:/{run_id}/{artifact_path}"
    registered_model_name = REGISTERED_MODEL_FMT.format(cluster_id=cluster_id)

    # Create the Registered Model if it doesn’t exist
    try:
        client.create_registered_model(registered_model_name)
    except RestException:
        # already exists
        pass

    # Create a new version
    mv = client.create_model_version(
        name=registered_model_name,
        source=model_uri,
        run_id=run_id
    )

    # Transition to the desired stage, archiving any existing versions
    client.transition_model_version_stage(
        name=registered_model_name,
        version=mv.version,
        stage=TARGET_STAGE,
        archive_existing_versions=True
    )

    print(
        f"Cluster {cluster_id}: registered version {mv.version} "
        f"of '{registered_model_name}' and moved to stage '{TARGET_STAGE}'"
    )
