#Module-Specific definitions
%define mod_name mod_parmguard
%define mod_conf A18_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	DSO module for the apache web server
Name:		apache-%{mod_name}
Version:	1.3c
Release:	17
Group:		System/Servers
License:	GPL
URL:		https://www.trickytools.com/php/mod_parmguard.php
Source0:	http://www.trickytools.com/downloads/%{mod_name}-%{version}.tar.bz2
Source1:	%{mod_conf}.bz2
Patch0:		mod_parmguard-1.3-soname_fix.diff
Patch1:		mod_parmguard-1.2-apache220_1.diff
Patch2:		mod_parmguard-1.2-apache220_2.diff
Patch3:		mod_parmguard-1.3-checkconf.diff
Patch4:		mod_parmguard-1.3-format_not_a_string_literal_and_no_format_arguments.diff
BuildRequires:	autoconf2.5
BuildRequires:	automake
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
Epoch:		1

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
%patch4 -p0 -b .format_not_a_string_literal_and_no_format_arguments

# fix strange perms
find doc/manual -type f | xargs chmod 644

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build
export WANT_AUTOCONF_2_5=1
rm -f missing
libtoolize --copy --force; aclocal; autoconf; automake --add-missing

%configure2_5x --localstatedir=/var/lib \
    --with-apxs2=%{_bindir}/apxs

make

%install

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

%files
%doc AUTHORS ChangeLog INSTALL NEWS README TODO doc/manual/* doc/test generator
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%attr(0755,root,root) %{_bindir}/%{mod_name}-checkconf
%{_var}/www/html/addon-modules/*




%changelog
* Sat Feb 11 2012 Oden Eriksson <oeriksson@mandriva.com> 1:1.3c-16mdv2012.0
+ Revision: 772713
- rebuild

* Tue May 24 2011 Oden Eriksson <oeriksson@mandriva.com> 1:1.3c-15
+ Revision: 678385
- mass rebuild

* Mon Jan 03 2011 Oden Eriksson <oeriksson@mandriva.com> 1:1.3c-14mdv2011.0
+ Revision: 627733
- don't force the usage of automake1.7

* Sun Oct 24 2010 Oden Eriksson <oeriksson@mandriva.com> 1:1.3c-13mdv2011.0
+ Revision: 588043
- rebuild

* Mon Mar 08 2010 Oden Eriksson <oeriksson@mandriva.com> 1:1.3c-12mdv2010.1
+ Revision: 516160
- rebuilt for apache-2.2.15

* Sat Aug 01 2009 Oden Eriksson <oeriksson@mandriva.com> 1:1.3c-11mdv2010.0
+ Revision: 406631
- rebuild

* Wed Jan 07 2009 Oden Eriksson <oeriksson@mandriva.com> 1:1.3c-10mdv2009.1
+ Revision: 326500
- rediff patches
- fix build with -Werror=format-security

* Mon Jul 14 2008 Oden Eriksson <oeriksson@mandriva.com> 1:1.3c-9mdv2009.0
+ Revision: 235066
- rebuild

* Thu Jun 05 2008 Oden Eriksson <oeriksson@mandriva.com> 1:1.3c-8mdv2009.0
+ Revision: 215617
- fix rebuild
- hard code %%{_localstatedir}/lib to ease backports

* Fri Mar 07 2008 Oden Eriksson <oeriksson@mandriva.com> 1:1.3c-7mdv2008.1
+ Revision: 181824
- rebuild

* Mon Feb 18 2008 Thierry Vignaud <tv@mandriva.org> 1:1.3c-6mdv2008.1
+ Revision: 170738
- rebuild
- fix "foobar is blabla" summary (=> "blabla") so that it looks nice in rpmdrake
- kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Sat Sep 08 2007 Oden Eriksson <oeriksson@mandriva.com> 1:1.3c-5mdv2008.0
+ Revision: 82647
- rebuild


* Sat Mar 10 2007 Oden Eriksson <oeriksson@mandriva.com> 1.3c-4mdv2007.1
+ Revision: 140724
- rebuild

* Thu Nov 09 2006 Oden Eriksson <oeriksson@mandriva.com> 1:1.3c-3mdv2007.1
+ Revision: 79473
- Import apache-mod_parmguard

* Mon Aug 07 2006 Oden Eriksson <oeriksson@mandriva.com> 1:1.3c-3mdv2007.0
- rebuild

* Sun Apr 16 2006 Oden Eriksson <oeriksson@mandriva.com> 1:1.3c-2mdk
- fix build against apache-2.2.x
- fix the apache config

* Mon Nov 28 2005 Oden Eriksson <oeriksson@mandriva.com> 1:1.3c-1mdk
- 1.3c
- fix versioning
- fix dl url

* Sun Jul 31 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54_1.3-2mdk
- fix deps

* Fri Jun 03 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54_1.3-1mdk
- rename the package
- the conf.d directory is renamed to modules.d
- use new rpm-4.4.x pre,post magic

* Sun Mar 20 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53_1.3-4mdk
- use the %1

* Mon Feb 28 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53_1.3-3mdk
- fix %%post and %%postun to prevent double restarts
- fix bug #6574

* Wed Feb 16 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53_1.3-2mdk
- spec file cleanups, remove the ADVX-build stuff

* Tue Feb 08 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53_1.3-1mdk
- rebuilt for apache 2.0.53

* Wed Sep 29 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.52_1.3-1mdk
- built for apache 2.0.52

* Fri Sep 17 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.51_1.3-1mdk
- built for apache 2.0.51

* Wed Sep 01 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.50_1.3-1mdk
- 1.3
- fix P0
- added P2

* Tue Jul 13 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.50_1.2-1mdk
- built for apache 2.0.50
- remove redundant provides

* Tue Jun 15 2004 Oden Eriksson <oden.eriksson@kvikkjokk.net> 2.0.49_1.2-1mdk
- built for apache 2.0.49
- added P1

