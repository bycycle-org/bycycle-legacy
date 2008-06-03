#!/bin/bash
# Portland specific for now
# Run as root (sudo). Pass effective user as arg $1.

# Env
if [ "$1" = "" ]; then
    echo "ERROR: Effective user must be provided as first argument."
    exit 127
fi
user="$1"
home="/home/${user}"
as_user_do="sudo -u ${user}"

# The file containing the Virtual Host configuration
vhost_conf_file=/usr/local/apache2/conf/extra/httpd-vhosts.conf

# Top level of SVN data checkout
data_home=${home}/byCycleData/portlandor/pirate
last_svn_version_path="${data_home}/last_svn_version"

# Compare current SVN version to last SVN version.
# If they're the same, there's nothing to do, so exit.
curr_svn_version=`svnversion ${data_home}`
last_svn_version=`cat ${last_svn_version_path}`

# Path to daemontools setup
tp_service_path="${home}/byCycle/apps/web/tripplanner/trunk/service/tripplanner"

if [ "${curr_svn_version}" = "${last_svn_version}" ]; then
    echo "Data is up to date at version ${curr_svn_version}."
    exit 0
fi

# Otherwise, we upgrade the data.
echo "Upgrading data..."
if [ 6 -eq 2 ]; then
echo "Setting 503 response and restarting Apache..."
sed -i 's/#ErrorDocument 503/ErrorDocument 503/g' ${vhost_conf_file} || exit 1
apachectl restart || exit 2

# Stop app server
echo "Stopping application server..."
$as_user_do svc -d ${tp_service_path} || exit 3

# Run integration script
# Note: We should pass the integrate params to *this* script and pass them
#       through to the integrate script.
echo "Running data integration script. Please wait; this will take a while..."
$as_user_do ${home}/byCycle/core/trunk/byCycle/scripts/integrate.py \
    --region portlandor \
    --source pirate \
    --layer str06oct \
    --no-prompt \
    || exit 4

# Start app server
echo "Restarting app server..."
$as_user_do svc -u ${tp_service_path} || exit 5
fi
echo "Removing 503 response and restarting Apache..."
sed -i 's/ErrorDocument 503/#ErrorDocument 503/g' ${vhost_conf_file} || exit 6
apachectl restart || exit 7

# Update SVN version of last update (i.e., this update).
echo "Setting SVN version to ${curr_svn_version}..."
echo -n ${curr_svn_version} > ${last_svn_version_path} || exit 8

echo "All done."
exit 0

