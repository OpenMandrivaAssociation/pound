Summary:	A reverse-proxy and load-balancer
Name:		pound
Version:	2.6
Release:	%mkrel 1
Group:		System/Servers
License:	GPLv2
URL:		http://www.apsis.ch/pound/
Source0:	http://www.apsis.ch/pound/Pound-%{version}.tgz
Source1:	pound.cfg
Source2:	pound.init
Source3:	pound-openssl.cnf
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
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

install -m0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/pound/pound.cfg
install -m0755 %{SOURCE2} %{buildroot}%{_initrddir}/%{name}
install -m0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/pki/%{name}/%{name}.cnf

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


%changelog
* Mon Feb 20 2012 Dmitry Mikhirev <dmikhirev@mandriva.org> 2.6-1mdv2011.0
+ Revision: 778153
- new version 2.6
- dropped patch applied upstream

* Tue Dec 07 2010 Oden Eriksson <oeriksson@mandriva.com> 2.5-3mdv2011.0
+ Revision: 614607
- the mass rebuild of 2010.1 packages

* Thu Apr 15 2010 Funda Wang <fwang@mandriva.org> 2.5-2mdv2010.1
+ Revision: 534995
- add fedora patch to build with openssl 1.0

* Tue Mar 02 2010 Sandro Cazzaniga <kharec@mandriva.org> 2.5-1mdv2010.1
+ Revision: 513603
- update to 2.5
- fix license
- drop old patch (that was applied upstream)

* Mon Jun 22 2009 Oden Eriksson <oeriksson@mandriva.com> 2.4.4-1mdv2010.0
+ Revision: 387979
- 2.4.4

* Sun Sep 07 2008 Oden Eriksson <oeriksson@mandriva.com> 2.4.3-1mdv2009.0
+ Revision: 282184
- 2.4.3

* Fri Aug 01 2008 Thierry Vignaud <tv@mandriva.org> 2.2.3-4mdv2009.0
+ Revision: 259250
- rebuild

* Thu Jul 24 2008 Thierry Vignaud <tv@mandriva.org> 2.2.3-3mdv2009.0
+ Revision: 247165
- rebuild

* Wed Jan 02 2008 Olivier Blin <blino@mandriva.org> 2.2.3-1mdv2008.1
+ Revision: 140735
- restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request


* Fri Jan 26 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.3-1mdv2007.0
+ Revision: 114141
- 2.2.3
- reworked the config, initscript and added ssl cert generation
- Import pound

* Sat Feb 04 2006 Spencer Anderson <sdander@mandriva.org> 2.0-1mdk
- 2.0
- use mkrel

* Mon Aug 22 2005 Spencer Anderson <sdander@mandriva.org> 1.9-1mdk
- 1.9

* Sun Dec 12 2004 Spencer Anderson <sdander@oberon.ark.com> 1.8-1mdk
- 1.8

* Wed May 26 2004 Spencer Anderson <sdander@oberon.ark.com> 1.7-1mdk
- 1.7

* Fri Feb 27 2004 Olivier Thauvin <thauvin@aerov.jussieu.fr> 1.6-2mdk
- Own %%{_sysconfdir}/pound

