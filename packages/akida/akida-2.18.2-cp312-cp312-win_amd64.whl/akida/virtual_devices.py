import warnings
from collections import namedtuple
from math import ceil, floor, sqrt

from .core import (NP, AKD1500_v1, Device, FPGA_v2, IpVersion,
                   NSoC_v1, NSoC_v2, TwoNodesIP_v1, LayerType, Model)
from .mapping import MapMode


LayerSequence = namedtuple('LayerSequence', ['layers'])


def AKD1000():
    """Returns a virtual device for an AKD1000 NSoC.

    This function returns a virtual device for the Brainchip's AKD1000
    NSoC.

    Returns:
        :obj:`Device`: a virtual device.

    """
    dma_event = NP.Ident(3, 1, 0)
    dma_conf = NP.Ident(3, 1, 1)
    nps = [
        NP.Info(NP.Ident(1, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(1, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(1, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(1, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(1, 4, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(1, 4, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(1, 4, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(1, 4, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(1, 5, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(1, 5, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(1, 5, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(1, 5, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(2, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(2, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(2, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(2, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(2, 4, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(2, 4, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(2, 4, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(2, 4, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(2, 5, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(2, 5, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(2, 5, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(2, 5, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 1, 2), {NP.Type.CNP1}, False),
        NP.Info(NP.Ident(3, 1, 3), {NP.Type.CNP1}, False),
        NP.Info(NP.Ident(3, 2, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(3, 2, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 2, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 2, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(3, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 4, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(3, 4, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 4, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 4, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 5, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(3, 5, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 5, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 5, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(4, 1, 0), {NP.Type.CNP1, NP.Type.FNP2}, False),
        NP.Info(NP.Ident(4, 1, 1), {NP.Type.CNP1, NP.Type.FNP2}, False),
        NP.Info(NP.Ident(4, 1, 2), {NP.Type.CNP1, NP.Type.FNP2}, False),
        NP.Info(NP.Ident(4, 1, 3), {NP.Type.CNP1, NP.Type.FNP2}, False),
        NP.Info(NP.Ident(4, 2, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(4, 2, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(4, 2, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(4, 2, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(4, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(4, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(4, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(4, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(4, 4, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(4, 4, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(4, 4, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(4, 4, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(4, 5, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(4, 5, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(4, 5, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(4, 5, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(5, 2, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(5, 2, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(5, 2, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(5, 2, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(5, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(5, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(5, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(5, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(5, 4, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(5, 4, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(5, 4, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(5, 4, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(5, 5, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(5, 5, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(5, 5, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(5, 5, 3), {NP.Type.CNP1, NP.Type.CNP2}, False)
    ]
    mesh = NP.Mesh(IpVersion.v1, dma_event, dma_conf, NP.Info.hrc(False), nps)
    return Device(NSoC_v2, mesh)


def TwoNodesIPv1():
    """Returns a virtual device for a two nodes Akida IP.

    Returns:
        :obj:`Device`: a virtual device.

    """
    dma_event = NP.Ident(1, 1, 0)
    dma_conf = NP.Ident(1, 1, 1)
    nps = [
        NP.Info(NP.Ident(1, 2, 0), {NP.Type.CNP1, NP.Type.FNP2}, False),
        NP.Info(NP.Ident(1, 2, 1), {NP.Type.CNP1}, False),
        NP.Info(NP.Ident(1, 2, 2), {NP.Type.CNP1}, False),
        NP.Info(NP.Ident(1, 2, 3), {NP.Type.CNP1}, False),
        NP.Info(NP.Ident(1, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(1, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(1, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(1, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}, False)
    ]
    mesh = NP.Mesh(IpVersion.v1, dma_event, dma_conf, NP.Info.hrc(False), nps)
    return Device(TwoNodesIP_v1, mesh)


def AKD1500():
    """Returns a virtual device for AKD1500 chip.

    Returns:
        :obj:`Device`: a virtual device.

    """
    dma_event = NP.Ident(1, 1, 0)
    dma_conf = NP.Ident(1, 1, 1)
    nps = [
        NP.Info(NP.Ident(1, 2, 0), {NP.Type.CNP1, NP.Type.FNP2}, False),
        NP.Info(NP.Ident(1, 2, 1), {NP.Type.CNP1}, False),
        NP.Info(NP.Ident(1, 2, 2), {NP.Type.CNP1}, False),
        NP.Info(NP.Ident(1, 2, 3), {NP.Type.CNP1}, False),
        NP.Info(NP.Ident(1, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(1, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(1, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(1, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(2, 1, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(2, 1, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(2, 1, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(2, 1, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(2, 2, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(2, 2, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(2, 2, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(2, 2, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(2, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(2, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(2, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(2, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 1, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(3, 1, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 1, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 1, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 2, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(3, 2, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 2, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 2, 3), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}, False),
        NP.Info(NP.Ident(3, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}, False),
        NP.Info(NP.Ident(3, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}, False)
    ]
    mesh = NP.Mesh(IpVersion.v1, dma_event, dma_conf, NP.Info.hrc(False), nps)
    return Device(AKD1500_v1, mesh)


def TwoNodesIPv2():
    """Returns a 2-node virtual device for FPGA v2.

    Returns:
        :obj:`Device`: a virtual device.

    """
    dma_event = NP.Ident(1, 1, 0)
    dma_conf = NP.Ident(1, 1, 1)
    skipdmas_num_channels = 2
    skip_dmas = [
        NP.Info(
            NP.Ident(1, 1, 3, skipdmas_num_channels),
            {NP.Type.SKIP_DMA_STORE, NP.Type.SKIP_DMA_LOAD}, False)]
    nps = [
        NP.Info(NP.Ident(1, 2, 0), {NP.Type.CNP1, NP.Type.FNP2}, True),
        NP.Info(NP.Ident(1, 2, 1), {NP.Type.CNP1}, True),
        NP.Info(NP.Ident(1, 2, 2), {NP.Type.CNP1}, True),
        NP.Info(NP.Ident(1, 2, 3), {NP.Type.CNP1}, True),
        NP.Info(NP.Ident(2, 2, 0), {NP.Type.CNP1, NP.Type.FNP3}, True),
        NP.Info(NP.Ident(2, 2, 1), {NP.Type.CNP1, NP.Type.CNP2}, True),
        NP.Info(NP.Ident(2, 2, 2), {NP.Type.CNP1, NP.Type.CNP2}, True),
        NP.Info(NP.Ident(2, 2, 3), {NP.Type.CNP1, NP.Type.CNP2}, True)
    ]

    mesh = NP.Mesh(IpVersion.v2, dma_event, dma_conf, NP.Info.hrc(True), nps, skip_dmas)
    return Device(FPGA_v2, mesh)


def SixNodesIPv2():
    """Returns a 6-node virtual device for FPGA v2.

    Returns:
        :obj:`Device`: a virtual device.

    """
    dma_event = NP.Ident(1, 1, 0)
    dma_conf = NP.Ident(1, 1, 1)
    skipdmas_num_channels = 4
    skip_dmas = [
        NP.Info(
            NP.Ident(1, 1, 3, skipdmas_num_channels),
            {NP.Type.SKIP_DMA_STORE, NP.Type.SKIP_DMA_LOAD}, False)]
    nps = [
        NP.Info(NP.Ident(1, 2, 0), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.FNP2}, True),
        NP.Info(NP.Ident(1, 2, 1), {NP.Type.TNP_B, NP.Type.CNP1}, True),
        NP.Info(NP.Ident(1, 2, 2), {NP.Type.TNP_B, NP.Type.CNP1}, True),
        NP.Info(NP.Ident(1, 2, 3), {NP.Type.TNP_B, NP.Type.CNP1}, True),
        NP.Info(NP.Ident(1, 3, 0), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.CNP2}, True),
        NP.Info(NP.Ident(1, 3, 1), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.CNP2}, True),
        NP.Info(NP.Ident(1, 3, 2), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.CNP2}, True),
        NP.Info(NP.Ident(1, 3, 3), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.CNP2}, True),
        NP.Info(NP.Ident(2, 2, 0), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.FNP3}, True),
        NP.Info(NP.Ident(2, 2, 1), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.CNP2}, True),
        NP.Info(NP.Ident(2, 2, 2), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.CNP2}, True),
        NP.Info(NP.Ident(2, 2, 3), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.CNP2}, True),
        NP.Info(NP.Ident(2, 3, 0), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.CNP2}, True),
        NP.Info(NP.Ident(2, 3, 1), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.CNP2}, True),
        NP.Info(NP.Ident(2, 3, 2), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.CNP2}, True),
        NP.Info(NP.Ident(2, 3, 3), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.CNP2}, True),
        NP.Info(NP.Ident(3, 2, 0), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.FNP3}, True),
        NP.Info(NP.Ident(3, 2, 1), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.CNP2}, True),
        NP.Info(NP.Ident(3, 2, 2), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.CNP2}, True),
        NP.Info(NP.Ident(3, 2, 3), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.CNP2}, True),
        NP.Info(NP.Ident(3, 3, 0), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.CNP2}, True),
        NP.Info(NP.Ident(3, 3, 1), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.CNP2}, True),
        NP.Info(NP.Ident(3, 3, 2), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.CNP2}, True),
        NP.Info(NP.Ident(3, 3, 3), {NP.Type.TNP_B, NP.Type.CNP1, NP.Type.CNP2}, True)
    ]

    mesh = NP.Mesh(IpVersion.v2, dma_event, dma_conf, NP.Info.hrc(True), nps, skip_dmas)
    return Device(FPGA_v2, mesh)


def create_device(num_cnp_tnp,
                  num_fnp,
                  num_skip_dma_channel=0,
                  include_hrc=True,
                  sram_size=None,
                  hw_version=FPGA_v2,
                  ):
    """Creates an Akida device with the specified hardware components.

    Args:
        num_cnp_tnp (int): Number of CNP and TNP_B units (TNP_B is only available on 2.x devices).
        num_fnp (int): Number of FNP units to include. An FNP2 with external memory is added first,
            followed by FNP3 units.
        num_skip_dma_channel (int, optional): Number of skip DMA channels (only applicable for
            2.x devices). Defaults to 0.
        include_hrc (bool, optional): Whether to include the HRC. Defaults to True.
        sram_size (akida.NP.SramSize, optional): Size of shared SRAM available inside the mesh.
          Defaults to None.
        weight_memory (int, optional): Size of shared filter SRAM in bytes available inside the
            mesh for each two NPs. Defaults to None.
        hw_version (akida.HwVersion, optional): The version of the device. Defaults to FPGA_v2.

    Returns:
        akida.Device: An Akida device.
    """
    # General akida node info
    SKIP_DMA_ROW = 1
    SKIP_DMA_ID = 3
    MAX_SKIP_DMA_CHANNELS_PER_COL = 4
    NUM_NPS_PER_NODE = 4

    # Get Ip version
    ip_version = hw_version.ip_version

    # Lut is a v2 feature
    has_lut = ip_version == IpVersion.v2

    def _get_supported_hw_version(ip_version):
        if ip_version == IpVersion.v2:
            return [FPGA_v2]
        return [NSoC_v1, NSoC_v2, TwoNodesIP_v1, AKD1500_v1]

    def _compute_total_nps(num_cnp_tnp, num_fnp):
        total_nps = num_cnp_tnp + num_fnp

        # The nodes are completed with NPs of type CNP1, CNP2 (and TNP_B if hw_version = FPGA_v2)
        # if the requested NPs are not a multiple of NUM_NPS_PER_NODE.
        nps_to_add = (-total_nps) % NUM_NPS_PER_NODE
        num_cnp_tnp += nps_to_add
        total_nps += nps_to_add

        return total_nps, num_cnp_tnp

    def _compute_optimal_nps_grid_shape(total_nps):
        if total_nps == 0:
            return 0, 0
        num_nodes = total_nps / NUM_NPS_PER_NODE
        fractional_diff = (num_nodes / sqrt(num_nodes)) - (num_nodes // sqrt(num_nodes))

        # Increment columns first and then rows
        num_cols = floor(sqrt(num_nodes)) + ceil(fractional_diff)
        num_rows = floor(sqrt(num_nodes)) + round(fractional_diff)

        return num_rows, num_cols

    def _make_skip_dmas(num_cols, num_skip_dma_channel):
        skip_dmas = []

        if hw_version != FPGA_v2 and num_skip_dma_channel > 0:
            raise ValueError(f"Skip DMAs are only supported on v2 devices (hw_version=FPGA_v2). "
                             f"Current hardware version: {hw_version}.")

        if num_skip_dma_channel == 0:
            return skip_dmas

        # Distribute Skip DMAs accross columns as much as possible
        # When the number of Skip DMAs exceeds the number of columns used by nps, we increase
        # the number of columns.
        current_max_skip_dma_channels = num_cols * MAX_SKIP_DMA_CHANNELS_PER_COL
        if (extra_channels := num_skip_dma_channel - current_max_skip_dma_channels) > 0:
            num_cols += ceil((extra_channels) / MAX_SKIP_DMA_CHANNELS_PER_COL)

        # Compute number of channels per skip dma
        num_channels_per_skip_dma = ceil(num_skip_dma_channel / num_cols)

        # Deduce the number of skip dmas in the device
        num_skip_dmas = min(num_skip_dma_channel, num_cols)

        for col in range(1, num_skip_dmas + 1):
            skip_dmas.append(
                NP.Info(NP.Ident(col, SKIP_DMA_ROW, SKIP_DMA_ID, num_channels_per_skip_dma),
                        {NP.Type.SKIP_DMA_STORE, NP.Type.SKIP_DMA_LOAD}, False)
            )

        return skip_dmas

    def _make_nps(num_rows, num_cols, num_cnp_tnp, num_fnp):
        # Construct NP types
        cnp_types = [NP.Type.CNP1, NP.Type.CNP2]
        fnp_types = [NP.Type.FNP2]
        # If a device with only 1 FNP is requested, the corresponding NP will only
        # have FNP installed.
        if num_fnp > 1:
            fnp_types = [NP.Type.CNP1, NP.Type.CNP2] + fnp_types
            if hw_version == FPGA_v2:
                fnp_types.insert(0, NP.Type.TNP_B)

        if hw_version == FPGA_v2:
            cnp_types.insert(0, NP.Type.TNP_B)

        nps = []
        # Starting from row 2
        for row in range(2, num_rows + 2):
            for col in range(1, num_cols + 1):
                # Now loop over nps
                for id in range(NUM_NPS_PER_NODE):
                    if num_cnp_tnp > 0:
                        nps.append(NP.Info(NP.Ident(col, row, id), cnp_types, has_lut))
                        num_cnp_tnp -= 1
                    elif num_fnp > 0:
                        nps.append(NP.Info(NP.Ident(col, row, id), fnp_types, has_lut))
                        # Change FNP2 with FNP3
                        if fnp_types[-1] == NP.Type.FNP2:
                            fnp_types[-1] = NP.Type.FNP3
                        num_fnp -= 1
        return nps

    # Check HW version
    supported_hw_version = _get_supported_hw_version(ip_version)
    if hw_version not in supported_hw_version:
        raise ValueError(f"Invalid HW version '{hw_version}'. "
                         f"Expected one of: {supported_hw_version}.")

    # Compute total nps and construct the optimal grid for NPs
    # The mesh should be as square as possible
    total_nps, num_cnp_tnp = _compute_total_nps(num_cnp_tnp, num_fnp)
    num_rows, num_cols = _compute_optimal_nps_grid_shape(total_nps)
    if total_nps == 0 and not include_hrc:
        raise ValueError("It is not possible to create a completely empty device. "
                         f"num_cnp_tnp + num_fnp ({total_nps}) must be greater than zero or "
                         "HRC must be included).")

    # Make DMA event and conf
    dma_event = NP.Ident(1, 1, 0)
    dma_conf = NP.Ident(1, 1, 1)

    # Make SkipDMAs
    skip_dmas = _make_skip_dmas(num_cols, num_skip_dma_channel)

    # Make NPs
    nps = _make_nps(num_rows, num_cols, num_cnp_tnp, num_fnp)

    # Default SRAM size if not specified
    if sram_size is None:
        sram_size = NP.SramSize_v2 if ip_version == IpVersion.v2 else NP.SramSize_v1

    # Make the mesh
    hrc = NP.Info.hrc(has_lut) if include_hrc else None
    mesh = NP.Mesh(ip_version, dma_event, dma_conf, hrc, nps, skip_dmas, sram_size)

    return Device(hw_version, mesh)


def compute_minimal_memory(model):
    """Compute the minimal memory required for inputs and weights on the device.

    Args:
        model (akida.Model): an Akida model.

    Returns:
        int, int: minimal input_buffer memory and minimal weight memory in bytes.
    """
    # Check that model is mapped
    assert any([s.program is not None for s in model.sequences]), "Model needs to be mapped"

    minimal_input_buffer_memory = 0
    minimal_weight_memory = 0

    for layer in model.layers:
        if not layer.mapping:
            continue

        for np in layer.mapping.nps:
            np_weight_size = np.mem_info.weight_size
            if np.type == NP.Type.FNP3:
                # FNP weight SRAM in 32-bit words, 48 bits are used per 50-bit word.
                # We need to convert first to 32 bit by dividing by 4 to compute weight size
                np_weight_size /= 4

                # Compute weight size and convert back to bytes by multiplying by 4
                np_weight_size = ceil(50 * np_weight_size / 48) * 4

            minimal_input_buffer_memory = max(minimal_input_buffer_memory, np.mem_info.input_size)
            minimal_weight_memory = max(minimal_weight_memory, np_weight_size)

    return minimal_input_buffer_memory, minimal_weight_memory


def _get_outbounds(layer, layers):
    return [ly for ly in layers if layer in ly.inbounds]


def _model_generator(layers):
    # Scroll through a list of layers, returning a pair of consecutive layers. Notes:
    # - one of the two branches must not have nodes (not implemented yet)
    # - merge layer is performed in the following NP, so we take their inbounds
    queue = [layers[-1]]
    while len(queue) > 0:
        t_layer = queue.pop(0)
        inbounds = t_layer.inbounds
        # Skip a layer if it is a merge one.
        if len(inbounds) == 1 and len(inbounds[0].inbounds) > 1:
            inbounds = inbounds[0].inbounds
        # Check inbounds constraints.
        if len(inbounds) > 1:
            # In case of multiple branches, one of them must not contain layers.
            # This translates to some inbound having multiple outbounds.
            new_inbounds = []
            for ly in inbounds:
                # Remove the branch with empty layers
                if len(_get_outbounds(ly, layers)) == 1:
                    new_inbounds.append(ly)
            if len(new_inbounds) != 1:
                raise NotImplementedError(f"{t_layer} has multiple inbounds, "
                                          "but there is no empty branch.")
            # Remove the inbounds that are not empty branches.
            inbounds = new_inbounds

        # Yield the pair (inbound, target_layer) if both have been mapped
        # Or if taget_layer is mapped and the inbound is an InputData layer.
        if len(inbounds) == 1 and t_layer.mapping is not None:
            if inbounds[0].parameters.layer_type == LayerType.InputData or \
                    inbounds[0].mapping is not None:
                yield LayerSequence((inbounds[0], t_layer))
                # Then, update the queue with the inbound layer.
                queue.append(inbounds[0])


def _get_initial_skip_dma_channels(model):
    # The initial number of skip DMAs is len(btc) + len(skips)
    SKIP_LAYER_TYPES = [LayerType.Add, LayerType.Concatenate]
    BTC_LAYER_TYPES = [LayerType.BufferTempConv, LayerType.DepthwiseBufferTempConv]
    skip_dma_channels = 0
    for ly in model.layers:
        if ly.parameters.layer_type in SKIP_LAYER_TYPES + BTC_LAYER_TYPES:
            skip_dma_channels += 1
    return skip_dma_channels


def _get_initial_number_of_fnp(model):
    # The initial number of FNP is len(dense), since they are not split
    FNP_LAYER_TYPES = [LayerType.Dense1D]
    nb_fnp = 0
    for ly in model.layers:
        if ly.parameters.layer_type in FNP_LAYER_TYPES:
            nb_fnp += 1
    return nb_fnp


def _get_np_components(model_or_pass, np_types=None):
    total_nps = []
    for layer in model_or_pass.layers:
        if hasattr(layer.mapping, 'nps'):
            for np in layer.mapping.nps:
                if np_types is None or np.type in np_types:
                    total_nps.append(np)
        if hasattr(layer.mapping, 'skipdma_loads'):
            for np in layer.mapping.skipdma_loads:
                if np_types is None or np.type in np_types:
                    total_nps.append(np)
        if hasattr(layer.mapping, 'skipdma_stores'):
            for np in layer.mapping.skipdma_stores:
                if np_types is None or np.type in np_types:
                    total_nps.append(np)
    return total_nps


def _compute_skip_dma_channels(model_or_pass):
    # Compute the number of skip DMA channels as max(len(SKIP_DMA_STORE), len(SKIP_DMA_LOAD))
    skip_dma_load = _get_np_components(model_or_pass, (NP.SKIP_DMA_LOAD,))
    skip_dma_store = _get_np_components(model_or_pass, (NP.SKIP_DMA_STORE,))
    return max(len(skip_dma_load), len(skip_dma_store))


def _compute_number_of_cnp_tnp(model_or_pass):
    # Compute the number of CNP/TNP-B.
    CNP_TNP_B_TYPES = (NP.CNP1, NP.CNP2, NP.TNP_B)
    total_cnps = _get_np_components(model_or_pass, CNP_TNP_B_TYPES)
    return len(total_cnps)


def _compute_number_of_fnp(model_or_pass):
    # Compute the number of FNP.
    FNP_TYPES = (NP.FNP2, NP.FNP3)
    total_fnps = _get_np_components(model_or_pass, FNP_TYPES)
    return len(total_fnps)


def compute_min_device(model,
                       enable_hwpr=False,
                       sram_size=None,
                       minimal_memory=False,
                       initial_num_nodes=36):
    """Builds the Akida virtual device that can fit the model entirely
    with or without reconfiguration.

    Args:
        model (akida.Model): the model used to determine the device.
        enable_hwpr (bool, optional): if True, the device is computed assuming
            partial reconfiguration. Defaults to False.
        sram_size (NP.SramSize, optional): Size of shared SRAM available inside the mesh.
            Ignored when `minimal_memory` is True. Defaults to None.
        minimal_memory (bool, optional): if True, computes and sets the minimal required
            inputs and weights memory for the device. Defaults to False.
        initial_num_nodes (int, optional): the initial number of nodes with which to compute
            the base device. Defaults to 36.

    Returns:
        akida.Device: the computed device
    """
    if not isinstance(model, Model):
        raise TypeError(f"Expected model to be an {Model}, got {type(model)}.")
    NUM_NPS_PER_NODE = 4
    if model.ip_version != IpVersion.v2:
        raise ValueError("Only IpVersion.v2 models are supported. "
                         f"Current model version={model.ip_version}")

    # Create a copy of the model to avoid modifying the original one.
    model = Model(layers=model.layers)

    # Compute a base device with which to compute the next parameters.
    params = {"num_skip_dma_channel": _get_initial_skip_dma_channels(model),
              "num_fnp": _get_initial_number_of_fnp(model),
              "sram_size": sram_size}

    params["num_cnp_tnp"] = NUM_NPS_PER_NODE * initial_num_nodes - params["num_fnp"]
    if params["num_cnp_tnp"] < 0:
        raise ValueError("Impossible to compute base device: "
                         f"the number of initial nodes ({initial_num_nodes}) is not enough.")
    device = create_device(**params)

    # Map model with the default parameters.
    model.map(device, mode=MapMode.Minimal, hw_only=True)

    # Now that the model has been mapped onto the base device,
    # we can compute the parameters to build the required device.
    if enable_hwpr:
        params["num_cnp_tnp"] = params["num_fnp"] = 0
        for layer_seq in _model_generator(model.layers):
            # Compute the number of CNP/FNP needed to map the model in multiple passes,
            # as the larger sum of 2 consecutive layers.
            params["num_cnp_tnp"] = max(params["num_cnp_tnp"],
                                        _compute_number_of_cnp_tnp(layer_seq))
            params["num_fnp"] = max(params["num_fnp"], _compute_number_of_fnp(layer_seq))
        # To compute the minimum number of skip DMA channels needed when partial reconfiguration
        # is allowed, we iterate the device until we find a valid one.
        for num_skip_dma_channel in range(1, params.pop("num_skip_dma_channel") + 1):
            try:
                device = create_device(num_skip_dma_channel=num_skip_dma_channel, **params)
                model.map(device, mode=MapMode.Minimal, hw_only=True)
                params["num_skip_dma_channel"] = num_skip_dma_channel
                break
            except Exception:
                continue
    else:
        params["num_cnp_tnp"] = _compute_number_of_cnp_tnp(model)
        params["num_fnp"] = _compute_number_of_fnp(model)
        params["num_skip_dma_channel"] = _compute_skip_dma_channels(model)

    if minimal_memory:
        if sram_size is not None:
            warnings.warn(
                "The 'sram_size' argument will be ignored because 'minimal_memory' is set to True. "
                "The required memory will be computed automatically. Continuing execution"
            )
        params["sram_size"] = NP.SramSize(*compute_minimal_memory(model))

    # Create a virtual device with the requirements.
    device = create_device(**params)

    # Sanity check: map model on device.
    try:
        model.map(device, mode=MapMode.Minimal, hw_only=True)
    except Exception as e:
        raise RuntimeError("It was not possible to find a device for this model. "
                           f"Reason:\n{str(e)}")
    return device


def compute_common_device(ak_models):
    """Computes a common Akida device that can run all the given models.
    Ensures all models were mapped.

    Args:
        ak_models (List[akida.Model]): A list of Akida models whose hardware
            requirements will be combined.

    Returns:
        akida.Device: A new device that can map all the given models.
    """
    if not ak_models:
        raise ValueError("The list of Akida models cannot be empty.")
    if wrong_model_types := [type(m) for m in ak_models if not isinstance(m, Model)]:
        raise TypeError(f"Devices cannot be computed for models of type {wrong_model_types}.")
    if any(model.device is None for model in ak_models):
        raise ValueError("All models must be mapped on a device.")

    # For safety, check that all models devices have the same version
    assert all(model.device.version == ak_models[0].device.version for model in ak_models), \
        "Models devices have different versions."

    include_hrc = any(model.device.mesh.hrc for model in ak_models)
    max_num_cnp_tnp = 0
    max_num_fnp = 0
    max_num_skip_dma_channel = 0
    sram_size = NP.SramSize(0, 0)

    for model in ak_models:
        # Update params
        for sequence in model.sequences:
            for pass_ in sequence.passes:
                max_num_cnp_tnp = max(max_num_cnp_tnp,
                                      _compute_number_of_cnp_tnp(pass_))
                max_num_fnp = max(max_num_fnp,
                                  _compute_number_of_fnp(pass_))
                max_num_skip_dma_channel = max(max_num_skip_dma_channel,
                                               _compute_skip_dma_channels(pass_))

        # Update Sram size
        sram_size = NP.SramSize(max(sram_size.input_bytes,
                                    model.device.mesh.np_sram_size.input_bytes),
                                max(sram_size.weight_bytes,
                                    model.device.mesh.np_sram_size.weight_bytes))

    return create_device(max_num_cnp_tnp, max_num_fnp,
                         max_num_skip_dma_channel, include_hrc,
                         sram_size, ak_models[0].device.version)
