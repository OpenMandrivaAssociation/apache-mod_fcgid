#Module-Specific definitions
%define mod_name mod_fcgid
%define load_order 227

Summary:	Apache module for FastCGI
Name:		apache-%{mod_name}
Version:	2.3.6
Release:	14
Group:		System/Servers
License:	Apache License
URL:		http://www.apache.org
Source0:	http://httpd.apache.org/dev/dist/mod_fcgid/mod_fcgid-%{version}.tar.gz
Source1:	http://httpd.apache.org/dev/dist/mod_fcgid/mod_fcgid-%{version}.tar.gz.asc
Patch0:		mod_fcgid-2.3.6-CVE-2012-1181.diff
BuildRequires:	file
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
Epoch:		1

%description
mod_fcgid is a binary compatibility alternative to Apache module mod_fastcgi.
mod_fcgid has a new process management strategy, which concentrates on reducing
the number of fastcgi server, and kick out the corrupt fastcgi server as soon
as possible.

%prep

%setup -q -n %{mod_name}-%{version}
%patch0 -p0

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build

# still a bit ugly

pushd modules/fcgid
cp fcgid_config.h.in fcgid_config.h
%{_bindir}/apxs -I. -c mod_fcgid.c fcgid_bridge.c fcgid_conf.c fcgid_pm_main.c \
    fcgid_protocol.c fcgid_spawn_ctl.c fcgid_proctbl_unix.c fcgid_pm_unix.c \
    fcgid_proc_unix.c fcgid_bucket.c fcgid_filter.c fcgid_mutex_unix.c
popd

%install

install -d %{buildroot}%{_libdir}/apache
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}/var/lib/%{name}

install -m0755 modules/fcgid/.libs/*.so %{buildroot}%{_libdir}/apache/

cat > %{buildroot}%{_sysconfdir}/httpd/modules.d/%{load_order}_%{mod_name}.conf << EOF
LoadModule fcgid_module	%{_libdir}/apache/%{mod_name}.so

#FcgidIPCDir - fastcgi socket file path
FcgidIPCDir /var/lib/%{name}

# Use FastCGI to process .fcg .fcgi & .fpl scripts
# Don't do this if mod_fastcgi is present, as it will try to do the same thing
AddHandler fcgid-script fcg fcgi fpl
EOF

# fix docs
cp modules/fcgid/ChangeLog ChangeLog.old
cp docs/manual/mod/mod_fcgid.html.en mod_fcgid.html

%post
/bin/systemctl daemon-reload >/dev/null 2>&1 || :

%postun
if [ "$1" = "0" ]; then
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%files
%doc ChangeLog.old *-FCGID mod_fcgid.html
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/*.conf
%attr(0755,root,root) %{_libdir}/apache/*.so
%attr(0755,apache,apache) %dir /var/lib/%{name}


%changelog
* Thu Mar 22 2012 Oden Eriksson <oeriksson@mandriva.com> 1:2.3.6-4
+ Revision: 786011
- adapt...
- grr...
- fix the path to apxs
- fix CVE-2012-1181
- various fixes

* Sat Feb 11 2012 Oden Eriksson <oeriksson@mandriva.com> 1:2.3.6-3
+ Revision: 772654
- rebuild

* Tue May 24 2011 Oden Eriksson <oeriksson@mandriva.com> 1:2.3.6-2
+ Revision: 678313
- mass rebuild
- 2.3.6

* Thu Nov 04 2010 Oden Eriksson <oeriksson@mandriva.com> 1:2.3.6-0.1mdv2011.0
+ Revision: 593299
- 2.3.6 (pre-release)

* Sun Oct 24 2010 Oden Eriksson <oeriksson@mandriva.com> 1:2.3.5-0.3mdv2011.0
+ Revision: 587983
- rebuild

* Mon Mar 08 2010 Oden Eriksson <oeriksson@mandriva.com> 1:2.3.5-0.2mdv2010.1
+ Revision: 516100
- rebuilt for apache-2.2.15

* Wed Jan 27 2010 Oden Eriksson <oeriksson@mandriva.com> 1:2.3.5-0.1mdv2010.1
+ Revision: 497126
- 2.3.5 (pre-release)
- update the config

* Tue Sep 29 2009 Oden Eriksson <oeriksson@mandriva.com> 1:2.3.2-0.1mdv2010.0
+ Revision: 450850
- 2.3.2 (pre-release)

* Wed Sep 09 2009 Oden Eriksson <oeriksson@mandriva.com> 1:2.3.1-0.1mdv2010.0
+ Revision: 435478
- 2.3.1 (pre-release of the asf incubated mod_fcgid)

* Sat Aug 01 2009 Oden Eriksson <oeriksson@mandriva.com> 1:2.2-7mdv2010.0
+ Revision: 406584
- rebuild

* Tue Jan 06 2009 Oden Eriksson <oeriksson@mandriva.com> 1:2.2-6mdv2009.1
+ Revision: 325752
- rebuild

* Mon Jul 14 2008 Oden Eriksson <oeriksson@mandriva.com> 1:2.2-5mdv2009.0
+ Revision: 234947
- rebuild

* Thu Jun 05 2008 Oden Eriksson <oeriksson@mandriva.com> 1:2.2-4mdv2009.0
+ Revision: 215579
- fix rebuild
- hard code %%{_localstatedir}/lib to ease backports

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

* Fri Mar 07 2008 Oden Eriksson <oeriksson@mandriva.com> 1:2.2-3mdv2008.1
+ Revision: 181733
- rebuild

* Mon Feb 18 2008 Thierry Vignaud <tv@mandriva.org> 1:2.2-2mdv2008.1
+ Revision: 170721
- rebuild
- fix "foobar is blabla" summary (=> "blabla") so that it looks nice in rpmdrake
- kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Sat Oct 13 2007 Oden Eriksson <oeriksson@mandriva.com> 1:2.2-1mdv2008.1
+ Revision: 98022
- 2.2

* Sat Sep 08 2007 Oden Eriksson <oeriksson@mandriva.com> 1:2.1-2mdv2008.0
+ Revision: 82579
- rebuild

* Wed May 16 2007 Oden Eriksson <oeriksson@mandriva.com> 1:2.1-1mdv2008.0
+ Revision: 27179
- 2.1


* Sat Mar 10 2007 Oden Eriksson <oeriksson@mandriva.com> 2.0-2mdv2007.1
+ Revision: 140676
- rebuild

* Fri Jan 12 2007 Oden Eriksson <oeriksson@mandriva.com> 1:2.0-1mdv2007.1
+ Revision: 107876
- 2.0
- sync somewhat with fc extras
- bunzip the config
- drop the apache220 patch, fixed upstream

* Thu Nov 09 2006 Oden Eriksson <oeriksson@mandriva.com> 1:1.07-4mdv2007.1
+ Revision: 79424
- Import apache-mod_fcgid

* Mon Aug 07 2006 Oden Eriksson <oeriksson@mandriva.com> 1:1.07-4mdv2007.0
- rebuild

* Fri Mar 03 2006 Michael Scherer <misc@mandriva.org> 1:1.07-3mdk
- enhance summary
- enable .fcgi handling by default

* Wed Dec 21 2005 Oden Eriksson <oeriksson@mandriva.com> 1:1.07-2mdk
- rebuilt against apache-2.2.0 (P0)

* Mon Nov 28 2005 Oden Eriksson <oeriksson@mandriva.com> 1:1.07-1mdk
- 1.07
- fix versioning
- fix dl url

* Sun Jul 31 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54_1.04-2mdk
- fix deps

* Fri Jun 03 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54_1.04-1mdk
- rename the package
- the conf.d directory is renamed to modules.d
- use new rpm-4.4.x pre,post magic

* Sun Mar 20 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53_1.04-4mdk
- use the %1

* Mon Feb 28 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53_1.04-3mdk
- fix %%post and %%postun to prevent double restarts
- fix bug #6574

* Wed Feb 16 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53_1.04-2mdk
- spec file cleanups, remove the ADVX-build stuff

* Mon Feb 14 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53_1.04-1mdk
- 1.04
- strip away annoying ^M

* Tue Feb 08 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53_1.03-1mdk
- rebuilt for apache 2.0.53

* Fri Nov 19 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.52_1.03-2mdk
- fix deps

* Fri Nov 19 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.52_1.03-1mdk
- initial mandrake package

