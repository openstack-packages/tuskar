%global homedir %{_datadir}/tuskar

Name:	      openstack-tuskar
Version:      XXX
Release:      XXX
Summary:	  A service for managing OpenStack deployments

Group:		  Applications/System
License:	  ASL 2.0
URL:		    https://github.com/openstack/tuskar
Source0:	  https://pypi.python.org/packages/source/t/tuskar/tuskar-%{version}.tar.gz
Source1:    openstack-tuskar-api.service

BuildArch:     noarch

BuildRequires: systemd-devel
BuildRequires: python2-devel
BuildRequires: python-setuptools
BuildRequires: python-lockfile
BuildRequires: python-pbr
BuildRequires: python-sphinx >= 1.1.3

Requires: python-sqlalchemy
Requires: python-migrate
Requires: python-anyjson
Requires: python-argparse
Requires: python-eventlet
Requires: python-kombu
Requires: python-lxml
Requires: python-webob
Requires: python-greenlet
Requires: python-iso8601
Requires: python-flask
Requires: python-flask-babel
Requires: python-pecan
Requires: python-wsme
Requires: python-six >= 1.5.2
Requires: python-posix_ipc
Requires: PyYAML
Requires: python-oslo-config
Requires: python-novaclient
Requires: python-keystoneclient
Requires: python-heatclient
Requires: openstack-tripleo-heat-templates

Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units

%description
Tuskar gives administrators the ability to control how and where OpenStack
services are deployed across the data-center. Using Tuskar, administrators
divide hardware into "resource classes" that allow predictable elastic scaling
as cloud demands grow. This resource orchestration allows Tuskar users to
ensure SLAs, improve performance, and maximize utilization across the
data-center.

%prep
%setup -q -n tuskar-%{upstream_version}
rm requirements.txt

%build
export OSLO_PACKAGE_VERSION=%{version}
%{__python2} setup.py build

%install
export OSLO_PACKAGE_VERSION=%{version}
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}

install -d -m 755 %{buildroot}%{_sharedstatedir}/tuskar
install -d -m 755 %{buildroot}%{_sysconfdir}/tuskar

# Move config to /etc
mv etc/tuskar/tuskar.conf.sample %{buildroot}%{_sysconfdir}/tuskar/tuskar.conf

# install systemd scripts
install -d -m 755 %{buildroot}%{_unitdir}
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}

# set scripts to be executable
chmod +x %{buildroot}%{python2_sitelib}/tuskar/common/service.py
chmod +x %{buildroot}%{python2_sitelib}/tuskar/cmd/api.py
chmod +x %{buildroot}%{python2_sitelib}/tuskar/cmd/dbsync.py
chmod +x %{buildroot}%{python2_sitelib}/tuskar/cmd/load_roles.py

%files
%doc LICENSE README.rst
%{python2_sitelib}/tuskar
%{python2_sitelib}/*.egg-info
%{_unitdir}/openstack-tuskar-api.service
# binaries for tuskar
%attr(0755, root, root) %{_bindir}/tuskar-api
%attr(0755, root, root) %{_bindir}/tuskar-dbsync
%attr(0755, root, root) %{_bindir}/tuskar-load-roles
%attr(0755, root, root) %{_bindir}/tuskar-delete-roles
%attr(0755, root, root) %{_bindir}/tuskar-load-role
%attr(0755, root, root) %{_bindir}/tuskar-load-seed
%attr(0755, tuskar, tuskar) %{_sharedstatedir}/tuskar
%dir %attr(0755, root, tuskar) %{_sysconfdir}/tuskar
%config(noreplace) %attr(0644, root, root) %{_sysconfdir}/tuskar/tuskar.conf
# database
%ghost %attr(0755, root, root) %{python2_sitelib}/tuskar/openstack/common/db/tuskar.sqlite

%pre
# Add the "tuskar" user and group
getent group tuskar >/dev/null || groupadd -r tuskar
getent passwd tuskar >/dev/null || \
    useradd -r -g tuskar -d %{_sharedstatedir}/tuskar -s /sbin/nologin \
-c "OpenStack Tuskar Daemons" tuskar
exit 0

%post
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun
if [ $1 -eq 0 ] ; then
    /bin/systemctl --no-reload disable %{name}-api.service > /dev/null 2>&1 || :
    /bin/systemctl stop %{name}-api.service > /dev/null 2>&1 || :
fi

%postun
if [ $1 -ge 1 ] ; then
    /bin/systemctl try-restart %{name}-api.service >/dev/null 2>&1 || :
fi

%changelog
