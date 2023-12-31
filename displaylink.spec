%undefine _debugsource_packages

Name: displaylink
Version: 5.8
Release: 2
# https://www.synaptics.com/products/displaylink-graphics/downloads/ubuntu
Source0: https://www.synaptics.com/sites/default/files/exe_files/2023-08/DisplayLink%20USB%20Graphics%20Software%20for%20Ubuntu%{version}-EXE.zip
Source1: https://raw.githubusercontent.com/displaylink-rpm/displaylink-rpm/master/20-displaylink.conf
Source2: https://raw.githubusercontent.com/displaylink-rpm/displaylink-rpm/master/displaylink.logrotate
Source3: https://raw.githubusercontent.com/displaylink-rpm/displaylink-rpm/master/95-displaylink.preset
Summary: DisplayLink USB Graphics driver
URL: https://github.com/displaylink/displaylink
License: Binary-only, distributable
Group: Hardware
ExclusiveArch: %{x86_64} %{aarch64} %{ix86} %{arm}
BuildRequires: systemd-rpm-macros
BuildRequires: sed
# dlopen()ed -- therefore no autogenerated dependency
Requires: %mklibname evdi

%description
Driver for HDMI/VGA adapters built upon the DisplayLink DL-6xxx,
DL-5xxx, DL-41xx and DL-3xxx series of chipsets. This includes
numerous docking stations, USB monitors, and USB adapters.

WARNING: This driver is distributed as a binary only. Neither you
nor the OpenMandriva team can review what this binary, run as root,
actually does.
It may work, but it may also wipe your harddisk clean or send all
your data to someone who shouldn't have it.
Please complain to DisplayLink.

%prep
%autosetup -p1 -c
chmod +x *.run
./displaylink-driver-*.run --noexec --keep

%build

%install
mkdir -p %{buildroot}%{_libexecdir}/%{name}

# DisplayLinkManager binary...
%ifarch %{x86_64}
cp -a displaylink-driver-*/x64-*/DisplayLinkManager %{buildroot}%{_libexecdir}/%{name}
%else
%ifarch %{ix86}
cp -a displaylink-driver-*/x86-*/DisplayLinkManager %{buildroot}%{_libexecdir}/%{name}
%else
%ifarch %{aarch64}
cp -a displaylink-driver-*/aarch64-*/DisplayLinkManager %{buildroot}%{_libexecdir}/%{name}
%else
%ifarch %{arm}
cp -a displaylink-driver-*/arm-*/DisplayLinkManager %{buildroot}%{_libexecdir}/%{name}
%else
echo "Unsupported architecture"
exit 1
%endif
%endif
%endif
%endif

cd displaylink-driver-*[0-9]
# Firmware
cp *.spkg %{buildroot}%{_libexecdir}/%{name}/

# Systemd services and udev integration...
mkdir -p %{buildroot}%{_sysconfdir}/udev/rules.d %{buildroot}%{_libexecdir}/%{name} %{buildroot}%{_unitdir} %{buildroot}%{_sysconfdir}/pm/sleep.d
# Adjust to FHS paths instead of those created by the .run file
sed -i -e 's,/opt/displaylink,%{_libexecdir}/displaylink,g' *.sh
# Make sure we install to the buildroot
sed -i -e 's, /lib/systemd,%{buildroot}%{_prefix}/lib/systemd,g' -e 's, /etc/pm, %{buildroot}%{_sysconfdir}/pm,g' service-installer.sh
chmod +x *.sh
./udev-installer.sh systemd %{buildroot}%{_udevrulesdir}/99-displaylink.rules %{buildroot}%{_libexecdir}/%{name}/udev.sh
. ./service-installer.sh
create_dl_service systemd %{buildroot}%{_libexecdir}/%{name} %{buildroot}%{_prefix}
# Fix script pointing at buildroot
rm %{buildroot}%{_sysconfdir}/pm/sleep.d/10_displaylink
ln -s ../../..%{_libexecdir}/%{name}/suspend.sh %{buildroot}%{_sysconfdir}/pm/sleep.d/10_displaylink
# Module config
mkdir -p %{buildroot}%{_sysconfdir}/modprobe.d
echo 'options evdi initial_device_count=4' >%{buildroot}%{_sysconfdir}/modprobe.d/evdi.conf
# Xorg config
mkdir -p %{buildroot}%{_datadir}/X11/xorg.conf.d
cp %{S:1} %{buildroot}%{_datadir}/X11/xorg.conf.d/
# logs
mkdir -p %{buildroot}%{_localstatedir}/log/displaylink %{buildroot}%{_sysconfdir}/logrotate.d
cp %{S:2} %{buildroot}%{_sysconfdir}/logrotate.d/
# launch if installed
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system-preset
cp %{S:3} %{buildroot}%{_prefix}/lib/systemd/system-preset/

%post
%systemd_post displaylink-driver.service

%preun
%systemd_preun displaylink-driver.service

%postun
%systemd_postun_with_restart displaylink-driver.service

%files
%{_libexecdir}/%{name}
%{_sysconfdir}/pm/sleep.d/10_displaylink
%{_udevrulesdir}/99-displaylink.rules
%{_unitdir}/displaylink-driver.service
%{_sysconfdir}/modprobe.d/evdi.conf
%{_datadir}/X11/xorg.conf.d/20-displaylink.conf
%{_prefix}/lib/systemd/system-preset/*
%config(noreplace) %{_sysconfdir}/logrotate.d/displaylink.logrotate
%dir %{_localstatedir}/log/displaylink
