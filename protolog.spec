Summary:	The Internet Protocols logger
Summary(pl.UTF-8):	Program zapisujący informacje związane z protokołami Internetowymi
Name:		protolog
Version:	1.0.8
Release:	8
License:	GPL
Group:		Networking
URL:		http://www.grigna.com/diego/linux/
Source0:	ftp://sunsite.unc.edu/pub/Linux/system/network/monitor/%{name}-%{version}.tar.gz
# Source0-md5:	c5a48e61170b3ead0dc55ad86454da1d
Source1:	%{name}.logrotate
Source2:	%{name}.sysconfig
Source3:	%{name}.init
Patch0:		%{name}-1.0.8.make.diff
Patch1:		%{name}-DESTDIR.patch
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires(post):	sed >= 4.0
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
It consists of three daemons that logs incoming IP/TCP, IP/UDP and
IP/ICMP packets.

%description -l pl.UTF-8
Pakiet zawiera trzy daemony logujące informację na temat
przychodzących pakietów IP/TCP, IP/UDP oraz IP/ICMP.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
%{__make} -C src \
	CC="%{__cc}" \
	OPT="%{rpmcflags}"

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig,logrotate.d},%{_sbindir},%{_mandir}/man8} \
	$RPM_BUILD_ROOT/var/log/archive/protolog

%{__make} -C src install \
	DESTDIR=$RPM_BUILD_ROOT \
	bindir=%{_sbindir} \
	mandir=%{_mandir}/man8 \
	logdir=/var/log/protolog

touch $RPM_BUILD_ROOT/var/log/protolog/{icmp.log,icmp.raw,tcp.log,tcp.raw,udp.log,udp.raw}

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/logrotate.d/%{name}
install -p %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
install -p %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/protolog

# handled by initscript
rm -f $RPM_BUILD_ROOT%{_sbindir}/{KillLoggers,LaunchLoggers}

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ "$1" = 1 ]; then
	localip=$(/sbin/ip -f inet addr show | awk '/inet/{print $2}' | awk -F/ '{print $1}' | LC_ALL=C sort -u | xargs)
	sed -i -e "/^#IGNORE_ADDR=.*/s,.*,IGNORE_ADDR='$localip'," /etc/sysconfig/protolog
fi
/sbin/chkconfig --add protolog
%service protolog restart

%preun
if [ "$1" = "0" ]; then
	%service protolog stop
	/sbin/chkconfig --del protolog
fi

%files
%defattr(644,root,root,755)
%doc doc/{BUGS,README,TCP.flags.txt}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/protolog
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/protolog
%attr(755,root,root) %{_sbindir}/*
%attr(754,root,root) /etc/rc.d/init.d/protolog
%attr(750,root,root) %dir /var/log/protolog
%attr(750,root,root) %dir /var/log/archive/protolog
%ghost %attr(640,root,root) /var/log/protolog/*
%{_mandir}/man8/*
