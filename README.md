# koji-rekor-plugin
Koji Hub plugin that initiates automatic uploads to Rekor Transparency Server whenever an RPM is signed in Koji to enable additional supply chain security

# Purpose
A Rekor transparency log records immutable records of artifacts and their signature materials that can be queried for inclusion proof and signature metadata. Accordingly, it Rekor functions as a timestamped source of truth that individuals can check their software against, creating a a chain of custody for the artifact. It also dcreases the friction in the package verification process for end-users by simplifying key management needs. This plugin enables parties to incorporate Rekor into their Koji build and signing process; in doing so, they and others can use Rekor to independently verify RPM packages to increase trust, traceability, and non-repudiation in their workflows.

# Usage
Koji doesn’t natively sign RPMs. The proper mechanism to sign a package is to:
  1. Make a copy of the unsigned RPM
  2. Sign the RPM in the CLI (`rpmsign -addsign <rpm_package>`) or through a signing system/server
  3. Import the signed RPM headers to Koji Hb (CLI Command: `koji import-sig`)

The Rekor plugin triggers upon the Koji Hub callback 'PostRPMSign', which occurs whenever an RPM signature header is imported to Koji. The plugin takes the signed RPM, its signature, and the relevant public key that is stored on the signing machine and uploads the materials to a Rekor transparency log. If the upload is successful, the log returns an inclusion proof that is saved in the directory `rekor-logs` under Koji's top directory.

# Installation
Install `rekor_log.py` in the Koji Hub plugins folder `usr/lib/koji-hub-plugins/`
Save `rekor_log.conf` in `/etc/koji-hub/plugins/`

Update the Hub configuration file `/etc/koji-hub/hub.conf` to enable the plugin  
```
# A space-separated list of plugins to enable
Plugins = rekor_log
```
Restart Apache: `systemctl restart httpd.service`

# Configuration Options
There are four options in the configuration file.
**public_key_path**: The plugin needs to be able to access the public key corresponding with the RPM's signature. Export the public key using `gpg --export --armor <Name>` the file in a path that is accessible to the Hub; the default is `/usr/share/koji-hub/public-keys`.
**rekor_server_url**: 
**enforce_rekor_upload**:
**record_log_info**:
