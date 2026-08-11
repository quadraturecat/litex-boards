#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2026 Scott Torborg <storborg@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxUSPPlatform
from litex.build.openfpgaloader import OpenFPGALoader

# IOs ----------------------------------------------------------------------------------------------

_io = [
    ("clk300", 0,
        Subsignal("p", Pins("AD21"), IOStandard("DIFF_SSTL12")),
        Subsignal("n", Pins("AE21"), IOStandard("DIFF_SSTL12"))
    ),
    # System reset: pulled up by default, active low with press PB3
    ("cpu_reset_n", 0, Pins("V19"), IOStandard("LVCMOS12")),

    ("clk156p25", 0,
        Subsignal("p", Pins("Y7")),
        Subsignal("n", Pins("Y6")),
    ),

    # User push buttons: pulled down by default, active high with press
    ("user_btn", 0, Pins("R21"), IOStandard("LVCMOS12")),
    ("user_btn", 1, Pins("R20"), IOStandard("LVCMOS12")),
    ("user_btn", 2, Pins("P21"), IOStandard("LVCMOS12")),
    ("user_btn", 3, Pins("P20"), IOStandard("LVCMOS12")),

    # User switches
    ("user_sw", 0, Pins("P19"), IOStandard("LVCMOS12")),
    ("user_sw", 1, Pins("N19"), IOStandard("LVCMOS12")),
    ("user_sw", 2, Pins("P23"), IOStandard("LVCMOS12")),
    ("user_sw", 3, Pins("N23"), IOStandard("LVCMOS12")),

    # LEDs
    ("user_led", 0, Pins("A10"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("B10"), IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("B11"), IOStandard("LVCMOS33")),
    ("user_led", 3, Pins("C11"), IOStandard("LVCMOS33")),

    ("rgb_led", 0,
        Subsignal("r", Pins("AE15")),
        Subsignal("g", Pins("AD15")),
        Subsignal("b", Pins("AF13")),
        IOStandard("LVCMOS18"),
    ),
    ("rgb_led", 1,
        Subsignal("r", Pins("U26")),
        Subsignal("g", Pins("P24")),
        Subsignal("b", Pins("N24")),
        IOStandard("LVCMOS12"),
    ),

    # Serial.
    ("serial", 0,
        Subsignal("tx", Pins("AF15"), IOStandard("LVCMOS18")),
        Subsignal("rx", Pins("AF14"), IOStandard("LVCMOS18")),
    ),

    # DDR4 SDRAM IS43QR16512A-083TBL
    ("ddram", 0,
        Subsignal("a", Pins(
            "AE22 AF22 AD23 AE23 AC22 AC23 AB21 AC21",
            "AF20 AD20 AE20 AC19 AD19 AF18"),
            IOStandard("SSTL12_DCI")),
        Subsignal("ba",      Pins("AE17 AF17"), IOStandard("SSTL12_DCI")),
        Subsignal("bg",      Pins("AD16"), IOStandard("SSTL12_DCI")),
        Subsignal("ras_n",   Pins("AD18"), IOStandard("SSTL12_DCI")), # A16
        Subsignal("cas_n",   Pins("AC18"), IOStandard("SSTL12_DCI")), # A15
        Subsignal("we_n",    Pins("AF19"), IOStandard("SSTL12_DCI")), # A14
        Subsignal("cs_n",    Pins("AE16"), IOStandard("SSTL12_DCI")),
        Subsignal("act_n",   Pins("Y21"), IOStandard("SSTL12_DCI")),
        Subsignal("dm",      Pins("AE25 Y20 U19 Y22"),
            IOStandard("POD12_DCI")),
        Subsignal("dq",      Pins(
            "AB25 AB26 AF24 AF25 AD24 AD25 AB24 AC24",
            "AA19 AB19 AA20 AB20 Y17  AA17 Y18  AA18",
            "U21  U22  T20  U20  T22  T23  W19  W20",
            "Y25  Y26  AA24 AA25 V23  W23  V24  W24"),
            IOStandard("POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_p",   Pins("AC26 AB17 V21 W25"),
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("dqs_n",   Pins("AD26 AC17 V22 W26"),
            IOStandard("DIFF_POD12_DCI"),
            Misc("PRE_EMPHASIS=RDRV_240"),
            Misc("EQUALIZATION=EQ_LEVEL2")),
        Subsignal("clk_p",   Pins("AA22"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("clk_n",   Pins("AB22"), IOStandard("DIFF_SSTL12_DCI")),
        Subsignal("cke",     Pins("AE18"), IOStandard("SSTL12_DCI")),
        Subsignal("odt",     Pins("AE26"), IOStandard("SSTL12_DCI")),
        Subsignal("reset_n", Pins("AC16"), IOStandard("LVCMOS12")),
        Misc("SLEW=FAST"),
    ),

    ("spiflash4x", 0,
        Subsignal("cs_n", Pins("AA12")),
        Subsignal("clk",  Pins("Y11")),
        Subsignal("dq",   Pins("AD11 AC12 AC11 AE11")),
        IOStandard("LVCMOS18")
    ),


    # MII Ethernet (10/100 only)
    ("eth_clocks", 0,
        Subsignal("tx", Pins("AA14")),
        Subsignal("rx", Pins("Y15")),
        IOStandard("LVCMOS18"),
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("AC14")),
        Subsignal("mdio",    Pins("AC13")),
        Subsignal("mdc",     Pins("AB15")),
        Subsignal("rx_dv",   Pins("AA15")),
        Subsignal("rx_er",   Pins("AB16")),
        Subsignal("rx_data", Pins("W15 W14 Y16 W16")),
        Subsignal("tx_en",   Pins("AB14")),
        Subsignal("tx_er",   Pins("AE13")),  # XXX What's this??
        Subsignal("tx_data", Pins("W13 W12 AA13 Y13")),
        Subsignal("col",     Pins("AD14")),
        Subsignal("crs",     Pins("AD13")),
        IOStandard("LVCMOS18"),
    ),

    # PCIe.
    ("pcie_x1", 0,
        Subsignal("rst_n", Pins("E11"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("AB7")),
        Subsignal("clk_n", Pins("AB6")),
        Subsignal("rx_p",  Pins("AF2")),
        Subsignal("rx_n",  Pins("AF1")),
        Subsignal("tx_p",  Pins("AF7")),
        Subsignal("tx_n",  Pins("AF6"))
    ),
    ("pcie_x2", 0,
        Subsignal("rst_n", Pins("E11"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("AB7")),
        Subsignal("clk_n", Pins("AB6")),
        Subsignal("rx_p",  Pins("AF2 AE4")),
        Subsignal("rx_n",  Pins("AF1 AE3")),
        Subsignal("tx_p",  Pins("AF7 AE9")),
        Subsignal("tx_n",  Pins("AF6 AE8"))
    ),
    ("pcie_x4", 0,
        Subsignal("rst_n", Pins("E11"), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("AB7")),
        Subsignal("clk_n", Pins("AB6")),
        Subsignal("rx_p",  Pins("AF2 AE4 AD2 AB2")),
        Subsignal("rx_n",  Pins("AF1 AE3 AD1 AB1")),
        Subsignal("tx_p",  Pins("AF7 AE9 AD7 AC5")),
        Subsignal("tx_n",  Pins("AF6 AE8 AD6 AC4"))
    ),

    # SFP
    ("sfp", 0,
        Subsignal("txp", Pins("G5")),
        Subsignal("txn", Pins("G4")),
        Subsignal("rxp", Pins("F2")),
        Subsignal("rxn", Pins("F1")),
    ),
    ("sfp_tx", 0,
        Subsignal("p", Pins("G5")),
        Subsignal("n", Pins("G4")),
    ),
    ("sfp_rx", 0,
        Subsignal("p", Pins("F2")),
        Subsignal("n", Pins("F1")),
    ),
    ("sfp_tx_disable", 0, Pins("N22"), IOStandard("LVCMOS12")),
    ("sfp_tx_fault",     0, Pins("V26"), IOStandard("LVCMOS12")),
    ("sfp_rx_los",       0, Pins("E10"), IOStandard("LVCMOS12")),

    # I2C
    # This is connected to a PCA9544 expander at address 0x70
    # Mux port 0: SFP connector
    # Mux port 1: Click interface
    # Mux port 2: FMC interface
    # Mux port 3: Temp sensor STTS22HTR at address 0x3f
    ("i2c", 0,
        Subsignal("scl", Pins("D9")),
        Subsignal("sda", Pins("C9")),
        IOStandard("LVCMOS33"),
    ),
]


# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # Note: really, the FMC connector on the AUBoard-15P is somewhere in
    # between an LPC and HPC. Four transceivers are populated, but no HAnn
    # signals.
    ("LPC", {
        "CLK0_M2C_P"    : "G12",
        "CLK0_M2C_N"    : "F12",
        "CLK1_M2C_P"    : "F14",
        "CLK1_M2C_N"    : "F13",
        "LA00_CC_P"     : "F24",
        "LA00_CC_N"     : "F25",
        "LA01_CC_P"     : "J23",
        "LA01_CC_N"     : "J24",
        "LA02_P"        : "H26",
        "LA02_N"        : "G26",
        "LA03_P"        : "M20",
        "LA03_N"        : "M21",
        "LA04_P"        : "J19",
        "LA04_N"        : "J20",
        "LA05_P"        : "M19",
        "LA05_N"        : "L19",
        "LA06_P"        : "D26",
        "LA06_N"        : "C26",
        "LA07_P"        : "J12",
        "LA07_N"        : "H12",
        "LA08_P"        : "H14",
        "LA08_N"        : "G14",
        "LA09_P"        : "H21",
        "LA09_N"        : "H22",
        "LA10_P"        : "E25",
        "LA10_N"        : "E26",
        "LA11_P"        : "E13",
        "LA11_N"        : "E12",
        "LA12_P"        : "L18",
        "LA12_N"        : "K18",
        "LA13_P"        : "K22",
        "LA13_N"        : "K23",
        "LA14_P"        : "L20",
        "LA14_N"        : "K20",
        "LA15_P"        : "K21",
        "LA15_N"        : "J21",
        "LA16_P"        : "L24",
        "LA16_N"        : "L25",
        "LA17_CC_P"     : "J25",
        "LA17_CC_N"     : "J26",
        "LA18_CC_P"     : "G24",
        "LA18_CC_N"     : "G25",
        "LA19_P"        : "F23",
        "LA19_N"        : "E23",
        "LA20_P"        : "D24",
        "LA20_N"        : "D25",
        "LA21_P"        : "D23",
        "LA21_N"        : "C24",
        "LA22_P"        : "B14",
        "LA22_N"        : "A14",
        "LA23_P"        : "B25",
        "LA23_N"        : "B26",
        "LA24_P"        : "H23",
        "LA24_N"        : "H24",
        "LA25_P"        : "J13",
        "LA25_N"        : "H13",
        "LA26_P"        : "L22",
        "LA26_N"        : "L23",
        "LA27_P"        : "J15",
        "LA27_N"        : "J14",
        "LA28_P"        : "K25",
        "LA28_N"        : "K26",
        "LA29_P"        : "D14",
        "LA29_N"        : "D13",
        "LA30_P"        : "C14",
        "LA30_N"        : "C13",
        "LA31_P"        : "C12",
        "LA31_N"        : "B12",
        "LA32_P"        : "A13",
        "LA32_N"        : "A12",
        "LA33_P"        : "M25",
        "LA33_N"        : "M26",
        "GBTCLK0_M2C_P" : "V7",
        "GBTCLK0_M2C_N" : "V6",
        "GBTCLK1_M2C_P" : "T7",
        "GBTCLK1_M2C_N" : "T6",
        "PRSNT_M2C_B"   : "F10",
        "DP0_C2M_P"     : "AA5",  # C2
        "DP0_C2M_N"     : "AA4",  # C3
        "DP0_M2C_P"     : "Y2",  # C6
        "DP0_M2C_N"     : "Y1",  # C7
        "DP1_M2C_P"     : "V2",  # A2
        "DP1_M2C_N"     : "V1",  # A3
        "DP1_C2M_P"     : "W5",  # A22
        "DP1_C2M_N"     : "W4",  # A23
        "DP2_M2C_P"     : "T2",  # A6
        "DP2_M2C_N"     : "T1",  # A7
        "DP2_C2M_P"     : "U5",  # A26
        "DP2_C2M_N"     : "U4",  # A27
        "DP3_M2C_P"     : "P2",  # A10
        "DP3_M2C_N"     : "P1",  # A11
        "DP3_C2M_P"     : "R5",  # A30
        "DP3_C2M_N"     : "R4",  # A31
        }
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxUSPPlatform):
    default_clk_name   = "clk300"
    default_clk_period = 1e9/300e6

    def __init__(self, toolchain="vivado"):
        XilinxUSPPlatform.__init__(self, "xcau15p-ffvb676-2-e", _io, _connectors, toolchain=toolchain)

    def create_programmer(self):
        return OpenFPGALoader(
            fpga_part="xcau15p-ffvb676",
            cable="ft2232",
            ftdi_serial="1234-oj1",
            freq=15e6,
        )

    def do_finalize(self, fragment):
        XilinxUSPPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk300", loose=True), 1e9/300e6)
        self.add_period_constraint(self.lookup_request("clk156p25", loose=True), 1e9/156.25e6)
        self.add_platform_command("set_property INTERNAL_VREF 0.84 [get_iobanks 66]")
