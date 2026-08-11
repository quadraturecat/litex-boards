#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Scott Torborg <storborg@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

import os

from migen import *

from litex.gen import *

from litex_boards.platforms import tria_auboard15p

from litex.soc.cores.clock import *
from litex.soc.integration.soc import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.xadc import USSystemMonitor
from litex.soc.cores.dna import USDNA
from litex.soc.cores.bitbang import I2CMaster
from litex.soc.cores.spi import SPIMaster

from litedram.modules import IS43QR16512A
from litedram.phy import usddrphy

from liteeth.phy import LiteEthPHYMII
from liteeth.phy.usp_gth_1000basex import USP_GTH_1000BASEX

from litepcie.phy.usppciephy import USPPCIEPHY
from litepcie.software import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain("sys")
        self.cd_sys4x  = ClockDomain("sys4x")
        self.cd_idelay = ClockDomain("idelay")

        # # #

        # Clk.
        clk300 = platform.request("clk300")

        # PLL.
        self.pll = pll = USMMCM(speedgrade=-2)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk300, 300e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq, with_reset=False)
        pll.create_clkout(self.cd_sys4x,  4*sys_clk_freq)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.idelayctrl = USPIDELAYCTRL(cd_ref=self.cd_sys4x, cd_sys=self.cd_sys)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(125e6),
        with_xadc       = False,
        with_dna        = False,
        with_ethernet   = False,
        with_etherbone  = False,
        eth_ip          = "192.168.1.50",
        eth_phy         = "mii",
        remote_ip       = None,
        eth_dynamic_ip  = False,
        with_led_chaser = True,
        with_pcie       = False, pcie_speed="gen3",
        with_sdcard     = False,
        **kwargs):
        platform = tria_auboard15p.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Tria AUBoard-15P", **kwargs)

        self.add_jtagbone()

        i2c_pads = platform.request("i2c")
        self.i2c = I2CMaster(i2c_pads)

        if with_xadc:
            self.xadc = USSystemMonitor()

        if with_dna:
            self.dna = USDNA()
            self.dna.add_timing_constraints(platform, sys_clk_freq, self.crg.cd_sys.clk)

        # DDR4 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.ddrphy = usddrphy.USPDDRPHY(platform.request("ddram"),
                memtype          = "DDR4",
                sys_clk_freq     = sys_clk_freq,
                iodelay_clk_freq = 500e6
            )
            self.add_sdram("sdram",
                phy           = self.ddrphy,
                module        = IS43QR16512A(sys_clk_freq, "1:4"),
                size          = 0x40000000,
                l2_cache_size = kwargs.get("l2_size", 8192)
            )

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = USPPCIEPHY(platform, platform.request("pcie_x4"),
                speed      = pcie_speed,
                data_width = {"gen3": 128, "gen4": 256}[pcie_speed],
                ip_name    = "pcie4c_uscale_plus",
                bar0_size  = 0x20000,
            )
            self.pcie_phy.update_config({
                "mode_selection"   : "Advanced",
                "en_gt_selection"  : "true",
                "select_quad"      : "GTH_Quad_224",
                "pcie_blk_locn"    : "X0Y0",
                "gen_x0y0"         : "true",
                "gen_x1y0"         : "false",
            })
            self.add_pcie(phy=self.pcie_phy, ndmas=1)

        # Ethernet / Etherbone ---------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            if eth_phy == "mii":
                self.ethphy = LiteEthPHYMII(
                    clock_pads = self.platform.request("eth_clocks"),
                    pads       = self.platform.request("eth"),
                )
            elif eth_phy == "sfp":
                self.ethphy = USP_GTH_1000BASEX(
                    self.platform.request("clk156p25", 0),
                    data_pads=self.platform.request("sfp", 0),
                    sys_clk_freq=sys_clk_freq,
                    refclk_freq=156.25e6,
                )
                self.comb += self.platform.request("sfp_tx_disable", 0).eq(0)
            else:
                raise ValueError(
                    "unsupported phy %r, pick from mii, sfp, or sfp+" % eth_phy
                )
            if with_etherbone:
                self.add_etherbone(phy=self.ethphy, ip_address=eth_ip, with_ethmac=with_ethernet)
            if with_ethernet:
                self.add_ethernet(phy=self.ethphy, dynamic_ip=eth_dynamic_ip, local_ip=eth_ip, remote_ip=remote_ip)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

        # TODO add RGB LEDs / pushbuttons / switches?
        # TODO add SFP
        # TODO add HDMI


# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=tria_auboard15p.Platform, description="LiteX SoC on AUBoard-15P.")
    parser.add_target_argument("--sys-clk-freq",        default=125e6, type=float, help="System clock frequency.")
    parser.add_target_argument("--with-xadc", action="store_true", help="Enable XADC.")
    parser.add_target_argument("--with-dna", action="store_true", help="Enable DNA.")
    parser.add_target_argument("--eth-phy",        default="mii", help="Ethernet PHY (mii|sfp|sfp+)")
    ethopts = parser.target_group.add_mutually_exclusive_group()
    ethopts.add_argument("--with-ethernet",  action="store_true", help="Enable Ethernet support.")
    ethopts.add_argument("--with-etherbone", action="store_true", help="Enable Etherbone support.")
    parser.add_target_argument("--eth-ip",         default="192.168.1.50",                   help="Ethernet/Etherbone IP address.")
    parser.add_target_argument("--remote-ip",      default="192.168.1.100",                  help="Remote IP address of TFTP server.")
    parser.add_target_argument("--eth-dynamic-ip", action="store_true",                      help="Enable dynamic Ethernet IP assignment.")
    parser.add_target_argument("--with-pcie",      action="store_true",                      help="Enable PCIe support.")
    parser.add_target_argument("--pcie-speed",     default="gen3", choices=["gen3", "gen4"], help="PCIe speed.")
    parser.add_target_argument("--driver",         action="store_true",                      help="Generate PCIe driver.")
    args = parser.parse_args()

    assert not (args.with_etherbone and args.eth_dynamic_ip)

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        with_xadc      = args.with_xadc,
        with_dna       = args.with_dna,
        with_ethernet  = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        eth_phy        = args.eth_phy,
        eth_ip         = args.eth_ip,
        remote_ip      = args.remote_ip,
        eth_dynamic_ip = args.eth_dynamic_ip,
        with_pcie      = args.with_pcie,
        pcie_speed     = args.pcie_speed,
        **parser.soc_argdict
    )

    builder = Builder(soc, **parser.builder_argdict)
    if args.build or args.driver:
        if not args.build:
            builder.compile_software = False
            builder.compile_gateware = False
        builder.build(**parser.toolchain_argdict)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
