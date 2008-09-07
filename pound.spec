Summary:	A reverse-proxy and load-balancer
Name:		pound
Version:	2.4.3
Release:	%mkrel 1
Group:		System/Servers
License:	GPL
URL:		http://www.apsis.ch/pound/
Source0:	http://www.apsis.ch/pound/Pound-%{version}.tgz
Source1:	pound.cfg
Source2:	pound.init
Source3:	pound-openssl.cnf
Patch0:		Pound-mdv_conf.diff
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires:	openssl
BuildRequires:	openssl-devel
BuildRequires:	pcre-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
The Pound program is a reverse proxy, load balancer and HTTPS
front-end for Web server(s).

%prep

%setup -q -n Pound-%{version}
%patch0 -p1

cp %{SOURCE1} %{name}.cfg
cp %{SOURCE2} %{name}.init
cp %{SOURCE3} %{name}-openssl.cnf

%build

%configure2_5x
 
%make

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_mandir}/man8
install -d %{buildroot}%{_sysconfdir}/pound
install -d %{buildroot}%{_sysconfdir}/pki/%{name}/certs
install -d %{buildroot}/var/run/pound

install -m0755 pound %{buildroot}%{_sbindir}
install -m0755 poundctl %{buildroot}%{_sbindir}
install -m0644 *.8 %{buildroot}%{_mandir}/man8/

install -m0644 pound.cfg %{buildroot}%{_sysconfdir}/pound/pound.cfg
install -m0755 %{name}.init %{buildroot}%{_initrddir}/%{name}
install -m0644 %{name}-openssl.cnf %{buildroot}%{_sysconfdir}/pki/%{name}/%{name}.cnf

touch %{buildroot}%{_sysconfdir}/pki/%{name}/certs/%{name}.pem
chmod 600 %{buildroot}%{_sysconfdir}/pki/%{name}/certs/%{name}.pem

%pre
%_pre_useradd %{name} /var/run/pound /bin/false

%post
%_post_service %{name}
if [ -f /var/lock/subsys/%{name} ]; then
    %{_initrddir}/%{name} restart 1>&2;
fi

# create a ssl cert
if [ ! -f %{_sysconfdir}/pki/%{name}/certs/%{name}.pem ]; then
    echo "Generating a SSL certificate for %{name}"
    openssl req -x509 -newkey rsa:1024 -batch -keyout \
    %{_sysconfdir}/pki/%{name}/certs/%{name}.pem \
    -out %{_sysconfdir}/pki/%{name}/certs/%{name}.pem \
    -days 365 -nodes -config %{_sysconfdir}/pki/%{name}/%{name}.cnf
    chmod 600 %{_sysconfdir}/pki/%{name}/certs/%{name}.pem
fi

%preun
%_preun_service %{name}
    
%postun
%_postun_userdel %{name}

if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/%{name} ]; then
	%{_initrddir}/%{name} restart 1>&2
    fi
fi

%clean
rm -rf %{buildroot}

%files
%defattr(644,root,root,755)
%doc README
%attr(0755,root,root) %{_initrddir}/%{name}
%attr(0755,root,root) %{_sbindir}/*
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/%{name}/%{name}.cfg
%attr(0600,root,root) %ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{_sysconfdir}/pki/%{name}/certs/%{name}.pem
%attr(0644,root,root) %config(missingok,noreplace) %verify(not md5 size mtime) %{_sysconfdir}/pki/%{name}/%{name}.cnf
%{_mandir}/man8/*
%dir /var/run/pound


