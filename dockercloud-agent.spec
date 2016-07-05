# TODO
# - handle external deps
#   + go get -d -v
#   - github.com/ActiveState/tail (download)
#   - github.com/hpcloud/tail (download)
#   - github.com/flynn-archive/go-shlex (download)
#   - github.com/getsentry/raven-go (download)
Summary:	Agent to manage docker in nodes controlled by Docker Cloud
Name:		dockercloud-agent
Version:	1.1.0
Release:	0.1
License:	Apache v2.0
Group:		Applications/System
Source0:	https://github.com/docker/dockercloud-agent/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	9a3382c0a8f4b55bb8e94a250b6fd1dd
URL:		https://github.com/docker/dockercloud-agent/
BuildRequires:	golang >= 1.4
BuildRequires:	golang < 1.6
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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
install -d $RPM_BUILD_ROOT%{_sbindir}
install -p %{name} $RPM_BUILD_ROOT%{_sbindir}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md NOTICE
%attr(755,root,root) %{_sbindir}/dockercloud-agent