

# def build_apinode_client(params):
#     """
#     Builds an APINodeClient, handling both local and remote deployer configurations.
#     """
#     client_design = dataikuapi.DSSClient(params["host"], params["api"])
#     api_deployer = client_design.get_apideployer()
#     infra_settings = api_deployer.get_infra(params["api_dev_infra_id"]).get_settings().get_raw()

#     # Check if this is a local deployer-based infra (apiNodes exist)
#     if 'apiNodes' in infra_settings and len(infra_settings['apiNodes']) > 0:
#         api_url = infra_settings['apiNodes'][0]['url']
#         print(f"Using local API node URL: {api_url}")
#     else:
#         # Remote deployer: construct the endpoint URL
#         api_url = f"{params['host']}/public/api/v1/{params['api_service_id']}/{params['api_endpoint_id']}"
#         print(f"Using remote API endpoint URL: {api_url}")

#     return dataikuapi.APINodeClient(api_url, params["api"])

# def build_apinode_client(params):
#     """
#     Builds APINodeClient, compatible with both local and remote deployer configurations.
#     """
#     client_design = dataikuapi.DSSClient(params["host"], params["api"])
#     api_deployer = client_design.get_apideployer()
#     infra_settings = api_deployer.get_infra(params["api_dev_infra_id"]).get_settings().get_raw()

#     # If using a local deployer (inside DSS instance)
#     if 'apiNodes' in infra_settings and len(infra_settings['apiNodes']) > 0:
#         api_url = infra_settings['apiNodes'][0]['url']
#         print(f"Using local API node URL: {api_url}")
#         return dataikuapi.APINodeClient(api_url, params["api"])

#     else:
#         # Remote deployer: build full service-level URL
#         api_url = f"{params['host']}/public/api/v1/{params['api_service_id']}"
#         print(f"Using remote API service endpoint: {api_url}")

#         # Create API Node client with Bearer token auth
#         return dataikuapi.APINodeClient(
#             api_url,
#             params["api"],  # SDK API key = token
#             params["api_service_id"],  # service ID
#             {"Authorization": f"Bearer {params['api']}"}  # extra headers
#         )


import dataikuapi
import requests
import inspect

import dataikuapi

def build_apinode_client(params):
    """
    Build an APINodeClient for both local (DSS) and remote (AKS-based) API deployer setups.
    Automatically resolves a dynamic URL when deployed on AKS.
    """
    client_design = dataikuapi.DSSClient(params["host"], params["api"])
    api_deployer = client_design.get_apideployer()

    infra = api_deployer.get_infra(params["api_dev_infra_id"])
    infra_settings = infra.get_settings().get_raw()

    # Case 1: Local DSS Infra (URL from 'apiNodes')
    if "apiNodes" in infra_settings and len(infra_settings["apiNodes"]) > 0:
        api_url = infra_settings["apiNodes"][0]["url"]
        print(f"Using local API node URL: {api_url}")
        return dataikuapi.APINodeClient(api_url, params["api"])

    # Case 2: Remote Deployer (AKS)
    deployment_id = f"{params['api_service_id']}-on-{params['api_dev_infra_id']}"
    print(f"No local apiNodes found, looking up remote deployment '{deployment_id}'...")

    deployment = next(
        (d for d in api_deployer.list_deployments() if d.id() == deployment_id),
        None
    )
    if not deployment:
        raise ValueError(f"Deployment with ID '{deployment_id}' not found!")

    print(f"Found deployment '{deployment_id}', fetching live status...")

    # Try different ways to extract the URL from the deployment status
    live_status = deployment.get_status()

    try:
        status_dict = live_status.to_dict()
    except AttributeError:
        try:
            status_dict = vars(live_status)
        except Exception:
            raise ValueError("Unable to parse deployment status into a usable format.")

    api_url = status_dict.get("url") or status_dict.get("healthCheckUrl")
    if not api_url:
        raise ValueError(f"No usable 'url' found in deployment status: {status_dict}")

    if api_url.endswith("/predict"):
        api_url = api_url.rsplit("/", 1)[0]

    print(f"Using deployed API URL: {api_url}")

    return dataikuapi.APINodeClient(
        api_url,
        params["api"],
        extra_headers={"Authorization": f"Bearer {params['api']}"}
    )



def test_standard_call(params):
    client = build_apinode_client(params)
    print("Test is using API node URL {}".format(client.base_uri))
    record_to_predict = {
        "State": "KS",
        "Account_Length": 128,
        "Area_Code": 415,
        "Phone": "382-4657",
        "Intl_Plan": False,
        "VMail_Plan": True,
        "VMail_Message": 25,
        "Day_Mins": 265.1,
        "Day_Calls": 110,
        "Day_Charge": 45.07,
        "Eve_Mins": 197.4,
        "Eve_Calls": 99,
        "Eve_Charge": 16.78,
        "Night_Mins": 244.7,
        "Night_Calls": 91,
        "Night_Charge": 11.01,
        "Intl_Mins": 10,
        "total_Mins": 717.2,
        "Intl_Calls": 3,
        "Intl_Charge": 2.7,
        "Total_Charge": 75.56,
        "CustServ_Calls": 1,
        "cluster_labels": "cluster_4"
    }
    prediction = client.predict_record(params["api_endpoint_id"], record_to_predict)
    assert prediction['result']['prediction'] == '1', "Prediction should be 1 but is {}".format(prediction['result']['prediction'])


def test_missing_param(params):
    client = build_apinode_client(params)
    print("Test is using API node URL {}".format(client.base_uri))
    record_to_predict = {
        "Account_Length": 128,
        "Area_Code": 415,
        "Phone": "382-4657",
        "Intl_Plan": False,
        "VMail_Message": 25,
        "Day_Mins": 265.1,
        "Day_Calls": 110,
        "Day_Charge": 45.07,
        "Eve_Mins": 197.4,
        "Eve_Calls": 99,
        "Eve_Charge": 16.78,
        "Night_Mins": 244.7,
        "Night_Calls": 91,
        "Night_Charge": 11.01,
        "Intl_Mins": 10,
        "total_Mins": 717.2,
        "Intl_Calls": 3,
        "Intl_Charge": 2.7,
        "Total_Charge": 75.56,
        "CustServ_Calls": 1,
        "cluster_labels": "cluster_4"
    }
    prediction = client.predict_record(params["api_endpoint_id"], record_to_predict)
    assert prediction['result']['ignored'], "Record should be ignored but got {}".format(prediction['result'])
    assert prediction['result']['ignoreReason'] == "IGNORED_BY_MODEL", "Reason should be IGNORED_BY_MODEL but got {}".format(prediction['result'])
