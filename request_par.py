from flask import *
from flask_cors import CORS
import oci
import datetime

app = Flask(__name__)
CORS(app)

@app.route('/image', methods=['GET'])
def index():
    # get objec and bucket name from url
    object = request.args.get('object')
    bucket = request.args.get('bucket')
    # replace REST endpoint depending on region you are using
    object_REST_endpoint = 'https://objectstorage.us-ashburn-1.oraclecloud.com'

    # Option 1. config file  ( I am locally testing this out)
    configfile = "Your_Path/config"
    config = oci.config.from_file(configfile)
    object_storage = oci.object_storage.ObjectStorageClient(config)
    namespace = object_storage.get_namespace().data

    # Option 2. get signer from instance principals in VM in OCI
    #signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    # initialize the ObjectStorageClient with an empty config and only a signer
    #object_storage = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
    #namespace = object_storage.get_namespace().data

    # Review parameters to access object storage
    #print(namespace, bucket, object)

    # Generate RFC 3339 timestamp for time_expires
    current_time = datetime.datetime.utcnow()
    # PAR URL will be only available for 5 mins
    mins_added = datetime.timedelta(minutes=5)
    time_expires = current_time + mins_added

    create_preauthenticated_request_details = oci.object_storage.models.CreatePreauthenticatedRequestDetails()
    create_preauthenticated_request_details.name = object + '-' + str(current_time)
    create_preauthenticated_request_details.object_name = object
    create_preauthenticated_request_details.access_type = 'ObjectRead'
    create_preauthenticated_request_details.time_expires = time_expires
    access_uri = object_storage.create_preauthenticated_request(namespace, bucket,
                                                                create_preauthenticated_request_details)
    par_url = object_REST_endpoint + access_uri.data.access_uri
    #print(access_uri.data, par_url)
    return par_url

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)
