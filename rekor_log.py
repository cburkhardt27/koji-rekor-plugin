import logging
import base64
import requests
import json
import os.path
import os
import sys
sys.path.insert(0, "/usr/share/koji-hub")
from koji.plugin import callback
from koji.context import context
import koji

CONFIG_FILE = '/etc/koji-hub/plugins/rekor_transparency_plugin.conf'
config = None

# Log output to Apache's ssl_error_log
logger = logging.getLogger('koji.plugin.rekor')
logger.setLevel(logging.INFO)

def get_signed_rpm(buildinfo, rpminfo, sigkeyinfo, enforce_upload):
    """At the time of the callback, the RPM's signature has been added to Koji,
    but the RPM with its signature header hasn't yet been added to the database.
    Function returns that signed RPM so it can be uploaded to Rekor."""
    buildpath = koji.pathinfo.build(buildinfo)
    rpmpath = koji.pathinfo.rpm(rpminfo)
    unsigned_rpm_path = "%s/%s" % (buildpath,rpmpath)
    logging.getLogger('koji.plugin.rekor').info('Unsigned RPM path is %s' % unsigned_rpm_path)
    if not os.path.isfile(unsigned_rpm_path):
        if enforce_upload == "True":
            raise koji.CallbackError("RPM path does not contain expected file: %s" % unsigned_rpm_path)
        else:
            logging.getLogger('koji.pluign.rekor').error("RPM path does not contain expected file: %s" % unsigned_rpm_path)
            return
    sighdrpath = "%s/%s" % (buildpath, koji.pathinfo.sighdr(rpminfo, sigkeyinfo))
    logging.getLogger('koji.plugin.rekor').info('Sigkey is %s and the sighdr path is %s' % (sigkeyinfo, sighdrpath))
    with open(sighdrpath, 'rb') as f:
        sighdr = f.read()
    return koji.splice_rpm_sighdr(sighdr, unsigned_rpm_path)


def post_rekor(signed_rpm, public_key, rekor_url, enforce_upload):
    """Post RPM signing information to Rekor server"""
    with open(signed_rpm, "rb") as f:
        rpm_bytes = f.read()
        rpm_b64 = base64.b64encode(rpm_bytes).decode('utf-8')
    if not os.path.isfile(public_key):
        if enforce_upload == "True":
            koji.ConfigurationError("Public key path does not contain expected file")
        else:
            logging.getLogger('koji.plugin.rekor').error("Public key path does not contain expected file")
            return
    with open(public_key, "rb") as f:
        public_key_bytes = f.read()
        rpm_pub_key_b64 = base64.b64encode(public_key_bytes).decode('utf-8')
    payload_json = {
        "apiVersion": "0.0.1",
        "kind": "rpm",
        "spec": {
            "package": {
                "content": rpm_b64
            },
            "publicKey": {
                "content": rpm_pub_key_b64
            }
        }
    }
    payload = json.dumps(payload_json)
    rekor_api_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    try:
        r = requests.post(rekor_url, data=payload, headers=rekor_api_headers)
    except requests.ConnectionError:
        if enforce_upload == "True":
            koji.CallbackError("Server connection error")
        else:
            logging.getLogger('koji.plugin.rekor').error("Server connection error")
    except requests.Timeout:
        if enforce_upload == "True":
            koji.CallbackError("Server timed out")
        else:
            logging.getLogger('koji.plugin.rekor').error("Server timed out")
    except requests.exceptions:
        if enforce_upload == "True":
            koji.CallbackError("Unknown server error")
        else:
            logging.getLogger('koji.plugin.rekor').error("Unknown server error")
    else:
        return r

def record_log_info(rpminfo, logjson):
    """Log the successful Rekor call in the directory /rekor_logs under the top directory"""
    nvra = "%(name)s-%(version)s-%(release)s.%(arch)s" % rpminfo
    rpmpath = "%(name)s/%(version)s/%(release)s/%(arch)s" % rpminfo
    logpath = os.path.join(koji.pathinfo.topdir, "rekor_logs", rpmpath)
    if not os.path.exists(logpath):
        os.makedirs(logpath)
    infofile = "%s/%s.json" % (logpath, nvra)
    logging.getLogger('koji.plugin.rekor').info("Writing Rekor info to: %s" % infofile)
    with open(infofile, "x") as f:
        f.write(logjson)

@callback('postRPMSign')
def upload_to_rekor_log(cbtype, *args, **kws):
    global config
    if not config:
        config = koji.read_config_files([(CONFIG_FILE, True)])
    public_key = config.get('config', 'public_key_path')
    rekor_url = config.get('config', 'rekor_server_url') + "/api/v1/log/entries"
    enforce_upload = config.get('config', 'enforce_rekor_upload')
    record_info = config.get('config', 'record_log_info')
    # Check that the RPM is both built and signed    
    if kws['build']['state'] != 1:
        if enforce_upload == "True":
            raise koji.CallbackError("Build state incomplete")
        else:
            logging.getLogger('koji.plugin.rekor').error("Build state incomplete")
            return
    if not kws['sigkey']:
        if enforce_upload == "True":
            raise koji.CallbackError("RPM is unsigned")
        else:
            logging.getLogger('koji.plugin.rekor').error('RPM is unsigned')
            return

    signed_rpm = get_signed_rpm(kws['build'], kws['rpm'], kws['sigkey'], enforce_upload)
    rekor_response = post_rekor(signed_rpm, public_key, rekor_url, enforce_upload)

    if rekor_response == None:
        return
    if rekor_response.status_code == 201:
        logging.getLogger('koji.plugin.rekor').info('Upload successful. Writing Rekor log info to file. %s' % rekor_response.text)
        if record_info == "True":
            record_log_info(kws['rpm'], rekor_response.text)
    elif rekor_response.status_code == 409:
        logging.getLogger('koji.plugin.rekor').info('Upload aborted. Rekor entry already exists. %s' % rekor_response.text)
        return
    else:
        if enforce_upload == "True":
            koji.CallbackError('Upload failed. %s' % rekor_response.text)
        else:
            logging.getLogger('koji.plugin.rekor').info('Upload failed. %s' % rekor_response.text)
            return