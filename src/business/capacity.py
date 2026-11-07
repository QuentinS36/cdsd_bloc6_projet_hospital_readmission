def calculate_avg_occupancy_rate(avg_inpatient, capacity):
    """Calculate hospital bed occupancy rate."""

    if capacity <= 0:
        raise ValueError("Capacity must be greater than zero.")
    else:
        avg_occupancy_rate = avg_inpatient / capacity * 100

    return avg_occupancy_rate


def calculate_capacity_thresholds(capacity, tolerance_range):
    """Calculate lower and upper capacity thresholds."""

    tolerance = tolerance_range / 100

    lower_threshold = capacity * (1 - tolerance)
    upper_threshold = capacity * (1 + tolerance)

    return lower_threshold, upper_threshold


def calculate_bed_need(stock, capacity):
    """Calculate the additional number of beds required."""

    return max(stock - capacity, 0)


def calculate_capacity_days(
        df_inpatient, 
        lower_threshold,
        upper_threshold,
):
    overcapacity_days = (
        df_inpatient["final_inpatient_census"] > upper_threshold
    ).sum()

    undercapacity_days = (
        df_inpatient["final_inpatient_census"] < lower_threshold
    ).sum()

    return overcapacity_days, undercapacity_days