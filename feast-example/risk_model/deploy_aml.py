import os
from re import S
from azureml.core import Workspace
from azureml.core.environment import Environment
from azureml.core.webservice import AksWebservice
from azureml.core import Workspace, Model
from azureml.core.model import InferenceConfig


def main():
    print("Connecting to Azure ML Workspace.....")
    ws = Workspace.get(
        subscription_id=os.getenv('WS_SUBSCRIPTION_ID'),
        resource_group=os.getenv('WS_RESOURCE_GROUP'),
        name=os.getenv('WS_NAME'))
    kv = ws.get_default_keyvault()

    # Create Deployment Environment
    # Note the file_path is assuming that deploy.py is called from root of project
    print("Setting up Deployment Environment configuration.....")
    env = Environment.from_conda_specification(
        name="deploy_env",
        file_path="./config/conda_dependencies.yaml")

    env.docker.base_image = None
    env.docker.base_dockerfile = "./Dockerfile"

    env.python.user_managed_dependencies = False
    env.inferencing_stack_version = "latest"

    deployment_config = AksWebservice.deploy_configuration(
        compute_target_name=os.getenv("AKS_INFERENCE_NAME"),
        autoscale_enabled=True,
        autoscale_min_replicas=1,
        autoscale_max_replicas=3,
        cpu_cores=.5,
        memory_gb=2,
        enable_app_insights=True,
        tags={"data": "home_credit_risk"})

    # For Local Testing
    # deployment_config = LocalWebservice.deploy_configuration(
    #     port=12345
    # )

    inference_config = InferenceConfig(
        entry_script="score.py",
        source_directory="./risk_model",
        environment=env)

    model = Model(workspace=ws, name=os.getenv("MODEL_NAME"), version=int(os.getenv("MODEL_VERSION")))
    model_path = Model.get_model_path(model_name=os.getenv("MODEL_NAME"), version=int(os.getenv("MODEL_VERSION")), _workspace=ws)
    # deploy the service
    service_name = os.getenv("SERVICE_NAME")

    inference_config.environment.environment_variables = {
        'SNOWFLAKE_USER': kv.get_secret("SNOWFLAKE-USER"),
        'SNOWFLAKE_PASS': kv.get_secret("SNOWFLAKE-PASS"),
        'REGISTRY_PATH': kv.get_secret("FEAST-REGISTRY-PATH"),
        'snowflake_compute_name': kv.get_secret("SNOWFLAKE-COMPUTE"),
        'snowflake_database_name': kv.get_secret("SNOWFLAKE-DB"),
        'snowflake_role_name': kv.get_secret("SNOWFLAKE-ROLE"),
        "REDIS_CONN_STRING": kv.get_secret("REDIS-CONN-STRING"),
        'SNOWFLAKE_ACC': kv.get_secret("SNOWFLAKE-ACC"),
        "AZURE_CLIENT_ID": kv.get_secret("AZURE-CLIENT-ID"),
        "AZURE_TENANT_ID": kv.get_secret("AZURE-TENANT-ID"),
        "AZURE_CLIENT_SECRET": kv.get_secret("AZURE-CLIENT-SECRET"),
        "MODEL_PATH": model_path
    }

    print("Deploy ML Model......")
    service = Model.deploy(
        workspace=ws,
        name=service_name,
        models=[model],
        inference_config=inference_config,
        deployment_config=deployment_config,
        overwrite=True
    )

    service.wait_for_deployment(show_output=True)

if __name__ == "__main__":
    main()
