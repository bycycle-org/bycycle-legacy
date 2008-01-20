#!/bin/bash
# Portland specific for now

as_user_do="sudo -u ${USER}"

# The file containing the Virtual Host configuration
vhost_conf_file=/usr/local/apache2/conf/extra/httpd-vhosts.conf

# Top level of SVN data checkout
data_home=${HOME}/byCycleData/portlandor/pirate
last_svn_version_path="${data_home}/last_svn_version"

# Compare current SVN version to last SVN version.
# If they're the same, there's nothing to do, so exit.
curr_svn_version=`svnversion ${data_home}`
last_svn_version=`cat ${last_svn_version_path}`

if [ "${curr_svn_version}" = "${last_svn_version}" ]; then
    echo "Data is up to date at version ${curr_svn_version}."
    exit 0
fi

# Otherwise, we update the last SVN version and upgrade the data.
echo -n ${curr_svn_version} > ${last_svn_version_path}
echo "Upgrading data..."

sed -i 's/#ErrorDocument 503/ErrorDocument 503/g' ${vhost_conf_file}
apachectl restart

tp_service_path="${HOME}/byCycle/apps/web/tripplanner/trunk/service/tripplanner"

# Stop app server
$as_user_do $svc -d ${tp_service_path}

# Run integration script
# Note: We should pass the integrate params to *this* script and pass them
#       through to the integrate script.
$as_user_do ${HOME}/byCycle/core/trunk/byCycle/scripts/integrate.py \
    --region portlandor \
    --source pirate \
    --layer str06oct \
    --no-prompt

# Start app server
$as_user_do $svc -u ${tp_service_path}

sed -i 's/ErrorDocument 503/#ErrorDocument 503/g' ${vhost_conf_file}
apachectl restart

