#Module-Specific definitions
%define mod_name mod_fcgid
%define mod_conf A27_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Apache module for FastCGI
Name:		apache-%{mod_name}
Version:	2.3.2
Release:	%mkrel 0.1
Group:		System/Servers
License:	Apache License
URL:		http://www.apache.org
Source0:	http://httpd.apache.org/dev/dist/mod_fcgid/mod_fcgid-2.3.2.tar.gz
Source1:	http://httpd.apache.org/dev/dist/mod_fcgid/mod_fcgid-2.3.2.tar.gz.asc
Source2:	%{mod_conf}
BuildRequires:	file
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
Epoch:		1
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_fcgid is a binary compatibility alternative to Apache module mod_fastcgi.
mod_fcgid has a new process management strategy, which concentrates on reducing
the number of fastcgi server, and kick out the corrupt fastcgi server as soon
as possible.

%prep

%setup -q -n %{mod_name}-%{version}

cp %{SOURCE2} %{mod_conf}

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build

# still a bit ugly

pushd modules/fcgid
cp fcgid_config.h.in fcgid_config.h
%{_sbindir}/apxs -I. -c mod_fcgid.c fcgid_bridge.c fcgid_conf.c fcgid_pm_main.c \
    fcgid_protocol.c fcgid_spawn_ctl.c  fcgid_proctbl_unix.c fcgid_pm_unix.c \
    fcgid_proc_unix.c fcgid_bucket.c fcgid_filter.c
popd

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}/var/lib/%{name}

install -m0755 modules/fcgid/.libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

# fix docs
cp modules/fcgid/ChangeLog ChangeLog.old
cp docs/manual/mod/mod_fcgid.html.en mod_fcgid.html

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc ChangeLog.old *-FCGID mod_fcgid.html
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%attr(0755,apache,apache) %dir /var/lib/%{name}
