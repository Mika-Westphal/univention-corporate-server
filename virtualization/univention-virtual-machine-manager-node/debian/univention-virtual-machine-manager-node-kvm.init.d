#!/bin/sh
# Univention Virtual Machine Manager KVM Node
#  init script
#
# Copyright 2010 Univention GmbH
#
# http://www.univention.de/
#
# All rights reserved.
#
# The source code of this program is made available
# under the terms of the GNU Affero General Public License version 3
# (GNU AGPL V3) as published by the Free Software Foundation.
#
# Binary versions of this program provided by Univention to you as
# well as other copyrighted, protected or trademarked materials like
# Logos, graphics, fonts, specific documentations and configurations,
# cryptographic keys etc. are subject to a license agreement between
# you and Univention and not subject to the GNU AGPL V3.
#
# In the case you use this program under the terms of the GNU AGPL V3,
# the program is provided in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License with the Debian GNU/Linux or Univention distribution in file
# /usr/share/common-licenses/AGPL-3; if not, see
# <http://www.gnu.org/licenses/>.
#
### BEGIN INIT INFO
# Provides:          univention-virtual-machine-manager-node-kvm
# Required-Start:    $network $local_fs
# Required-Stop:
# Should-Start:      $named
# Should-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Univention Virtual Machine Manager KVM Node
# Description:       Create a bridging network interface
### END INIT INFO

# configure interfaces which act as pure bridge ports:
setup_bridge_port() {
    local dev="$1"

    # take interface down ...
    ip link set ${dev} down

    # ... and configure it
    ip addr flush ${dev}
}

# Usage: create_bridge bridge
create_bridge () {
    local bridge=$1

    # Don't create the bridge if it already exists.
    if [ ! -e "/sys/class/net/${bridge}/bridge" ]; then
	brctl addbr ${bridge}
	brctl stp ${bridge} off
	brctl setfd ${bridge} 0
    fi
}

# Usage: add_to_bridge bridge dev
add_to_bridge () {
    local bridge=$1
    local dev=$2

    # Don't add $dev to $bridge if it's already on a bridge.
    if [ -e "/sys/class/net/${bridge}/brif/${dev}" ]; then
	ip link set ${dev} up || true
	return
    fi
    brctl addif ${bridge} ${dev}
    ip link set ${dev} up
}

is_network_root () {
    local rootfs=$(awk '{ if ($1 !~ /^[ \t]*#/ && $2 == "/") { print $3; }}' /etc/mtab)
    local rootopts=$(awk '{ if ($1 !~ /^[ \t]*#/ && $2 == "/") { print $4; }}' /etc/mtab)

    [[ "$rootfs" =~ "^nfs" ]] || [[ "$rootopts" =~ "_netdev" ]] && has_nfsroot=1 || has_nfsroot=0
    if [ $has_nfsroot -eq 1 ]; then
        local bparms=$(cat /proc/cmdline)
        for p in $bparms; do
            local ipaddr=$(echo $p | awk /nfsroot=/'{ print substr($1,9,index($1,":")-9) }')
            if [ "$ipaddr" != "" ]; then
                local nfsdev=$(ip route get $ipaddr | awk /$ipaddr/'{ print $3 }')
                [[ "$nfsdev" == "$netdev" ]] && return 0 || return 1
            fi
        done
    fi
    return 1
}

find_alt_device () {
    local interf=$1
    local prefix=${interf%[[:digit:]]}
    local ifs=$(ip link show | grep " $prefix" |\
                gawk '{ printf ("%s",substr($2,1,length($2)-1)) }' |\
                sed s/$interf//)
    echo "$ifs"
}

netdev=${netdev:-$(ip route list 0.0.0.0/0  | \
                   sed 's/.*dev \([a-z]\+[0-9]\+\).*$/\1/')}
if is_network_root ; then
    altdevs=$(find_alt_device $netdev)
    for netdev in $altdevs; do break; done
    if [ -z "$netdev" ]; then
        [ -x /usr/bin/logger ] && /usr/bin/logger "network-bridge: bridging not supported on network root; not starting"
        exit
    fi
fi
netdev=${netdev:-eth0}
bridge=${bridge:-${netdev}}
antispoof=${antispoof:-no}

pdev="p${netdev}"
tdev=tmpbridge

get_ip_info() {
    addr_pfx=`ip addr show dev $1 | egrep '^ *inet' | sed -e 's/ *inet //' -e 's/ .*//'`
    gateway=`ip route show dev $1 | fgrep default | sed 's/default via //'`
}
    
do_ifup() {
    if [ $1 != "${netdev}" ] || ! ifup $1 ; then
        if [ -n "$addr_pfx" ] ; then
            # use the info from get_ip_info()
            ip addr flush $1
            ip addr add ${addr_pfx} dev $1
            ip link set dev $1 up
            [ -n "$gateway" ] && ip route add default via ${gateway}
        fi
    fi
}

# Usage: transfer_addrs src dst
# Copy all IP addresses (including aliases) from device $src to device $dst.
transfer_addrs () {
    local src=$1
    local dst=$2
    # Don't bother if $dst already has IP addresses.
    if ip addr show dev ${dst} | egrep -q '^ *inet ' ; then
        return
    fi
    # Address lines start with 'inet' and have the device in them.
    # Replace 'inet' with 'ip addr add' and change the device name $src
    # to 'dev $src'.
    ip addr show dev ${src} | egrep '^ *inet ' | sed -e "
s/inet/ip addr add/
s@\([0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+/[0-9]\+\)@\1@
s/${src}/dev ${dst} label ${dst}/
s/secondary//
" | sh -e
    # Remove automatic routes on destination device
    ip route list | sed -ne "
/dev ${dst}\( \|$\)/ {
  s/^/ip route del /
  p
}" | sh -e
}

# Usage: transfer_routes src dst
# Get all IP routes to device $src, delete them, and
# add the same routes to device $dst.
# The original routes have to be deleted, otherwise adding them
# for $dst fails (duplicate routes).
transfer_routes () {
    local src=$1
    local dst=$2
    # List all routes and grep the ones with $src in.
    # Stick 'ip route del' on the front to delete.
    # Change $src to $dst and use 'ip route add' to add.
    ip route list | sed -ne "
/dev ${src}\( \|$\)/ {
  h
  s/^/ip route del /
  P
  g
  s/${src}/${dst}/
  s/^/ip route add /
  P
  d
}" | sh -e
}


##
# link_exists interface
#
# Returns 0 if the interface named exists (whether up or down), 1 otherwise.
#
link_exists()
{
    if ip link show "$1" >/dev/null 2>/dev/null
    then
        return 0
    else
        return 1
    fi
}

# Set the default forwarding policy for $dev to drop.
# Allow forwarding to the bridge.
antispoofing () {
    iptables -P FORWARD DROP
    iptables -F FORWARD
    iptables -A FORWARD -m physdev --physdev-in ${pdev} -j ACCEPT
}

# Usage: show_status dev bridge
# Print ifconfig and routes.
show_status () {
    local dev=$1
    local bridge=$2

    echo '============================================================'
    ip addr show ${dev}
    ip addr show ${bridge}
    echo ' '
    brctl show ${bridge}
    echo ' '
    ip route list
    echo ' '
    route -n
    echo '============================================================'
}

op_start () {
    if [ "${bridge}" = "null" ] ; then
	return
    fi

    if link_exists "$pdev"; then
        # The device is already up.
        return
    fi

    create_bridge ${tdev}

    transfer_addrs ${netdev} ${tdev}
    # Remember slaves for bonding interface.
    if [ -e /sys/class/net/${netdev}/bonding/slaves ]; then
	slaves=`cat /sys/class/net/${netdev}/bonding/slaves`
    fi
    # Remember the IP details for do_ifup.
    get_ip_info ${netdev}
    if ! ifdown ${netdev}; then
	ip link set ${netdev} down
	ip addr flush ${netdev}
    fi
    ip link set ${netdev} name ${pdev}
    ip link set ${tdev} name ${bridge}

    setup_bridge_port ${pdev}

    # Restore slaves
    if [ -n "${slaves}" ]; then
		ip link set ${pdev} up
		ifenslave ${pdev} ${slaves}
    fi
    add_to_bridge2 ${bridge} ${pdev}
    do_ifup ${bridge}

    if [ ${antispoof} = 'yes' ] ; then
	antispoofing
    fi
}

op_stop () {
    if [ "${bridge}" = "null" ]; then
	return
    fi
    if ! link_exists "$bridge"; then
	return
    fi

    transfer_addrs ${bridge} ${pdev}
    if ! ifdown ${bridge}; then
	get_ip_info ${bridge}
    fi
    ip link set ${pdev} down
    ip addr flush ${bridge}

    brctl delif ${bridge} ${pdev}
    ip link set ${bridge} down

    ip link set ${bridge} name ${tdev}
    ip link set ${pdev} name ${netdev}
    do_ifup ${netdev}

    brctl delbr ${tdev}
}

# adds $dev to $bridge but waits for $dev to be in running state first
add_to_bridge2() {
    local bridge=$1
    local dev=$2
    local maxtries=10

    echo -n "Waiting for ${dev} to negotiate link."
    ip link set ${dev} up
    for i in `seq ${maxtries}` ; do
	if ifconfig ${dev} | grep -q RUNNING ; then
	    break
	else
	    echo -n '.'
	    sleep 1
	fi
    done

    if [ ${i} -eq ${maxtries} ] ; then echo -n '(link isnt in running state)' ; fi
    echo

    add_to_bridge ${bridge} ${dev}
}

command=$1
case "$command" in
    start)
		op_start
		;;
    stop)
		op_stop
		;;
    status)
		show_status ${netdev} ${bridge}
		;;
    *)
		echo "Unknown command: $command" >&2
		echo 'Valid commands are: start, stop, status' >&2
		exit 1
esac
