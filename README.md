# koji-rekor-plugin
Koji Hub plugin that initiates automatic uploads to Rekor Transparency Server whenever an RPM is signed in Koji to enable additional supply chain security

# Purpose
A Rekor transparency log records immutable records of artifacts and their signature materials that can be queried for inclusion proof and signature metadata. Accordingly, it Rekor functions as a timestamped source of truth that individuals can check their software against, creating a a chain of custody for the artifact. It also dcreases the friction in the package verification process for end-users by simplifying key management needs. This plugin enables parties to incorporate Rekor into their Koji build and signing process; in doing so, they and others can use Rekor to independently verify RPM packages to increase trust, traceability, and non-repudiation in their workflows.

# Usage
Koji doesn’t natively sign RPMs. The proper mechanism to sign a package is to:
  1. Make a copy of the unsigned RPM
  2. Sign the RPM in the CLI (`rpmsign -addsign <rpm_package>`) or through a signing system/server
  3. Import the signed RPM headers to Koji Hub (CLI Command: `koji import-sig`)

The Rekor plugin triggers upon the Koji callback 'PostRPMSign', which occurs whenever an RPM signature header is imported to Koji. The plugin takes the signed RPM, it's signature, and the relevant public key that is stored on the signing machine and uploads the materials to a Rekor transparency log. If the upload is successful, the log returns an inclusion proof that is saved in the directory `rekor-logs` under Koji's top directory.

# Installation

# Configuration Options

**public_key_path**:
**rekor_server_url**:
**enforce_rekor_upload**:
**record_log_info**:
