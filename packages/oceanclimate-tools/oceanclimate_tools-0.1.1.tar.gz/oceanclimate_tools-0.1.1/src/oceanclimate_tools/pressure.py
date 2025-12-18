def hpa_to_pa(hpa):
    """Convert hectopascals (hPa) to pascals (Pa)."""
    return hpa * 100


def pa_to_hpa(pa):
    """Convert pascals (Pa) to hectopascals (hPa)."""
    return pa / 100


def hpa_to_atm(hpa):
    """Convert hectopascals (hPa) to atmospheres (atm)."""
    return hpa / 1013.25


def atm_to_hpa(atm):
    """Convert atmospheres (atm) to hectopascals (hPa)."""
    return atm * 1013.25


def hpa_to_psi(hpa):
    """Convert hectopascals (hPa) to psi."""
    return hpa * 0.0145037738


def psi_to_hpa(psi):
    """Convert psi to hectopascals (hPa)."""
    return psi / 0.0145037738
