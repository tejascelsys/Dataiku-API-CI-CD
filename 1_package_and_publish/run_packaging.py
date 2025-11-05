import dataikuapi
import sys

host = sys.argv[1]
apiKey = sys.argv[2]
project = sys.argv[3]
api_service_id = sys.argv[4]
api_package_id = sys.argv[5]
infra_dev_id = sys.argv[6]
infra_prod_id = sys.argv[7]

client = dataikuapi.DSSClient(host, apiKey)
test_project = client.get_project(project)

####################
# Retrieve the API Service in the project
api_service = test_project.get_api_service(api_service_id)
print("Found API Service to package {}".format(api_service))

####################
# # Create and retrieve an API package

# api_service.create_package(api_package_id)
# print("New package created with name '{}'".format(api_package_id))
# # Uncomment the next line to download and use the zip file (to upload it to an Artefact repository for example)
# # api_service.download_package_to_file(api_package_id, api_package_id + ".zip")
# version_as_stream = api_service.download_package_stream(api_package_id)
# print("Stream handle retrieved on the package")

# ####################
# # Find the service as known by API Deployer

# api_deployer = client.get_apideployer()
# deployer_service = ""
# for serv in api_deployer.list_services():
#     if serv.id() == api_service_id:
#         print("Found existing Deployer API service {}".format(api_service_id))
#         deployer_service = serv
# if deployer_service == "":
#     print("Creating missing service {}".format(api_service_id))
#     deployer_service = api_deployer.create_service(api_service_id)

# ####################
# # Import the new version

# # new_version = deployer_service.import_version(api_package_id, version_as_stream)
# new_version = deployer_service.import_version(version_as_stream)
# print("New version published as '{}'".format(api_package_id))

# ####################
# # Create and retrieve an API package

# api_service.create_package(api_package_id)
# print(f"New package created with name '{api_package_id}'")

# # Download the zip file locally so it can be uploaded to the remote deployer
# package_filename = f"{api_package_id}.zip"
# api_service.download_package_to_file(api_package_id, package_filename)
# print(f"Package downloaded locally as '{package_filename}'")

# ####################
# # Find the service as known by API Deployer

# api_deployer = client.get_apideployer()
# deployer_service = None
# for serv in api_deployer.list_services():
#     if serv.id() == api_service_id:
#         print(f"Found existing Deployer API service {api_service_id}")
#         deployer_service = serv
# if deployer_service is None:
#     print(f"Creating missing service {api_service_id}")
#     deployer_service = api_deployer.create_service(api_service_id)

# ####################
# # Import the new version to the remote deployer using the zip file

# # with open(package_filename, 'rb') as f:
# #     version_as_stream = f.read()

# # new_version = deployer_service.import_version(version_as_stream)
# # Publish ZIP file to remote deployer
# new_version = deployer_service.import_version_from_file(api_package_id, package_filename)
# print(f"Package '{api_package_id}' successfully published to remote deployer")

# print(f"New version published as '{api_package_id}'")



####################
# # Create and retrieve an API package

# api_service.create_package(api_package_id)
# print(f"New package created with name '{api_package_id}'")

# # Download the zip file locally so it can be uploaded to the remote deployer
# package_filename = f"{api_package_id}.zip"
# api_service.download_package_to_file(api_package_id, package_filename)
# print(f"Package downloaded locally as '{package_filename}'")

# ####################
# # Find the service as known by the API Deployer

# api_deployer = client.get_apideployer()
# deployer_service = None
# for serv in api_deployer.list_services():
#     if serv.id() == api_service_id:
#         print(f"Found existing Deployer API service '{api_service_id}'")
#         deployer_service = serv

# if deployer_service is None:
#     print(f"Creating missing service '{api_service_id}'")
#     deployer_service = api_deployer.create_service(api_service_id)

# ####################
# # Import the new version into the remote deployer using the ZIP file

# with open(package_filename, 'rb') as f:
#     new_version = deployer_service.import_version(f)

# print(f"Package '{api_package_id}' successfully published to remote deployer")
# print(f"New version imported as '{api_package_id}'")



import dataikuapi
import sys
import requests

host = sys.argv[1]
apiKey = sys.argv[2]
project = sys.argv[3]
api_service_id = sys.argv[4]
api_package_id = sys.argv[5]
infra_dev_id = sys.argv[6]
infra_prod_id = sys.argv[7]
remote_deployer_url = sys.argv[8]
remote_deployer_api_key = sys.argv[9]

client = dataikuapi.DSSClient(host, apiKey)
test_project = client.get_project(project)

####################
# Create and retrieve an API package

api_service = test_project.get_api_service(api_service_id)
api_service.create_package(api_package_id)
print(f"New package created with name '{api_package_id}'")

# Download the zip file locally so it can be uploaded to the remote deployer
package_filename = f"{api_package_id}.zip"
api_service.download_package_to_file(api_package_id, package_filename)
print(f"Package downloaded locally as '{package_filename}'")

####################
# Upload the ZIP to the remote deployer

print(f"Uploading package '{api_package_id}.zip' to remote deployer...")

deploy_url = f"{remote_deployer_url}/public/api/api-deployer/services/{api_service_id}/versions/{api_package_id}"
headers = {
    "Authorization": f"Bearer {remote_deployer_api_key}",
    "Content-Type": "application/zip"
}

with open(package_filename, 'rb') as f:
    response = requests.put(deploy_url, data=f, headers=headers)

if response.status_code in [200, 201]:
    print(f"Package '{api_package_id}' successfully uploaded to remote deployer")
else:
    raise Exception(f"Failed to upload package to remote deployer: {response.status_code} - {response.text}")

print(f"New version '{api_package_id}' is ready in remote deployer")
