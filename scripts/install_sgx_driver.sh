#!/usr/bin/env bash
SGX_SDK_VERSION="2.15.100.3"

set -eo pipefail

error() {
    echo "Error: $1" >&2
    exit 1
}

if [[ "$EUID" -ne 0 ]]; then
    error "Please run as root."
fi

RELEASE_INFO="$(cat /etc/issue)"
if [[ "$RELEASE_INFO" = *"Ubuntu 18.04"* ]]; then
    OS="Ubuntu-18.04"
elif [[ "$RELEASE_INFO" = *"Ubuntu 20.04"* ]]; then
    OS="Ubuntu-20.04"
else
    error "Ubuntu 18.04 or Ubuntu 20.04 is required."
fi

apt-get update -y
apt-get upgrade -y
apt-get install -y build-essential ocaml ocamlbuild automake autoconf libtool libssl-dev pkg-config
apt-get install -y llvm-dev libclang-dev clang # required by bindgen
apt-get install -y curl gnupg

case "$OS" in
    "Ubuntu-18.04")
        echo "deb [arch=amd64] https://download.01.org/intel-sgx/sgx_repo/ubuntu bionic main" > /etc/apt/sources.list.d/intel-sgx.list
        SGX_SDK_URL="https://download.01.org/intel-sgx/latest/linux-latest/distro/ubuntu18.04-server/sgx_linux_x64_sdk_$SGX_SDK_VERSION.bin"
        ;;
    "Ubuntu-20.04")
        echo "deb [arch=amd64] https://download.01.org/intel-sgx/sgx_repo/ubuntu focal main" > /etc/apt/sources.list.d/intel-sgx.list
        SGX_SDK_URL="https://download.01.org/intel-sgx/latest/linux-latest/distro/ubuntu20.04-server/sgx_linux_x64_sdk_$SGX_SDK_VERSION.bin"
        ;;
esac
curl -fsSL https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key | apt-key add -
curl -sL https://deb.nodesource.com/setup_16.x | bash -

apt-get update -y
apt-get install -y libsgx-uae-service libsgx-urts sgx-aesm-service
apt-get install -y nodejs

echo "install $SGX_SDK_URL..."
rm -f /tmp/sgx_linux_x64_sdk.bin
curl -fsSL "$SGX_SDK_URL" -o /tmp/sgx_linux_x64_sdk.bin
chmod +x /tmp/sgx_linux_x64_sdk.bin
mkdir -p /opt/intel
cd /opt/intel
echo 'yes'| /tmp/sgx_linux_x64_sdk.bin
rm -f /tmp/sgx_linux_x64_sdk.bin

DCAP_SGX_DRIVER_VERSION="1.41"
OOT_SGX_DRIVER_VERSION="2.11.0_2d2b795"

set -eo pipefail

error() {
    echo "Error: $1" >&2
    exit 1
}

if [[ "$EUID" -ne 0 ]]; then
    error "Please run as root."
fi

RELEASE_INFO="$(cat /etc/issue)"
if [[ "$RELEASE_INFO" = *"Ubuntu 18.04"* ]]; then
    OS="Ubuntu-18.04"
    DCAP_SGX_DERIVER_URL="https://download.01.org/intel-sgx/latest/linux-latest/distro/ubuntu18.04-server/sgx_linux_x64_driver_$DCAP_SGX_DRIVER_VERSION.bin"
    OOT_SGX_DERIVER_URL="https://download.01.org/intel-sgx/latest/linux-latest/distro/ubuntu18.04-server/sgx_linux_x64_driver_$OOT_SGX_DRIVER_VERSION.bin"
elif [[ "$RELEASE_INFO" = *"Ubuntu 20.04"* ]]; then
    OS="Ubuntu-20.04"
    DCAP_SGX_DERIVER_URL="https://download.01.org/intel-sgx/latest/linux-latest/distro/ubuntu20.04-server/sgx_linux_x64_driver_$DCAP_SGX_DRIVER_VERSION.bin"
    OOT_SGX_DERIVER_URL="https://download.01.org/intel-sgx/latest/linux-latest/distro/ubuntu20.04-server/sgx_linux_x64_driver_$OOT_SGX_DRIVER_VERSION.bin"
else
    error "Ubuntu 18.04 or Ubuntu 20.04 is required."
fi

apt-get update -y
apt-get install -y dkms

if [[ -x /opt/intel/sgx-aesm-service/cleanup.sh ]]; then
    /opt/intel/sgx-aesm-service/cleanup.sh
fi

# Comment the following lines for DCAP driver installation if your kernel version
# is above 5.11 where the in-kernel driver is under /dev/sgx*
#
# echo "install $DCAP_SGX_DERIVER_URL..."
# rm -f /tmp/sgx_linux_x64_driver.bin
# curl -fsSL "$DCAP_SGX_DERIVER_URL" -o /tmp/sgx_linux_x64_driver.bin
# chmod +x /tmp/sgx_linux_x64_driver.bin
# mkdir -p /opt/intel
# /tmp/sgx_linux_x64_driver.bin
# rm -f /tmp/sgx_linux_x64_driver.bin

echo "install $OOT_SGX_DERIVER_URL..."
rm -f /tmp/sgx_linux_x64_driver.bin
curl -fsSL "$OOT_SGX_DERIVER_URL" -o /tmp/sgx_linux_x64_driver.bin
chmod +x /tmp/sgx_linux_x64_driver.bin
mkdir -p /opt/intel
/tmp/sgx_linux_x64_driver.bin
rm -f /tmp/sgx_linux_x64_driver.bin

if [[ -x /opt/intel/sgx-aesm-service/startup.sh ]]; then
    /opt/intel/sgx-aesm-service/startup.sh
fi
