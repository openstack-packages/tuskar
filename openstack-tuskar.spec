Name:	      openstack-tuskar
Version:	  0.3.1
Release:	  2%{?dist}
Summary:	  A service for managing OpenStack deployments

Group:		  Applications/System
License:	  ASL 2.0
URL:		    https://github.com/openstack/tuskar
Source0:	  https://pypi.python.org/packages/source/t/tuskar/tuskar-%{version}.tar.gz
Source1:    openstack-tuskar-api.service

Patch0:     0001-Don-t-show-image-parameters-to-user.patch

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
%setup -q -n tuskar-%{version}
%patch0 -p1
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
chmod +x %{buildroot}%{python2_sitelib}/tuskar/openstack/common/rootwrap/cmd.py
chmod +x %{buildroot}%{python2_sitelib}/tuskar/cmd/api.py
chmod +x %{buildroot}%{python2_sitelib}/tuskar/cmd/manager.py
chmod +x %{buildroot}%{python2_sitelib}/tuskar/cmd/dbsync.py
chmod +x %{buildroot}%{python2_sitelib}/tuskar/openstack/common/rpc/zmq_receiver.py

%files
%doc LICENSE README.rst
%{python2_sitelib}/tuskar
%{python2_sitelib}/*.egg-info
%{_unitdir}/openstack-tuskar-api.service
# binaries for tuskar
%attr(0755, root, root) %{_bindir}/tuskar-api
%attr(0755, root, root) %{_bindir}/tuskar-dbsync
%attr(0755, root, root) %{_bindir}/tuskar-manager
%attr(0755, root, root) %{_sharedstatedir}/tuskar
%dir %attr(0755, root, root) %{_sysconfdir}/tuskar
%config(noreplace) %attr(0644, root, root) %{_sysconfdir}/tuskar/tuskar.conf

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
* Tue Apr 29 2014 Jordan OMara <jomara@redhat.com> 0.3.1-2
- incorrect previous patch, switched out (jomara@redhat.com)

* Tue Apr 16 2014 Jordan OMara <jomara@redhat.com> 0.3.1-1
- new source 0.3.1 (jomara@redhat.com)
- added jsonutils patch from oslo-incubator (jomara@redhat.com)

* Wed Apr 16 2014 Jordan OMara <jomara@redhat.com> 0.3.0-1
- new source 0.3.0 (jomara@redhat.com)

* Mon Apr 07 2014 Jordan OMara <jomara@redhat.com> 0.2.3-2
- adding python-six & python-posix_ipc dep (jomara@redhat.com)

* Fri Apr 04 2014 Jordan OMara <jomara@redhat.com> 0.2.3-1
- new source 0.2.3 (jomara@redhat.com)

* Thu Apr 03 2014 Jordan OMara <jomara@redhat.com> 0.2.2-3
- remove wsgi, add post/preun/postun runs for systemctl
- misc cleanup from additional reviews (jomara@redhat.com)

* Tue Apr 01 2014 Jordan OMara <jomara@redhat.com> 0.2.2-2
- __python --> __python2 (jomara@redhat.com)

* Wed Mar 26 2014 Jordan OMara <jomara@redhat.com> 0.2.2-1
- Fixing more rpmlint issues (jomara@redhat.com)

* Fri Mar 14 2014 Jordan OMara <jomara@redhat.com> 0.1.0-3
- Fixing various rpm issues (jomara@redhat.com)

* Wed Feb 26 2014 Jordan OMara <jomara@redhat.com> 0.7-2
- Adding PBR to buildrequires (jomara@redhat.com)

* Wed Feb 19 2014 Jordan OMara <jomara@redhat.com> 0.7-1
- Adding PBR to buildrequires (jomara@redhat.com)

* Wed Feb 19 2014 Jordan OMara <jomara@redhat.com> 0.6-1
- Removing %%configure block (jomara@redhat.com)

* Wed Feb 19 2014 Jordan OMara <jomara@redhat.com> 0.5-1
- Fixing tuskar prep location (jomara@redhat.com)

* Wed Feb 19 2014 Jordan OMara <jomara@redhat.com> 0.4-1
- Minor fixes for httpd.conf location (jomara@redhat.com)

* Wed Feb 19 2014 Jordan OMara <jomara@redhat.com> 0.3-1
- Automatic commit of package [openstack-tuskar] release [0.2-1].
  (jomara@redhat.com)
- Initialized to use tito. (jomara@redhat.com)
- Initial commit of spec file, wsgi file and apache module for wsgi
  (jomara@redhat.com)
- Merge "Getting correct count and attributes from database"
  (jenkins@review.openstack.org)
- Merge "Fix tuskar docs building" (jenkins@review.openstack.org)
- Fix tuskar docs building (jason.dobies@redhat.com)
- Getting correct count and attributes from database (lsmola@redhat.com)

* Wed Feb 19 2014 Jordan OMara <jomara@redhat.com> 0.2-1
- new package built with tito

* Wed Feb 19 2014 Jordan OMara <jomara@redhat.com> - 0.0.1-1
- initial package
