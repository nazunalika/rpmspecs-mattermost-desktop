# globals
%global debug_package %{nil}
%define __requires_exclude ^libffmpeg.so
%define releasedir linux-unpacked

Name:		mattermost-desktop
Version:	5.4.0
Release:	1%{?dist}
Summary:	Mattermost Desktop application for Linux
# aarch64 not supported
ExclusiveArch:	x86_64

License:	ASL 2.0
URL:		https://about.mattermost.com
Source0:	https://github.com/mattermost/desktop/archive/v%{version}.tar.gz

BuildRequires:	npm
BuildRequires:	nodejs
BuildRequires:	gcc-c++
BuildRequires:	libGL.so.1
BuildRequires:	libXi
BuildRequires:	git
Requires:	gtk2
Requires:	libXtst
Requires:	libXScrnSaver
Requires:	nss
Requires:	nspr
Requires:	alsa-lib

%description
Mattermost is an open-source, self-hostable online chat service with file
sharing, search, and integrations. It is designed as an internal chat for
organizations and companies. Mattermost was built and designed to be an
open-source alternative to Slack and Microsoft Teams.

This package contains the desktop application to connect to Mattermost
servers.

%prep
%autosetup -n desktop-%{version}

# To speed up build time, we need to remove building of debian packages and ia32 binaries
sed -i -e '/^[[:space:]]*"target": \[/!b' -e '$!N;s/\n[[:space:]]*"deb",//' electron-builder.json
sed -i -e '/^[[:space:]]*"target": \[/!b' -e '$!N;s/\n[[:space:]]*"tar.gz",//' electron-builder.json
sed -i -e '/^[[:space:]]*"target": \[/!b' -e '$!N;s/\n[[:space:]]*"appimage",//' electron-builder.json
sed -i -e '/^[[:space:]]*"target": \[/!b' -e '$!N;s/\n[[:space:]]*"rpm"//' electron-builder.json
sed -i 's/--ia32//g' package.json

# There's some things that we need to turn off or fixed
sed -i -e "s/git rev-parse --short HEAD/echo %{version}/" webpack.config.base.js
sed -i -e 's#resources/linux#src/assets/linux#' electron-builder.json

%build
npm install
npm run build
npm run package:linux

%install
rm -rf $RPM_BUILD_ROOT
%{__mkdir} -p ${RPM_BUILD_ROOT}/%{_bindir}
%{__mkdir} -p ${RPM_BUILD_ROOT}/%{_libdir}/%{name}
%{__mkdir} -p ${RPM_BUILD_ROOT}/%{_datadir}/{applications,pixmaps}

cp src/assets/linux/icon.svg ${RPM_BUILD_ROOT}/%{_datadir}/pixmaps/%{name}.svg

mv release/%{releasedir} release/%{name}
cd release/%{name}
rm create_desktop_file.sh

cat > %{name}.desktop <<EOF
[Desktop Entry]
Name=Mattermost
Comment=Mattermost Desktop application for Linux
Exec=/usr/bin/%{name}
Terminal=false
Type=Application
Icon=%{name}
Categories=Network;Application;InstantMessaging;
MimeType=x-scheme-handler/mattermost;
EOF

cp %{name}.desktop ${RPM_BUILD_ROOT}%{_datadir}/applications/%{name}.desktop
cp -r * ${RPM_BUILD_ROOT}/%{_libdir}/%{name}
rm ${RPM_BUILD_ROOT}/%{_libdir}/%{name}/%{name}.desktop
ln -s %{_libdir}/%{name}/%{name} $RPM_BUILD_ROOT/%{_bindir}/%{name}

%files
%doc README.md
%license LICENSE.txt NOTICE.txt
%{_bindir}/*
%{_libdir}/*
%{_datadir}/applications/%{name}.desktop
%{_datadir}/pixmaps/%{name}.svg

%changelog
* Sat Jul 15 2023 Louis Abel <tucklesepk@gmail.com> - 5.4.0-1
- Update to 5.4.0

* Tue Aug 17 2021 Louis Abel <tucklesepk@gmail.com> - 4.7.1-1
- Initial release
