
# Detailed Usage

The following detailed instructions are for manually signing RPMs and uploading them to Koji and Rekor using the plugin. The plugin should also work for automated signing systems, such as Sigul. It triggers upon the callback `PostRPMSign`, which is called whenever a signature header is uploaded to Koji. The corresponding CLI command is `koji import-sig`, which ultimately calls the function `add-rpm-sig` [where the callback occurs](https://github.com/koji-project/koji/blob/d0507c4d2d2269daa984db642e3bd957dff18948/hub/kojihub.py#L7628).
These steps are also outlined in a [demo](https://drive.google.com/file/d/1W-g0dlfXp1kM-MPVtu7sJHn1WPAKbu8g/view?usp=sharing).


Download the unsigned RPM from Koji:
```
koji download-build <build_name>
```
Configure the `.rpmmacros` file with appropriate GPG information; sign the RPM file using `rpmsign` and the `--rpmv3` flag to sign the entire package, not just the signature header (this ensures Rekor will accept and verify the signature):
```
rpmsign --addsign --rpmv3 <rpm_name>
```
Verify the RPM signature, if desired:
```
rpm -Kv <rpm_name>
```
Make sure the plugin is installed, enabled, and configured. Import the signature header into Koji:
```
koji import-sig
```
View the logs and/or Rekor receipt:
```
cat /etc/httpd/logs/ssl_error_log
cat /mnt/koji/rekor_logs/<name>/<version>/<release>/<architecture>/<json_receipt>
```
Search and retrieve the RPM's entry in Rekor:
```
rekor-cli search --artifact <rpm>
>>> Entry's UUID
rekor-cli get --uuid <uuid>
```
