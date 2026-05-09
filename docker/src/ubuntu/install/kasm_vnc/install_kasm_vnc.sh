#!/usr/bin/env bash
set -e

install_libjpeg_turbo() {
    local libjpeg_deb=libjpeg-turbo.deb
    wget "https://kasmweb-build-artifacts.s3.amazonaws.com/kasmvnc/${COMMIT_ID}/output/${UBUNTU_CODENAME}/libjpeg-turbo_2.1.4_amd64.deb" -O "$libjpeg_deb"
    apt-get install -y "./$libjpeg_deb"
    rm "$libjpeg_deb"
}

patch_clipboard_permission_check() {
    local browser_js="$KASM_VNC_PATH/www/core/util/browser.js"
    local bundle_js="$KASM_VNC_PATH/www/dist/main.bundle.js"

    # KasmVNC 0.9.3.2 treats navigator.clipboard.read as enough support for
    # binary clipboard, then queries "clipboard-read" through the Permissions
    # API. Firefox exposes enough Clipboard API surface to pass that check, but
    # rejects "clipboard-read" as a PermissionName and aborts the web UI.
    sed -i \
        's/if (isSafari()) { return false; }/if (isSafari() || isFirefox()) { return false; }/' \
        "$browser_js"
    sed -i \
        's/if (isSafari()) {/if (isSafari() || browser_isFirefox()) {/' \
        "$bundle_js"

    grep -q 'isSafari() || isFirefox()' "$browser_js"
    grep -q 'isSafari() || browser_isFirefox()' "$bundle_js"
}

echo "Install KasmVNC server"
cd /tmp
BUILD_ARCH=$(uname -p)
UBUNTU_CODENAME=""
COMMIT_ID="fdc4a63eda4b0bc77742cf1047434515fdf58d17"
BRANCH="release" # just use 'release' for a release branch
KASMVNC_VER="0.9.3.2"
COMMIT_ID_SHORT=$(echo "${COMMIT_ID}" | cut -c1-6)

# Naming scheme is now different between an official release and feature branch
KASM_VER_NAME_PART="${KASMVNC_VER}_${BRANCH}_${COMMIT_ID_SHORT}"
if [[ "${BRANCH}" == "release" ]] ; then
  KASM_VER_NAME_PART="${KASMVNC_VER}"
fi

UBUNTU_CODENAME=$(grep -Po -m 1 "(?<=_CODENAME=)\w+" /etc/os-release)
if [[ "${BUILD_ARCH}" =~ ^aarch64$ ]] ; then
    BUILD_URL="https://kasmweb-build-artifacts.s3.amazonaws.com/kasmvnc/${COMMIT_ID}/kasmvncserver_${UBUNTU_CODENAME}_${KASM_VER_NAME_PART}_arm64.deb"
elif [ "${UBUNTU_CODENAME}" == "bionic" ] ; then
    BUILD_URL="https://kasmweb-build-artifacts.s3.amazonaws.com/kasmvnc/${COMMIT_ID}/kasmvncserver_${UBUNTU_CODENAME}_${KASM_VER_NAME_PART}_libjpeg-turbo-latest_amd64.deb"
else
    BUILD_URL="https://kasmweb-build-artifacts.s3.amazonaws.com/kasmvnc/${COMMIT_ID}/kasmvncserver_${UBUNTU_CODENAME}_${KASM_VER_NAME_PART}_amd64.deb"
fi

wget "${BUILD_URL}" -O kasmvncserver.deb

apt-get update
apt-get install -y gettext ssl-cert libxfont2
dpkg -i /tmp/kasmvncserver.deb
apt-get -yf install
rm -f /tmp/kasmvncserver.deb
patch_clipboard_permission_check

#mkdir $KASM_VNC_PATH/certs
mkdir -p $KASM_VNC_PATH/www/Downloads
chown -R 0:0 $KASM_VNC_PATH
chmod -R og-w $KASM_VNC_PATH
#chown -R 1000:0 $KASM_VNC_PATH/certs
chown -R 1000:0 $KASM_VNC_PATH/www/Downloads
ln -s $KASM_VNC_PATH/www/index.html $KASM_VNC_PATH/www/vnc.html
