%define _default_patch_fuzz 2

%define glib2_version 2.6.0
%define libbonobo_version 2.13.0
%define libxml2_version 2.5
%define libxslt_version 1.0.19
%define gconf2_version 2.14
%define gnome_vfs2_version 2.5.3
%define orbit2_version 2.5.1
%define gconf_version 2.14

%define po_package libgnome-2.0

Summary: GNOME base library
Name: libgnome
Version: 2.28.0
Release: 11%{?dist}
URL: http://www.gnome.org
Source0: http://download.gnome.org/sources/libgnome/2.28/%{name}-%{version}.tar.bz2
Source1: desktop_gnome_peripherals_monitor.schemas
License: LGPLv2+
Group: System Environment/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires(pre):  GConf2 >= %{gconf2_version}
Requires(preun):  GConf2 >= %{gconf2_version}
Requires(post):  GConf2 >= %{gconf2_version}
# Added to avoid the warning messages about utmp group, bug #24171
# fixme, just libzvt?
Requires(pre): utempter
Requires(post): GConf2
Requires(pre): GConf2
Requires(preun): GConf2

BuildRequires:	zlib-devel
BuildRequires:	glib2-devel >= %{glib2_version}
BuildRequires:  libbonobo-devel >= %{libbonobo_version}
BuildRequires:  GConf2-devel >= %{gconf2_version}
BuildRequires:  gnome-vfs2-devel >= %{gnome_vfs2_version}
BuildRequires:  libxml2-devel >= %{libxml2_version}
BuildRequires:  ORBit2-devel >= %{orbit2_version}
BuildRequires:  libxslt-devel >= %{libxslt_version}
BuildRequires:  intltool
BuildRequires:  libtool
BuildRequires:  gettext
BuildRequires:  popt-devel

Requires: system-gnome-theme >= 60.0.0

# make sure to update gnome-desktop requires when changing below patch
Patch1: default-background.patch
Patch2: libgnome-2.11.1-scoreloc.patch
Patch3: libgnome-2.7.2-default-cursor.patch
Patch4: libgnome-2.8.0-default-browser.patch
Patch6: libgnome-2.19.1-default-settings.patch
Patch7: libgnome-2.22.0-default-sound-effects.patch

# backport from upstream svn
Patch8: im-setting.patch

Patch9: libgnome-2.24.1-default-noblink.patch

# updated translations
# https://bugzilla.redhat.com/show_bug.cgi?id=589217
Patch10: libgnome-translations.patch

Patch11: default-theme.patch

%description

GNOME (GNU Network Object Model Environment) is a user-friendly set of
GUI applications and desktop tools to be used in conjunction with a
window manager for the X Window System. The libgnome package includes
non-GUI-related libraries that are needed to run GNOME. The libgnomeui
package contains X11-dependent GNOME library features.


%package devel
Summary: Libraries and headers for libgnome
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

Conflicts: gnome-libs-devel < 1.4.1.2
Requires: zlib-devel
Requires: ORBit2-devel >= %{orbit2_version}
Requires: glib2-devel >= %{glib2_version}
Requires: libbonobo-devel >= %{libbonobo_version}
Requires: GConf2-devel >= %{gconf2_version}
Requires: gnome-vfs2-devel >= %{gnome_vfs2_version}
Requires: libxml2-devel >= %{libxml2_version}
Requires: libxslt-devel >= %{libxslt_version}
Requires: popt-devel
Requires: pkgconfig
# for /usr/share/gtk-doc/html
Requires: gtk-doc

%description devel

GNOME (GNU Network Object Model Environment) is a user-friendly set of
GUI applications and desktop tools to be used in conjunction with a
window manager for the X Window System. The libgnome-devel package
includes the libraries and include files that you will need to
use libgnome.

You should install the libgnome-devel package if you would like to
compile GNOME applications. You do not need to install libgnome-devel
if you just want to use the GNOME desktop environment.

%prep
%setup -q

%patch1 -p1 -b .default-background
%patch2 -p1 -b .scoreloc
%patch3 -p1 -b .default-cursor
%patch4 -p1 -b .default-browser
%patch6 -p1 -b .default-settings
%patch7 -p1 -b .default-sound-effects
%patch8 -p1 -b .im-setting
%patch9 -p1 -b .default-noblink
%patch10 -p1 -b .translations
%patch11 -p1 -b .default-theme

%build
%configure --disable-gtk-doc --disable-static --disable-esd

export tagname=CC
make %{?_smp_mflags} LIBTOOL=%{_bindir}/libtool

# strip unneeded translations from .mo files
# ideally intltool (ha!) would do that for us
# http://bugzilla.gnome.org/show_bug.cgi?id=474987
cd po
grep -v ".*[.]desktop[.]in[.]in$\|.*[.]server[.]in[.]in$" POTFILES.in > POTFILES.keep
mv POTFILES.keep POTFILES.in
intltool-update --pot
sed -ie 's|POT-Creation-Date.*|POT-Creation-Date: 2008-10-01 00:00-0400\\n"|g' %{po_package}.pot
for p in *.po; do
  msgmerge $p %{po_package}.pot > $p.out
  msgfmt -o `basename $p .po`.gmo $p.out
done

%install
rm -rf $RPM_BUILD_ROOT
export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
export tagname=CC
%makeinstall LIBTOOL=%{_bindir}/libtool
unset GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL
cp %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/gconf/schemas/

rm $RPM_BUILD_ROOT%{_libdir}/*.{a,la}
rm -f $RPM_BUILD_ROOT%{_libdir}/bonobo/monikers/*.{a,la}

for serverfile in $RPM_BUILD_ROOT%{_libdir}/bonobo/servers/*.server; do
    sed -i -e 's|location *= *"/usr/lib\(64\)*/|location="/usr/$LIB/|' $serverfile
done

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/skel/.gnome2

# http://bugzilla.gnome.org/show_bug.cgi?id=477846
rm -rf $RPM_BUILD_ROOT%{_datadir}/gnome-background-properties
rm -rf $RPM_BUILD_ROOT%{_datadir}/pixmaps

%find_lang %{po_package}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule %{_sysconfdir}/gconf/schemas/desktop_gnome_*.schemas > /dev/null || :

%pre
if [ "$1" -gt 1 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/desktop_gnome_*.schemas > /dev/null || :
fi

%preun
if [ "$1" -eq 0 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/desktop_gnome_*.schemas > /dev/null || :
fi

%postun -p /sbin/ldconfig

%files -f %{po_package}.lang
%defattr(-,root,root)

%doc AUTHORS COPYING.LIB NEWS README

%{_bindir}/*
%{_libdir}/lib*.so.*
%{_libdir}/bonobo/monikers/*
%{_libdir}/bonobo/servers/*
%{_mandir}/man7/*
%{_sysconfdir}/gconf/schemas/*.schemas
%{_sysconfdir}/sound
%{_sysconfdir}/skel/.gnome2

%files devel
%defattr(-,root,root)

%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*
%{_includedir}/*
%{_datadir}/gtk-doc/html/*

%changelog
* Wed Jul 14 2010 Jon McCann <jmccann@redhat.com> 2.28.0-11
- Actually apply patch
  Resolves: #611864

* Wed Jul 14 2010 Jon McCann <jmccann@redhat.com> 2.28.0-10
- Change default theme
  Resolves: #611864

* Tue May 18 2010 Ray Strode <rstrode@redhat.com> 2.28.0-9
- more defaults changes
  Related: #566368

* Tue May 18 2010 Ray Strode <rstrode@redhat.com> 2.28.0-8
- Update libgnome theme defaults
  Related: #566368

* Fri May 14 2010 Matthias Clasen <mclasen@redhat.com> - 2.28.0-7
- Updated translations
Resolves: #589217

* Wed May 05 2010 Ray Strode <rstrode@redhat.com> 2.28.0-6
- Change theme requires
  Related: #566368

* Thu Jan 28 2010 Ray Strode <rstrode@redhat.com> 2.28.0-5
- Update default background

* Tue Dec 15 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-4
- Remove a useless static library that trips up some
  rpmlint-type checks

* Wed Sep 23 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-1
- Update to 2.28.0

* Mon Aug 10 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.5-1
- Update to 2.27.5

* Wed Aug  5 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-8
- Default to Clearlooks GTK+ theme

* Tue Aug  4 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-7
- Default to Constantine backgrounds

* Tue Aug  4 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-6
- Drop Leonidas backgrounds in anticipation of Constantine backgrounds

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.26.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 22 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-4
- Turn off icons in buttons and menus by default

* Thu Jul  2 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-3
- Rebuild

* Mon Apr 27 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-2
- Don't drop schemas translations from po files

* Tue Mar 17 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-1
- Update to 2.26.0

* Sun Mar 15 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.1-1
- Update to 2.25.1
- Drop explicit library requires

* Tue Mar 10 2009 Ray Strode <rstrode@redhat.com> - 2.24.1-10
- Change default backgrounds to leonidas ones

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.24.1-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Feb 3  2009 Matthew Garrett <mjg@redhat.com> - 2.24.1-9
- Default to a non-blinking cursor

* Tue Dec 9  2008 Ray Strode <rstrode@redhat.com> - 2.24.1-8
- Drop esound-devel requires (bug 475442)

* Tue Oct 28 2008 Ray Strode <rstrode@redhat.com> - 2.24.1-7
- move Requires: solar-backgrounds to gnome-desktop so
  KDE spin doesn't pull it in (Requested by Rex).

* Thu Oct 23 2008 Bill Nottingham <notting@redhat.com> - 2.24.1-6
- sed the pot file to avoid multilib issues (#468161)

* Tue Oct 21 2008 Ray Strode <rstrode@redhat.com> - 2.24.1-5
- Default to "solar" instead of "waves"

* Tue Sep 30 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.1-4
- Fix multilib conflicts with touch

* Thu Sep 25 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.1-2
- Save some space

* Mon Sep 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.1-1
- Update to 2.24.1

* Mon Sep 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.0-2
- Update to 2.24.0

* Fri Aug 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.5-1
- Update to 2.23.5

* Thu Aug 14 2008 - Lennart Poettering <lpoetter@redhat.com> - 2.23.4-3
- Disable esd support since we have libcanberra now

* Fri Jul 25 2008 - Bastien Nocera <bnocera@redhat.com> - 2.23.4-2
- Remove the "esound by default" patch, it's obsoleted by
  changes in gnome-settings-daemon
- Add patch to support the new sound theme XSettings

* Tue Jun 17 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.4-1
- Update to 2.23.4

* Wed Jun  4 2008 Tomas Bzatek <tbzatek@redhat.com> - 2.23.3-1
- Update to 2.23.3

* Sun Apr  6 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-3
- Switch to waves as the default background

* Wed Mar 26 2008 - Bastien Nocera <bnocera@redhat.com> - 2.22.0-2
- Have the sound effects turned on by default (#438483)

* Mon Mar 10 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-1
- Update to 2.22.0

* Mon Mar 10 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.91-1
- Update to 2.21.91

* Fri Feb 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.90-3
- Make gio the default filechooser backend

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 2.21.90-2
- Autorebuild for GCC 4.3

* Tue Jan 29 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.90-1
- Update to 2.21.90

* Wed Jan 16 2008 Matthias Clasen <mclasen@redhat.com> - 2.20.1-4
- Make gvfs the default filechooser backend

* Tue Dec 18 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-3
- Add schema for gtk-im-module GConf key

* Wed Oct 17 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-2
- Install all necessary GConf schemas
 
* Mon Oct 15 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-1
- Update to 2.20.1 (translation update)

* Thu Oct 11 2007 Ray Strode <rstrode@redhat.com> - 2.20.0-4
- Add Requires: fedora-gnome-theme >= 8.0.0

* Wed Oct 10 2007 Ray Strode <rstrode@redhat.com> - 2.20.0-3
- Add Requires: fedora-gnome-theme

* Tue Sep 18 2007 Ray Strode <rstrode@redhat.com> - 2.20.0-2
- the location of the default background setting changed, 
  update correct schema input file

* Mon Sep 17 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.0-1
- Update to 2.20.0

* Tue Aug 28 2007 Máirín Duffy <duffy@redhat.com> - 2.19.1-9
- Change default background to Infinity

* Mon Aug 27 2007 Ray Strode <rstrode@redhat.com> - 2.19.1-8
- create .gnome2 directory by default for new users (bug 254237)

* Fri Aug 24 2007 Christopher Aillon <caillon@redhat.com> - 2.19.1-7
- The -devel package also needs to Require: popt-devel

* Thu Aug 23 2007 Matthew Barnes <mbarnes@redhat.com> - 2.19.1-6
- Build requires popt-devel.

* Thu Aug 23 2007 Adam Jackson <ajax@redhat.com> - 2.19.1-5
- Rebuild for build ID

* Tue Aug 14 2007 Lennart Poettering <lpoetter@redhat.com> - 2.19.1-4
- Enable ESD by default for PulseAudio transition (#251954)

* Sat Aug 11 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.1-3
- Switch the default GTK+ theme to Nodoka

* Tue Aug  7 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.1-2
- Update the license field

* Mon Jul 30 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.1-1
- Update to 2.19.1

* Sat Jul  7 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.0-2
- Fix directory ownership issues

* Mon Jun 18 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.0-1
- Update to 2.19.0
- Drop upstreamed patch

* Thu Apr 19 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.0-4
- Change the default icon theme to Fedora

* Thu Apr  5 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.0-3
- Fix patches to make changes in gconf default settings
  take effect again

* Thu Apr  5 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.0-3
- Fix patches to make changes in gconf default settings
  take effect again

* Sat Mar 31 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.0-2
- Set program name correctly

* Tue Mar 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.0-1
- Update to 2.18.0

* Tue Feb 27 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.92-1
- Update to 2.17.92

* Tue Feb 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.91-1
- Update to 2.17.91

* Mon Jan 22 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.90-1
- Update to 2.17.90

* Wed Jan 10 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.3-1
- Update to 2.17.3

* Wed Jan 10 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.2-1
- Update to 2.17.2

* Tue Dec  5 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.1-1
- Update to 2.17.1

* Wed Nov  8 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.0-1
- Update to 2.17.0

* Fri Oct 27 2006 David Zeuthen <davidz@redhat.com> - 2.16.0-7
- Make Echo the default icon theme and require echo-icon-theme for now

* Wed Oct 18 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-6
- Fix scripts according to packaging guidelines

* Tue Oct 17 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-5
- Tighten up Requires (#203813)

* Sun Oct 01 2006 Jesse Keating <jkeating@redhat.com> - 2.16.0-4
- rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Tue Sep 26 2006 Matthew Barnes <mbarnes@redhat.com> - 2.16.0-3.fc6
- Make the API documentation easier to navigate.

* Mon Sep 11 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-2
- Update the patch for the default background (#205867)
- Add missing BuildRequires

* Mon Sep  4 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-1.fc6
- Uodate to 2.16.0
- Require pkgconfig in the -devel package

* Sat Aug 12 2006 Matthias Clasen <mclasen@redhat.com> 2.15.2-1.fc6
- Update to 2.15.2
- Don't ship static libraries

* Thu Jul 27 2006 Mike A. Harris <mharris@redhat.com> 2.15.1-3.fc6
- Update utempter dependency and rebuild to ensure new libutempter is used.
- Change BuildRoot to comply with Fedora packaging guidelines.
- Change legacy style PreReqs to Requires({pre,post,postun}) style and update

* Mon Jul 24 2006 Ray Strode <rstrode@redhat.com> - 2.15.1-2
- turn off im menu by default (bug 199967)

* Wed Jul 12 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.1-1
- Update to 2.15.1

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.14.1-4.1
- rebuild

* Sat Jun 10 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.1-4
- Add missing BuildRequires

* Tue Jun  6 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.1-3
- Rebuild

* Tue Apr 11 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.1-2
- Update to 2.14.1

* Mon Mar 13 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.0-1
- Update to 2.14.0

* Mon Feb 27 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.90-1
- Update to 2.13.90
- Drop obsolete patch

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.13.7-5.1
- bump again for double-long bug on ppc(64)

* Thu Feb  9 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.7-5
- Rebuild

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.13.7-4.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Sun Feb  5 2006 Matthias Clasen <mclasen@redhat.com> 2.13.7-4
- Update requires

* Thu Jan 19 2006 Ray Strode <rstrode@redhat.com> - 2.13.7-3
- s/sed -ie/sed -i -e/

* Thu Jan 19 2006 Ray Strode <rstrode@redhat.com> - 2.13.7-2
- fix multilib bonobo shlib problem

* Mon Jan 16 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.7-1
- Update to 2.13.7

* Wed Dec 14 2005 Matthias Clasen <mclasen@redhat.com> - 2.13.4-1
- Update to 2.13.4

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Wed Nov 30 2005 Matthias Clasen <mclasen@redhat.com> - 2.13.2-1
- Update to 2.13.2
- Drop upstreamed patches

* Mon Oct 24 2005 Matthias Clasen <mclasen@redhat.com> - 2.12.0.1-2
- Add schema for some new keys

* Thu Sep 29 2005 Matthias Clasen <mclasen@redhat.com> - 2.12.0.1-1
- Update to 2.12.0.1

* Thu Sep 22 2005 Jeremy Katz <katzj@redhat.com> - 2.12.0-2
- fix broken translation in schema

* Thu Sep 8 2005 Matthias Clasen <mclasen@redhat.com> - 2.12.0-1
- Update to 2.12.0

* Tue Aug 9 2005 Ray Strode <rstrode@redhat.com> - 2.11.2-1
- Newer upstream version

* Mon Jul 11 2005 Matthias Clasen <mclasen@redhat.com> - 2.11.1-1
- Newer upstream version

* Wed Apr 13 2005 John (J5) Palmieri <johnp@redhat.com> - 2.10.0-3
- Change the default icon theme back to Clearlooks as the Clearlooks
  icon theme will now inherit from Bluecurve

* Wed Apr 13 2005 John (J5) Palmieri <johnp@redhat.com> - 2.10.0-2
- Reenable the default icon theme patch to be bluecurve 

* Fri Apr  8 2005 Ray Strode <rstrode@redhat.com> - 2.10.0-1
- Update to 2.10.0

* Fri Mar 18 2005 Matthias Clasen <mclasen@redhat.com> - 2.9.1-3
- Fix the build on s390

* Thu Mar 17 2005 Matthias Clasen <mclasen@redhat.com> - 2.9.1-2
- Switch to Clearlooks as default gtk theme, gnome as default
  icon theme

* Thu Jan 27 2005 Matthias Clasen <mclasen@redhat.com> - 2.9.1-1
- Update to 2.9.1

* Thu Nov 4 2004 Dan Walsh <dwalsh@redhat.com> - 2.8.0-3
- Stat gnome_user_private_dir before doing chmod, firefox gets
- blown up because of this in strict selinux policy.

* Mon Oct 18 2004  <jrb@redhat.com> - 2.8.0-2
- change default browser to firefox

* Wed Sep 22 2004 Alexander Larsson <alexl@redhat.com> - 2.8.0-1
- update to 2.8.0

* Tue Aug 31 2004 Alex Larsson <alexl@redhat.com> 2.7.92-1
- update to 2.7.92

* Wed Aug 11 2004 Alexander Larsson <alexl@redhat.com> - 2.7.2-2
- Update default fixes to patch schemas.in files

* Wed Aug  4 2004 Mark McLoughlin <markmc@redhat.com> 2.7.2-1
- Update to 2.7.2
- Remove sound properties patches and desktop_gnome_accessibility_startup
  schemas - all seem to be upstream now

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Sat May 15 2004 Colin Walters <walters@redhat.com> 2.6.0-3
- Apply another patch which fixes GNOME sound events, which
  due to what appears to be a glib bug, were broken by my
  previous patch.

* Thu Apr 13 2004 Colin Walters <walters@redhat.com> 2.6.0-2
- Apply my patch to fix --disable-sound property from HEAD

* Thu Apr  1 2004 Alex Larsson <alexl@redhat.com> 2.6.0-1
- update to 2.6.0

* Thu Mar 11 2004 Alex Larsson <alexl@redhat.com> 2.5.91-2
- enable gtk-doc

* Wed Mar 10 2004 Mark McLoughlin <markmc@redhat.com> 2.5.91-1
- Update to 2.5.91

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Feb 24 2004 Alexander Larsson <alexl@redhat.com> 2.5.90-1
- update to 2.5.90

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Jan 20 2004 Alexander Larsson <alexl@redhat.com> 2.5.3-1
- 2.5.3

* Tue Sep  2 2003 Alexander Larsson <alexl@redhat.com> 2.4.0-1
- 2.4.0

* Wed Aug 27 2003 Alexander Larsson <alexl@redhat.com> 2.3.7-2
- Default http handler is htmlview

* Wed Aug 27 2003 Alexander Larsson <alexl@redhat.com> 2.3.7-1
- update to 2.3.7

* Tue Aug 12 2003 Alexander Larsson <alexl@redhat.com> 2.3.6-1
- Gnome 2.3 update

* Mon Aug  4 2003 Jeremy Katz <katzj@redhat.com> 2.2.2-6
- rebuild

* Tue Jul 22 2003 Nalin Dahyabhai <nalin@redhat.com> 2.2.2-5
- rebuild

* Tue Jul 22 2003 Jonathan Blandford <jrb@redhat.com>
- install at-startup schemas

* Tue Jul 15 2003 Havoc Pennington <hp@redhat.com> 2.2.2-3
- --disable-gtk-doc

* Mon Jul 14 2003 Havoc Pennington <hp@redhat.com>
- automated rebuild

* Wed Jul  9 2003 Alexander Larsson <alexl@redhat.com> 2.2.2-2
- Fix default theme patch

* Mon Jul  7 2003 Havoc Pennington <hp@redhat.com> 2.2.1-1
- 2.2.2

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Feb 24 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Feb 24 2003 Owen Taylor <otaylor@redhat.com>
- Add back monospace schema, isn't upstream

* Mon Feb 10 2003 Bill Nottingham <notting@redhat.com> 2.2.0.1-6
- clean up filelist (#68226)
- make LIBTOOL=/usr/bin/libtool

* Fri Feb  7 2003 Jonathan Blandford <jrb@redhat.com> 2.2.0.1-3
- fix schema default.

* Thu Feb  6 2003 Jonathan Blandford <jrb@redhat.com> 2.2.0.1-2
- change schema default; add new schema

* Thu Jan 23 2003 Alexander Larsson <alexl@redhat.com>
- update to 2.2.0.1

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Wed Jan 22 2003 Jonathan Blandford <jrb@redhat.com>
- new version

* Sun Jan 12 2003 Havoc Pennington <hp@redhat.com>
- update requirements and rebuild

* Thu Jan  9 2003 Alexander Larsson <alexl@redhat.com>
- Update to 2.1.90
- Add a patch to change the default icon theme to Bluecurve

* Tue Dec  3 2002 Havoc Pennington <hp@redhat.com>
- add explicit gconftool-2 prereq in addition to gconf prereq

* Wed Nov 13 2002 Havoc Pennington <hp@redhat.com>
- only require bonobo-activation 1.0.0

* Sun Nov 10 2002 Havoc Pennington <hp@redhat.com>
- 2.1.1
- remove monospace font schema, should be upstream

* Wed Aug 28 2002 Matt Wilson <msw@redhat.com> 2.0.2-5
- added libgnome-2.0.2-program-init.patch to enable correct module
  initialization when gnome_program_init is called after
  gnome_program_module_register

* Wed Aug 21 2002 Elliot Lee <sopwith@redhat.com> 2.0.2-4
- Fix #64908 with patch3 (scoreloc)
- Add smp_mflags

* Mon Aug 12 2002 Havoc Pennington <hp@redhat.com>
- s/Wonderland/Bluecurve/

* Thu Aug  8 2002 Havoc Pennington <hp@redhat.com>
- change default background to new spec from garrett

* Wed Aug  7 2002 Havoc Pennington <hp@redhat.com>
- 2.0.2

* Wed Jul 24 2002 Owen Taylor <otaylor@redhat.com>
- Add schema for monospaced font

* Wed Jun 26 2002 Owen Taylor <otaylor@redhat.com>
- Fix find_lang

* Sun Jun 16 2002 Havoc Pennington <hp@redhat.com>
- 2.0.1
- put bonobo monikers in file list (don't know what they 
  do, but assuming they do something)
- include /etc/sound in file list

* Mon Jun 10 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Mon Jun 10 2002 Havoc Pennington <hp@redhat.com>
- change default gtk theme to Wonderland

* Fri Jun 07 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Wed Jun  5 2002 Havoc Pennington <hp@redhat.com>
- 1.117.2
- add ldconfig calls

* Mon May 20 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Mon May 20 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment
- add bonobo-activation build requires

* Mon May 20 2002 Havoc Pennington <hp@redhat.com>
- 1.117.1

* Fri May  3 2002 Havoc Pennington <hp@redhat.com>
- 1.116.0

* Thu Apr  4 2002 Jeremy Katz <katzj@redhat.com>
- 1.114.0

* Thu Feb 14 2002 Havoc Pennington <hp@redhat.com>
- 1.111.0

* Wed Jan 30 2002 Owen Taylor <otaylor@redhat.com>
- Version 1.110.0

* Tue Jan 22 2002 Havoc Pennington <hp@redhat.com>
- remove bogus dependency on libdb1

* Thu Jan  3 2002 Havoc Pennington <hp@redhat.com>
- fix the post script

* Thu Jan  3 2002 Havoc Pennington <hp@redhat.com>
- 1.108.0.90 cvs snap

* Tue Nov 27 2001 Havoc Pennington <hp@redhat.com>
- fix .schemas in post

* Tue Nov 27 2001 Havoc Pennington <hp@redhat.com>
- update CVS snap to 1.107.0.90, glib 1.3.11
- add libxslt dep
- require specific versions of dependent libs
- add bunch of missing stuff to file list
- install gconf schemas in post

* Sun Oct 28 2001 Havoc Pennington <hp@redhat.com>
- well, you only get the new CVS snap if you actually change the version in the spec file, doh

* Sun Oct 28 2001 Havoc Pennington <hp@redhat.com>
- new cvs snap, rebuild for glib 1.3.10, remove gtk requires

* Fri Sep 21 2001 Havoc Pennington <hp@redhat.com>
- new CVS snap, rebuild in 7.2-gnome

* Tue Sep 18 2001 Havoc Pennington <hp@redhat.com>
- Initial build.
- remove gtk2 dependency, doh
