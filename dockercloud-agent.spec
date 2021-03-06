# TODO
# - handle external deps
#   + go get -d -v
#   - github.com/ActiveState/tail (download)
#   - github.com/hpcloud/tail (download)
#   - github.com/flynn-archive/go-shlex (download)
#   - github.com/getsentry/raven-go (download)
# - downloads and installs third party closed binary (static 32bit ELF)
# 2016/07/05 21:55:37 Downloading NAT tunnel binary ...
# 2016/07/05 21:55:37 Downloading ngrok definition from https://cloud.docker.com/api/tutum/v1/agent/ngrok/latest/1.1.0.json
# 2016/07/05 21:55:37 Downloading ngrok from https://files.cloud.docker.com/packages/ngrok/ngrok-1.7.tgz
# 2016/07/05 21:55:46 Saving ngrok to %{_libexecdir}/dockercloud/
# 2016/07/05 21:55:46 Uncompressing: %{_libexecdir}/dockercloud/._ngrok
# 2016/07/05 21:55:46 Uncompressing: %{_libexecdir}/dockercloud/ngrok
# - runs with specific docker version (1.9.1-cs2), bundled, but we install docker package for 'docker' user
Summary:	Agent to manage docker in nodes controlled by Docker Cloud
Name:		dockercloud-agent
Version:	1.1.0
Release:	0.4
License:	Apache v2.0
Group:		Applications/System
Source0:	https://github.com/docker/dockercloud-agent/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	9a3382c0a8f4b55bb8e94a250b6fd1dd
Source1:	https://files.cloud.docker.com/packages/docker/docker-1.9.1-cs2.tgz
URL:		https://github.com/docker/dockercloud-agent/
BuildRequires:	golang < 1.6
BuildRequires:	golang >= 1.4
Requires:	device-mapper-libs >= 1.02.90-1
Requires:	docker
Requires:	gnupg2
Requires:	iptables
Requires:	libcgroup
Requires:	sqlite3
Requires:	tar
Requires:	xz
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_libexecdir	%{_prefix}/lib

%define		_enable_debug_packages 0
%define		gobuild(o:) go build -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n')" -a -v -x %{?**};

%description
This is the agent Docker Cloud uses to set up nodes. It's a daemon
that will register the host with the DockerCloud API using a user
token (Token), and will manage the installation, configuration and
ongoing upgrade of the Docker daemon.

For information on how to install it in your host, please check the
Bring Your Own Node documentation.

https://docs.docker.com/docker-cloud/infrastructure/byoh/

%prep
%setup -q

GOPATH=$(pwd)/vendor
install -d $GOPATH/src/github.com/docker
ln -s ../../../.. $GOPATH/src/github.com/docker/dockercloud-agent

%build
export GOPATH=$(pwd)/vendor

go get -d -v
%gobuild -o %{name}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_bindir}
install -p %{name} $RPM_BUILD_ROOT%{_bindir}

# Include init scripts
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{systemdunitdir}}
cp -p contrib/init/sysvinit-redhat/dockercloud-agent $RPM_BUILD_ROOT/etc/rc.d/init.d
cp -p contrib/init/systemd/dockercloud-agent.socket $RPM_BUILD_ROOT%{systemdunitdir}
cp -p contrib/init/systemd/dockercloud-agent.service $RPM_BUILD_ROOT%{systemdunitdir}

# Include logrotate
install -d $RPM_BUILD_ROOT/etc/logrotate.d
cp -p contrib/logrotate/dockercloud-agent $RPM_BUILD_ROOT/etc/logrotate.d

install -d $RPM_BUILD_ROOT%{_sysconfdir}/dockercloud/agent
cp -p dockercloud-agent.conf $RPM_BUILD_ROOT%{_sysconfdir}/dockercloud/agent

install -d $RPM_BUILD_ROOT%{_libexecdir}/dockercloud
cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_libexecdir}/dockercloud/docker.tar.gz

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md NOTICE
%config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/dockercloud-agent
%dir %{_sysconfdir}/dockercloud
%dir %{_sysconfdir}/dockercloud/agent
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/dockercloud/agent/dockercloud-agent.conf
%attr(754,root,root) /etc/rc.d/init.d/dockercloud-agent
%attr(755,root,root) %{_bindir}/dockercloud-agent
%{systemdunitdir}/dockercloud-agent.socket
%{systemdunitdir}/dockercloud-agent.service
%dir %{_libexecdir}/dockercloud
%{_libexecdir}/dockercloud/docker.tar.gz
