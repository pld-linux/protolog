Summary:     The Internet Protocols logger
Summary(pl): Program zapisuj±cy informacje zwi±zane z protoko³ami Internetowymi
Name:        protolog
Version:     1.0.6
Release:     1d
Copyright:   GPL
Group:       Networking
Group(pl):   Sieciowe
Vendor:	     Diego Javier Grigna <diego@grigna.com>
URL:	     http://www.grigna.com/diego/linux/
#######      ftp://sunsite.unc.edu/pub/Linux/system/network/monitor
Source:	     %{name}-%{version}.tar.gz
Patch0:	     %{name}-1.0.6.make.diff
Patch1:	     %{name}-1.0.6.quiet.diff
Patch2:	     %{name}-1.0.2.console.diff
Buildroot:   /var/tmp/buildroot-%{name}-%{version}

%description
It consists of three daemons that logs incoming
IP/TCP, IP/UDP and IP/ICMP packets.
						
%description -l pl
Pakiet zawiera trzy deamony loguj±ce informacjê na temat
przychodz±cych pakietów IP/TCP, IP/UDP oraz IP/ICMP.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
make -C src OPT="$RPM_OPT_FLAGS"

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/{etc/{rc.d/init.d,logrotate.d},usr/{sbin,man/man8}}

make -C src install \
bindir=$RPM_BUILD_ROOT/usr/sbin \
mandir=$RPM_BUILD_ROOT/usr/man/man8 \
logdir=$RPM_BUILD_ROOT/var/log/protolog

touch $RPM_BUILD_ROOT/var/log/protolog/{icmp.log,icmp.raw,tcp.log,tcp.raw}
touch $RPM_BUILD_ROOT/var/log/protolog/{udp.log,udp.raw}

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

PLOGTCP=
PLOGUDP=
PLOGICMP=

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
PLOGTCP="-lri \`hostname --ip-address\`"

# Opcje dla plogudp - UDP packet logger
# zobacz:	man plogudp
PLOGUDP="-li \`hostname --ip-address\`"

# Opcje dla plogicmp - ICMP packet logger
# zobacz:	man plogicmp
PLOGICMP="-lri \`hostname --ip-address\`"

EOF

cat  << EOF > $RPM_BUILD_ROOT/etc/logrotate.d/protolog
compress

/var/log/protolog/icmp.log {
	daily
	rotate 28
}

/var/log/protolog/icmp.raw {
        daily
	rotate 28
}

/var/log/protolog/tcp.log {
	daily
	rotate 28
}

/var/log/protolog/tcp.raw {
	daily
	rotate 28
}

/var/log/protolog/udp.log {
	daily
	rotate 28
}

/var/log/protolog/udp.raw {
	daily
	rotate 28
}

EOF

gzip -9fn $RPM_BUILD_ROOT/usr/man/man8/*
bzip2 -9 doc/BUGS doc/README

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add protolog

%preun
if [ $0 = 1]; then
    /sbin/chkconfig --del protolog
fi

%files
%defattr(644,root,root,755)
%doc doc/BUGS.bz2 doc/README.bz2

%attr(755,root,root) /usr/sbin/*
%attr(700,root,root) /etc/rc.d/init.d/protolog
%attr(750,root,root) %dir /var/log/protolog
%attr(640,root,root) %config(noreplace) %verify(not md5 size mtime) /var/log/protolog/*
%attr(640,root,root) /etc/logrotate.d/protolog
%attr(640,root,root) %config /etc/protolog.conf
%attr(644,root, man) /usr/man/man8/*

%changelog
* Wed Feb 03 1999 Arkadiusz Mi¶kiewicz <misiek@misiek.eu.org>
  [1.0.6-1d]
- new upstream release
- new rc-scripts ready

* Mon Jan 18 1999 Arkadiusz Mi¶kiewicz <misiek@pld.za.net>
  [1.0.2-1d]
- added logrotate config
- added console patch

* Sun Jan 17 1999 Arkadiusz Mi¶kiewicz <misiek@pld.za.net>
  [1.0.2-1d]
- initial RPM release
- TODO: logrotate config
