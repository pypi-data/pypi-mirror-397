def psu_to_ppt(psu):
    """
    Convert Practical Salinity Units (PSU) to parts per thousand (ppt).
    Commonly treated as approximately equivalent.
    """
    return psu


def ppt_to_psu(ppt):
    """
    Convert parts per thousand (ppt) to PSU (approximate).
    """
    return ppt


def psu_to_ppm(psu):
    """
    Approximate conversion:
    PSU ~ ppt and 1 ppt = 1000 ppm.
    """
    return psu * 1000


def ppm_to_psu(ppm):
    """
    Approximate conversion from ppm to PSU.
    """
    return ppm / 1000
