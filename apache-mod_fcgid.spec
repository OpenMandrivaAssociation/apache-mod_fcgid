#Module-Specific definitions
%define mod_name mod_fcgid
%define load_order 227

Summary:	Apache module for FastCGI
Name:		apache-%{mod_name}
Version:	2.3.6
Release:	4
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
