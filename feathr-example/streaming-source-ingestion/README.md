# Streaming ingestion setup

## Prerequisite
1. Eventhub setup
    1. Create an eventhub `Namespace` and `Event hubs` (topics) - follow this [link](https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-create).
    1. Setup the SAS policy for your topic - follow this [link](https://github.com/feathr-ai/feathr/blob/main/docs/how-to-guides/feathr-configuration-and-env.md#KAFKA_SASL_JAAS_CONFIG). The connection string would be the `KAFKA_SASL_JASS_CONFIG` value.
1. `eventhub_producer.py` setup
    1. Open the `eventhub_producser.py` and change the values of the variables:
        1. `KAFKA_BROKER` - this would be the `HOST_NAME` of your eventhub namespace - see the overview section of your eventhub namespace.
        1. `KAFKA_TOPIC` - this is the topic you've created when you setup the eventhub.
        1. `KAFKA_SASL_JASS_CONFIG` - this is value of the connection string generated when creating a `SAS Policy` for your topic. 
            - Note: Excude (remove) `EntityPath` section of the connection string.
        1. `GENERATION_SIZE_MIN` - this would be the start driver's id. This is optional, for testing you could change this value.
        1. `GENERATION_SIZE_MAX` = this would be the maximum dirver's id. This is optional, for testing you change this value.
1. `streaming_ingestion.ipynb` setup
    1. Open the `streaming_ingestion.ipynb` and supply the neccessary values of the environment variables.
        - os.environ['REDIS_PASSWORD']
        - os.environ['AZURE_CLIENT_ID']
        - os.environ['AZURE_TENANT_ID']
        - os.environ['AZURE_CLIENT_SECRET']
        - os.environ['KAFKA_SASL_JAAS_CONFIG'] - this is value of the connection string generated when creating a `SAS Policy` for your topic.
            - Note: Excude (remove) `EntityPath` section of the connection string.
    1. Change the values of the variables:
        1. KAFKA_BROKER - this would be the `HOST_NAME` of your eventhub namespace - see the overview section of your eventhub namespace.
        1. KAFKA_TOPIC - this is the topic you've created when you setup the eventhub.

## Running the notebook and producer
1. Run the `eventhub_producer.py` on the terminal - this would indefinitely keep on producing messages to your eventhub topic. Take note of the range of the `GENERATION_SIZE_MIN` and `GENERATION_SIZE_MAX`, this would be the ids produced for testing.
1. Run the `streaming_ingestion.ipynb` notebook. On the last cell (`Fetch streaming features values`), changed the ids (second argument) that is is within the `GENERATION_SIZE_MIN` and `GENERATION_SIZE_MAX` range to retrieve the materialized values.