# trim changelog included in binary rpms
%global _changelog_trimtime %(date +%s -d "1 year ago")

## tests busted due to %%{_target_platform} not being used as default anymore -- rex
#global tests 1

Name:    kate
Summary: Advanced Text Editor
Version: 24.12.2
Release: 2%{?dist}

# kwrite LGPLv2+
# kate: app LGPLv2, plugins, LGPLv2 and LGPLv2+ and GPLv2+
# ktexteditor: LGPLv2
License: LGPL-2.0-only AND LGPL-2.0-or-later AND GPL-2.0-or-later
URL:     https://apps.kde.org/kate/
Source0: https://github.com/KDE/%{name}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Patch0:  0001-Defuse-root-block.patch

## upstream patches

BuildRequires: desktop-file-utils
BuildRequires: gettext
BuildRequires: extra-cmake-modules
BuildRequires: kf6-rpm-macros
BuildRequires: libappstream-glib

# core dependencies
BuildRequires: cmake(Qt6Widgets)
BuildRequires: cmake(KF6I18n)
BuildRequires: cmake(KF6CoreAddons)
BuildRequires: cmake(KF6GuiAddons)
BuildRequires: cmake(KF6Crash)
BuildRequires: cmake(KF6IconThemes)
BuildRequires: cmake(KF6TextEditor)
BuildRequires: cmake(KF6DocTools)

# apps dependencies
BuildRequires: cmake(Qt6Test)
BuildRequires: cmake(KF6DBusAddons)
BuildRequires: cmake(KF6UserFeedback)
BuildRequires: cmake(KF6TextWidgets)
BuildRequires: cmake(KF6WindowSystem)
BuildRequires: qt6-qtbase-private-devel

# addons dependencies
BuildRequires: cmake(Qt6Concurrent)
BuildRequires: cmake(Qt6Sql)
BuildRequires: cmake(Qt6Keychain)
BuildRequires: cmake(KF6Config)
BuildRequires: cmake(KF6NewStuff)
BuildRequires: cmake(KF6Wallet)
BuildRequires: cmake(KF6KIO)

%if 0%{?tests}
BuildRequires: make
BuildRequires: xorg-x11-server-Xvfb
%endif

Requires: %{name}-libs = %{version}-%{release}
# not sure if we want -plugins by default, let's play it safe'ish
# and make it optional
Recommends: %{name}-plugins%{?_isa} = %{version}-%{release}

%description
%{summary}.

%package libs
Summary: Private runtime libraries for %{name}
%description libs
%{summary}.

%package plugins
Summary: Kate plugins
License: LGPL-2.0-only
Requires: %{name} = %{version}-%{release}
# Kate integrated terminal plugin doesnt work without Konsole
Recommends: konsole-part >= 24
%description plugins
%{summary}.

%package -n kwrite
Summary: Text Editor
License: LGPL-2.0-or-later
Requires: %{name}-libs = %{version}-%{release}
%description -n kwrite
%{summary}.


%prep
%autosetup -n kate-%{version} -p1


%build
%cmake_kf6 \
  -Wno-dev \
  -DBUILD_TESTING:BOOL=%{?tests:ON}%{!?tests:OFF}

%cmake_build


%install
%cmake_install


%find_lang all --all-name --with-html --with-man

grep plugin all.lang > plugins.lang
grep kwrite all.lang > kwrite.lang
cat all.lang plugins.lang kwrite.lang | sort | uniq -u > kate.lang


%check
appstream-util validate-relax --nonet %{buildroot}%{_kf6_metainfodir}/org.kde.kate.appdata.xml
desktop-file-validate %{buildroot}%{_kf6_datadir}/applications/org.kde.kate.desktop
desktop-file-validate %{buildroot}%{_kf6_datadir}/applications/org.kde.kwrite.desktop
%if 0%{?tests}
export CTEST_OUTPUT_ON_FAILURE=1
xvfb-run -a \
make test ARGS="--output-on-failure --timeout 20" -C %{_target_platform} ||:
%endif


%files -f kate.lang
%doc README.md
%license LICENSES/*
%{_kf6_bindir}/kate
%{_kf6_datadir}/applications/org.kde.kate.desktop
%{_kf6_datadir}/icons/hicolor/*/apps/kate.*
%{_kf6_metainfodir}/org.kde.kate.appdata.xml
%{_kf6_plugindir}/ktexteditor/cmaketoolsplugin.so
%{_kf6_plugindir}/ktexteditor/eslintplugin.so
%{_kf6_plugindir}/ktexteditor/formatplugin.so
%{_kf6_plugindir}/ktexteditor/rbqlplugin.so
%{_mandir}/man1/kate.1*


%files libs
%{_kf6_libdir}/libkateprivate.so.%{version}

%files plugins -f plugins.lang
%{_kf6_datadir}/kateproject/
%{_kf6_datadir}/katexmltools/
%{_kf6_plugindir}/ktexteditor/*.so

%files -n kwrite -f kwrite.lang
%{_kf6_bindir}/kwrite
%{_kf6_datadir}/applications/org.kde.kwrite.desktop
%{_kf6_datadir}/icons/hicolor/*/apps/kwrite.*
%{_kf6_metainfodir}/org.kde.kwrite.appdata.xml

