%if 0%{?fedora} || 0%{?rhel} >= 7
%global _docdir_fmt %{name}
%endif

Name: mbedtls3
Version: 3.6.0
Release: 1%{?dist}
Summary: Light-weight cryptographic and SSL/TLS library
License: Apache-2.0
URL: https://www.trustedfirmware.org/projects/mbed-tls
Source0: https://github.com/Mbed-TLS/mbedtls/releases/download/v3.6.0/mbedtls-3.6.0.tar.bz2
Patch0: 0001-mbedtls_xor-simplify-and-fix-build-error.diff
BuildRequires: make
BuildRequires: gcc-c++
BuildRequires: cmake
BuildRequires: doxygen
BuildRequires: graphviz
BuildRequires: perl-interpreter
BuildRequires: python3

%description
Mbed TLS is a light-weight open source cryptographic and SSL/TLS
library written in C. Mbed TLS makes it easy for developers to include
cryptographic and SSL/TLS capabilities in their (embedded)
applications with as little hassle as possible.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package        doc
Summary:        Documentation files for %{name}
BuildArch:      noarch

%description    doc
The %{name}-doc package contains documentation.

%prep
%autosetup -n mbedtls-3.6.0 -p1

sed -i 's|//\(#define MBEDTLS_THREADING_C\)|\1|' include/mbedtls/mbedtls_config.h
sed -i 's|//\(#define MBEDTLS_THREADING_PTHREAD\)|\1|' include/mbedtls/mbedtls_config.h

%build
export CFLAGS="%{optflags} -Wno-stringop-overflow -Wno-maybe-uninitialized"
export CXXLAGS="%{optflags} -Wno-stringop-overflow -Wno-maybe-uninitialized"

%cmake \
	-DCMAKE_BUILD_TYPE=Release \
	-DLINK_WITH_PTHREAD=ON \
	-DINSTALL_MBEDTLS_HEADERS=ON \
	-DENABLE_PROGRAMS=OFF \
	-DUSE_SHARED_MBEDTLS_LIBRARY=ON \
	-DUSE_STATIC_MBEDTLS_LIBRARY=OFF \
	-DGEN_FILES=OFF \
	-DENABLE_TESTING=Off

%cmake_build
make apidoc

%install
%cmake_install

# Library files aren't supposed to be executable, but RPM requires this historically
# for automatic per-file level automatic dependency generation at ELF binaries; see:
# - https://github.com/ARMmbed/mbedtls/commit/280165c9b39091c7c7ffe031430c7cf93ebc4dec
# - https://lists.fedoraproject.org/archives/list/devel@lists.fedoraproject.org/thread/PDD6RNQMII472HXM4XAUUWWZKKBGHPTO/
chmod 755 %{buildroot}%{_libdir}/*.so.*

# We want to prefix all the files under their own include and link directories so mbedtls and mbedtls3 can be installed
# side by side
mkdir -p %{buildroot}/%{_includedir}/mbedtls3
mv %{buildroot}/%{_includedir}/mbedtls %{buildroot}/%{_includedir}/mbedtls3

# %check
# %ctest --output-on-failure --force-new-ctest-process --parallel 1

%ldconfig_scriptlets

%files
%doc ChangeLog
%{!?_licensedir:%global license %%doc}
%license LICENSE
%{_libdir}/*.so.*

%files devel
%{_includedir}/mbedtls3/
%{_includedir}/psa/
%{_includedir}/everest/
%{_libdir}/pkgconfig/
%{_libdir}/cmake/
%{_libdir}/*.so

%files doc
%doc apidoc/*

%changelog
* Tue Apr 02 2024 Bill Roberts <bill.roberts@arm.com> - 3.6.0
- Update to 3.6.0