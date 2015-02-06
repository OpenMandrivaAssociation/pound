Summary:	A reverse-proxy and load-balancer
Name:		pound
Version:	2.7c
Release:	2
Group:		System/Servers
License:	GPLv2
URL:		http://www.apsis.ch/pound/
Source0:	http://www.apsis.ch/pound/Pound-%{version}.tgz
Source1:	pound.cfg
Source2:	pound.service
Source3:	pound-openssl.cnf
Requires:	openssl
BuildRequires:	openssl-devel
BuildRequires:	openssl
BuildRequires:	pcre-devel

%description
The Pound program is a reverse proxy, load balancer and HTTPS
front-end for Web server(s).

%prep
%setup -q -n Pound-%{version}

%build
%configure2_5x
%make

%install
install -d %{buildroot}%{_unitdir}
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_mandir}/man8
install -d %{buildroot}%{_sysconfdir}/pound
install -d %{buildroot}%{_sysconfdir}/pki/%{name}/certs
install -d %{buildroot}/var/run/pound

install -m0755 pound %{buildroot}%{_sbindir}
install -m0755 poundctl %{buildroot}%{_sbindir}
install -m0644 *.8 %{buildroot}%{_mandir}/man8/

install -m0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/pound/pound.cfg
install -m0755 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service
install -m0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/pki/%{name}/%{name}.cnf

touch %{buildroot}%{_sysconfdir}/pki/%{name}/certs/%{name}.pem
chmod 600 %{buildroot}%{_sysconfdir}/pki/%{name}/certs/%{name}.pem

%pre
%_pre_useradd %{name} /var/run/pound /bin/false

%post
%systemd_post pound.service
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
%systemd_preun pound.service

%postun
%systemd_postun_with_restart pound.service

%files
%defattr(644,root,root,755)
%doc README
%{_unitdir}/%{name}.service
%attr(0755,root,root) %{_sbindir}/*
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/%{name}/%{name}.cfg
%attr(0600,root,root) %ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{_sysconfdir}/pki/%{name}/certs/%{name}.pem
%attr(0644,root,root) %config(missingok,noreplace) %verify(not md5 size mtime) %{_sysconfdir}/pki/%{name}/%{name}.cnf
%{_mandir}/man8/*
%dir /var/run/pound
