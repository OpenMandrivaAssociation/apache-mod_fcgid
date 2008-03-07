#Module-Specific definitions
%define mod_name mod_fcgid
%define mod_conf A27_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Apache module for FastCGI
Name:		apache-%{mod_name}
Version:	2.2
Release:	%mkrel 3
Group:		System/Servers
License:	GPL
URL:		http://fastcgi.coremail.cn/
Source0:	http://fastcgi.coremail.cn/%{mod_name}.%{version}.tgz
Source1:	%{mod_conf}
Source2:        http://fastcgi.coremail.cn/doc.htm
Source3:        http://fastcgi.coremail.cn/configuration.htm
Patch0:         mod_fcgid.1.09-docurls.patch
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
mod_fcgid is a binary compatibility alternative to Apache module
mod_fastcgi. mod_fcgid has a new process management strategy,
which concentrates on reducing the number of fastcgi server, and
kick out the corrupt fastcgi server as soon as possible.

%prep

%setup -q -n %{mod_name}.%{version}

# cleanup
rm -rf .libs .deps 

cp %{SOURCE1} %{mod_conf}

cp %{SOURCE2} directives.htm
cp %{SOURCE3} .

%patch0 -p1

# fix strange perms
chmod 644 AUTHOR ChangeLog INSTALL.txt

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build
#My_Flags=`%{_sbindir}/apxs -q CFLAGS`

#make \
#    top_dir=%{_libdir}/apache \
#    CFLAGS="$My_Flags -I."

%{_sbindir}/apxs -I. -c mod_fcgid.c fcgid_bridge.c fcgid_conf.c fcgid_pm_main.c fcgid_protocol.c fcgid_spawn_ctl.c \
arch/unix/fcgid_proctbl_unix.c arch/unix/fcgid_pm_unix.c arch/unix/fcgid_proc_unix.c fcgid_bucket.c fcgid_filter.c

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}%{_localstatedir}/%{name}

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

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
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHOR COPYING ChangeLog INSTALL.txt configuration.htm directives.htm
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%attr(0755,apache,apache) %dir %{_localstatedir}/%{name}
