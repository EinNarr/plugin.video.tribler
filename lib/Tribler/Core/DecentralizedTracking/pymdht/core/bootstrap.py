# Copyright (C) 2011 Raul Jimenez
# Released under GNU LGPL 2.1
# See LICENSE.txt for more information
"""
- stable and unstable bootstrap addresses (hardcoded)
These nodes are hardcoded (see core/bootstrap.main and
core/bootstrap.backup). These two files are shipped with the code.
Stable nodes are run by us, unstable nodes are wild nodes we have seen running
for a long time.
Harcoded bootstrap nodes SHOULD NOT be added to the routing table to avoid
overloading them (use is_hardcoded() before adding nodes to routing table!

- local bootstrap addresses
These nodes are updated locally, thus the name. The file is saved in the same
directory as the logs (see conf_path in pymdht.Pymdht). If the file does not
exist, the hardcoded unstable list is used.
This file will contain, at most, an IP address per /24 subnet.

"""

import os
import sys
import random
import logging

import ptime as time
import identifier
import message
import node
import utils

logger = logging.getLogger('dht')

HARDCODED_STABLE_FILENAME = 'bootstrap_stable'
HARDCODED_UNSTABLE_FILENAME = 'bootstrap_unstable'
LOCAL_UNSTABLE_FILENAME = 'pymdht.bootstrap'

MAX_ZERO_UPTIME_ADDRS = 2100
MAX_LONG_UPTIME_ADDRS = 2500
ADD_LONG_UPTIME_ADDR_EACH =  3600 # one hour
MIN_LONG_UPTIME = 3600 # one hour
MAX_LONG_UPTIME = 24 * 3600 # write to file, don't wait

class OverlayBootstrapper(object):

    def __init__(self, conf_path, auto_save=True):
        self.auto_save = auto_save
        self.hardcoded_ips = set()
        self._stable_ip_port = {}
        self._unstable_ip_port = {}
        self._all_subnets = set()
        self._local_exists = False
        self._sample_unstable_addrs = []
        self.abs_local_filename = os.path.join(conf_path,
                                               LOCAL_UNSTABLE_FILENAME)

        filename = HARDCODED_STABLE_FILENAME
        f = utils.get_open_file(filename)
        for line in f or []:
            addr = _sanitize_bootstrap_addr(line)
            if addr is None:
                continue

            self.hardcoded_ips.add(addr[0])
            self._stable_ip_port[addr[0]] = addr[1]
            self._all_subnets.add(utils.get_subnet(addr))
        logger.debug('%s: %d hardcoded, %d stable',
                     filename, len(self.hardcoded_ips), len(self._stable_ip_port))
        # local (unstable)
        try:
            f = open(self.abs_local_filename)
        except:
            logger.debug("File does not exist")
            local_exists = False
        else:
            #TODO: use unstable if too few addrs in local? I don't think so
            local_exists = True
            for line in f:
                addr = _sanitize_bootstrap_addr(line)
                if addr is None:
                    continue
                self._unstable_ip_port[addr[0]] = addr[1]
                self._all_subnets.add(utils.get_subnet(addr))
        logger.debug('%s: %d hardcoded, %d unstable',
                     filename, len(self.hardcoded_ips), len(self._unstable_ip_port))
        filename = HARDCODED_UNSTABLE_FILENAME
        f = utils.get_open_file(filename)
        for line in f or []:
            addr = _sanitize_bootstrap_addr(line)
            if addr is None:
                continue
            self.hardcoded_ips.add(addr[0])
            if not local_exists:
                self._unstable_ip_port[addr[0]] = addr[1]
                self._all_subnets.add(utils.get_subnet(addr))
        logger.debug('%s: %d hardcoded, %d unstable',
                     filename, len(self.hardcoded_ips), len(self._unstable_ip_port))
        #long-term variables
        self.next_long_uptime_add_ts = time.time() # do first add asap
        self.longest_uptime = MIN_LONG_UPTIME
        self.longest_uptime_addr = None

    @property
    def unstable_len(self):
        return len(self._unstable_ip_port)

    def get_sample_unstable_addrs(self, num_addrs):
        #TODO: known issue (not critical)
        #If you get a new sample before the previous one is consumed
        #(i.e. self._sample_unstable_addrs == []), one of the assumptions of the
        #off-line detector is broken and the detector will not work.
        if self._sample_unstable_addrs:
            i_warn_you_msg = "You are messing with my off-line detector, my friend"
            logger.warning(i_warn_you_msg)
        if 1:#len(self._unstable_ip_port) < num_addrs:
            logger.debug('>>>len(self._unstable_ip_port) == %d, num_addrs: %d',
                         len(self._unstable_ip_port), num_addrs)

        self._sample_unstable_addrs = random.sample(
            self._unstable_ip_port.items(),
            min(num_addrs, len(self._unstable_ip_port))
            ) #TODO: what if the file is empty/contains too few nodes?
        # return a copy (lookup manager may modify it)
        return self._sample_unstable_addrs[:]

    def get_shuffled_stable_addrs(self):
        addrs = self._stable_ip_port.items()
        random.shuffle(addrs)
        return addrs

    def is_hardcoded(self, addr):
        """
        Having addresses hardcoded increases the load of these nodes "lucky"
        enough to be in the list.
        To compensate, these nodes should not be added to the routing table.

        Routing manager should check a node before adding to routing table.
        """
        return addr[0] in self.hardcoded_ips

    def report_unreachable(self, addr):
        """
        Use only during overlay bootstrap
        """
        if addr[0] not in self._unstable_ip_port:
            # Addr not present in a bootstrap list. Ignore.
            return
        # Reported addrs will be deleted from UNSTABLE list.  We consider the
        # case of a temporaly off-line node that incorrectly report nodes as
        # unreachable, when in reality the reported node may be reachable. This
        # case is common in Android (battery-saving settings shut off radio to
        # save battery).

        # The idea is that if addrs are reported as unreachable in the same order
        # as pinged (i.e. same as self._sample_unstable_addrs), we assume the
        # local node is off-line and do not remove the addr from UNSTABLE.

        # To make it simpler, we don't allow creating multiple samples (see
        # get_sample_unstable_addrs).
        if self._sample_unstable_addrs:
            if addr == self._sample_unstable_addrs.pop(0):
                # assume local node is off-line, do not remove
                logger.debug('OFF-LINE %s:%s', addr[0], addr[1])
                return
            else:
                self._sample_unstable_addrs = [] # end off-line mode
        #remove from dict (if present)
        del self._unstable_ip_port[addr[0]]
        self._all_subnets.remove(utils.get_subnet(addr))
        logger.debug('REMOVED %s:%s', addr[0], addr[1])

    def report_reachable(self, addr, uptime=0):
        """
        - uptime == 0:
          This node has been discovered during overlay boostrap. It will be added
          to the UNSTABLE list if there is enough room.
          **Use only from lookup manager (overlay bootstrap lookup).
        - uptime > 0:
          This node has been in the routing table for some time
          (uptime seconds). Once in a while, a long-term reachable node is
          written to the UNSTABLE file.
          **Use only from routing table manager.
        """
        addr_subnet = utils.get_subnet(addr)
        if len(self._unstable_ip_port) >= MAX_LONG_UPTIME_ADDRS:
            # Enough addrs in the list. Ignore.
            logging.debug('MAX_LONG_UPTIME_ADDRS reached')
            return
        if addr_subnet in self._all_subnets:
            # Subnet already in a bootstrap list. Ignore.
            logging.debug('subnet exists')
            return
        if uptime == 0:
            if len(self._unstable_ip_port) < MAX_ZERO_UPTIME_ADDRS:
                logger.debug('added short %s:%s', addr[0], addr[1])
                self._unstable_ip_port[addr[0]] = addr[1]
                self._all_subnets.add(addr_subnet)
        elif uptime >= MAX_LONG_UPTIME:
            # 24 hours. Add it right away.
            logger.debug('added 24h long: %s:%s, %f hours',
                         addr[0], addr[1], uptime / 3600)
            self._unstable_ip_port[addr[0]] = addr[1]
            self._all_subnets.add(addr_subnet)
        elif uptime >= self.longest_uptime:
            assert uptime >= MIN_LONG_UPTIME
            self.longest_uptime = uptime
            self.longest_uptime_addr = addr
            if time.time() >= self.next_long_uptime_add_ts:
                logger.debug('added long: %s:%s, %f hours',
                             addr[0], addr[1], uptime / 3600)
                self._unstable_ip_port[addr[0]] = addr[1]
                self._all_subnets.add(addr_subnet)
                self.longest_uptime = MIN_LONG_UPTIME
                self.next_long_uptime_add_ts += ADD_LONG_UPTIME_ADDR_EACH
                assert self.longest_uptime_addr
                self.longest_uptime_addr = None
                if self.auto_save:
                    self.save_to_file()

    def save_to_file(self):
        addrs = self._unstable_ip_port.items()
        addrs.sort()
        try:
            out = open(self.abs_local_filename, 'w')
        except:
            logger.exception()
            return
        for addr in addrs:
            logger.debug("%s, %s", addr[0], addr[1])  # TODO: inet_aton


def _sanitize_bootstrap_addr(line):
    params = line.split()
    if len(params) != 2:
        logging.warn('invalid bootstrap addr: %s', line)
        return
    ip, port_str = params
    try:
        port = int(port_str)
    except ValueError:
        logging.warn('invalid port (%s) in bootstrap addr: %s', port_str, line)
        return
    return ip, port
