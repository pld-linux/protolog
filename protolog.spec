Summary:	The Internet Protocols logger
Summary(pl):	Program zapisuj±cy informacje zwi±zane z protoko³ami Internetowymi
Name:		protolog
Version:	1.0.8
Release:	2
Copyright:	GPL
Group:		Networking
Group(pl):	Sieciowe
Vendor:		Diego Javier Grigna <diego@grigna.com>
URL:		http://www.grigna.com/diego/linux/
Source0:	ftp://sunsite.unc.edu/pub/Linux/system/network/monitor/%{name}-%{version}.tar.gz
Source1:	protolog.logrotate
Patch:		%{name}-1.0.8.make.diff
BuildRoot:	/tmp/%{name}-%{version}-root

%description
It consists of three daemons that logs incoming
IP/TCP, IP/UDP and IP/ICMP packets.
						
%description -l pl
Pakiet zawiera trzy deamony loguj±ce informacjê na temat
przychodz±cych pakietów IP/TCP, IP/UDP oraz IP/ICMP.

%prep
%setup -q
%patch -p1

%build
make -C src OPT="$RPM_OPT_FLAGS"

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/{etc/{rc.d/init.d,logrotate.d},usr/{sbin,man/man8}}

make -C src install \
bindir=$RPM_BUILD_ROOT%{_sbindir} \
mandir=$RPM_BUILD_ROOT%{_mandir}/man8 \
logdir=$RPM_BUILD_ROOT/var/log/protolog

touch $RPM_BUILD_ROOT/var/log/protolog/{icmp.log,icmp.raw,tcp.log,tcp.raw,udp.log,udp.raw}

cat  << EOF > $RPM_BUILD_ROOT/etc/rc.d/init.d/protolog
#!/bin/bash
#
# chkconfig: 2345 50 50
# description: IP protocols logger - logs TCP and ICMP.
#
# Source function library.
. /etc/rc.d/init.d/functions

# Source networking configuration.
. /etc/sysconfig/network

PLOGTCP="-q"
PLOGUDP="-q"
PLOGICMP="-q"

if [ -r /etc/protolog.conf ]; then
. /etc/protolog.conf
fi

# Check that networking is up.
[ \${NETWORKING} = "no" ] && exit 0
# See how we were called.
case "\$1" in
  start)
        show Starting protolog TCP daemon:
        daemon plogtcp \$PLOGTCP
	show Starting protolog UDP daemon:
	daemon plogudp \$PLOGUDP
	show Starting protolog ICMP daemon:
	daemon plogicmp \$PLOGICMP
        touch /var/lock/subsys/protolog
        ;;
  stop)
        show Stopping protolog TCP daemon:
        killproc plogtcp
	show Stopping protolog UDP daemon:
	killproc plogudp
	show Stopping protolog ICMP daemon:
	killproc plogicmp
        rm -f /var/lock/subsys/protolog
        ;;
  status)
        status protolog
        ;;
  restart)
        \$0 stop
	\$0 start
        ;;
  *)
        echo "Usage: \$0 {start|stop|status|restart}"
        exit 1
esac

exit 0
EOF

cat  << EOF > $RPM_BUILD_ROOT/etc/protolog.conf
#
# Opcje dla plogtcp - TCP packet logger
# zobacz:	man plogtcp
PLOGTCP="-qlri \`hostname --ip-address\`"

# Opcje dla plogudp - UDP packet logger
# zobacz:	man plogudp
PLOGUDP="-qli \`hostname --ip-address\`"

# Opcje dla plogicmp - ICMP packet logger
# zobacz:	man plogicmp
PLOGICMP="-qlri \`hostname --ip-address\`"

EOF

install %{SOURCE1} $RPM_BUILD_ROOT/etc/logrotate.d/%{name}

bzip2 -9 $RPM_BUILD_ROOT%{_mandir}/man8/*

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add protolog

%preun
/sbin/chkconfig --del protolog

%files
%defattr(644,root,root,755)
%doc doc/BUGS doc/README

%attr(755,root,root) %{_sbindir}/*
%attr(754,root,root) /etc/rc.d/init.d/protolog
%attr(750,root,root) %dir /var/log/protolog
%attr(640,root,root) %config(noreplace) %verify(not md5 size mtime) /var/log/protolog/*
%attr(640,root,root) /etc/logrotate.d/protolog
%attr(640,root,root) %config /etc/protolog.conf
 %{_mandir}/man8/*
