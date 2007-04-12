#Module-Specific definitions
%define mod_name mod_parmguard
%define mod_conf A18_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Mod_parmguard is a DSO module for the apache web server
Name:		apache-%{mod_name}
Version:	1.3c
Release:	%mkrel 4
Group:		System/Servers
License:	GPL
URL:		http://www.trickytools.com/php/mod_parmguard.php
Source0:	http://www.trickytools.com/downloads/%{mod_name}-%{version}.tar.bz2
Source1:	%{mod_conf}.bz2
Patch0:		mod_parmguard-1.3-soname_fix.diff
Patch1:		mod_parmguard-1.2-apache220_1.diff
Patch2:		mod_parmguard-1.2-apache220_2.diff
Patch3:		mod_parmguard-1.3-checkconf.diff
BuildRequires:	autoconf2.5
BuildRequires:	automake1.7
BuildRequires:	libtool
BuildRequires:	libxml2-devel
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file
Provides:	apache2-mod_parmguard
Obsoletes:	apache2-mod_parmguard
Epoch:		1
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_parmguard is an apache module that intercepts the HTTP
requests and validates the values of request parameters. If values
do not match the criteria, the request is rejected.

%prep

%setup -q -n %{mod_name}-1.3
%patch0 -p0 -b .soname
%patch1 -p0 -b .apache220_1
%patch2 -p1 -b .apache220_2
%patch3 -p0 -b .checkconf

# fix strange perms
find doc/manual -type f | xargs chmod 644

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build
export WANT_AUTOCONF_2_5=1
rm -f missing
libtoolize --copy --force; aclocal-1.7; autoconf; automake-1.7 --add-missing

%configure2_5x \
    --with-apxs2=%{_sbindir}/apxs

make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

cp -rp src/.libs .

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
bzcat %{SOURCE1} > %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

install -d %{buildroot}%{_var}/www/html/addon-modules
ln -s ../../../..%{_docdir}/%{name}-%{version} %{buildroot}%{_var}/www/html/addon-modules/%{name}-%{version}

# make the example/tests work... (ugly, but it works...)
perl -pi -e "s|_REPLACE_ME_|%{name}-%{version}|g" %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

# install the checkconf tool
install -d %{buildroot}%{_bindir}
install -m0755 src/checkconf %{buildroot}%{_bindir}/%{mod_name}-checkconf

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
%doc AUTHORS ChangeLog INSTALL NEWS README TODO doc/manual/* doc/test generator
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%attr(0755,root,root) %{_bindir}/%{mod_name}-checkconf
%{_var}/www/html/addon-modules/*


