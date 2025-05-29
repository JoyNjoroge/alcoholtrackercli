def convert_to_oz(amount, unit):
    """Convert different units to ounces"""
    unit = unit.lower()
    if unit == "ml":
        return amount * 0.033814
    elif unit == "l":
        return amount * 33.814
    elif unit == "oz":
        return amount
    else:
        raise ValueError(f"Unknown unit: {unit}")