VEHICLE_STATUS_CHART_COLORS = {
    "status-available": "#35c979",
    "status-reserved": "#f4be44",
    "status-sold": "#f46262",
    "status-neutral": "#8291a4",
}


def vehicle_status_class(description: str) -> str:
    normalized = description.strip().casefold()
    if normalized in {"disponível", "disponivel"}:
        return "status-available"
    if normalized == "reservado":
        return "status-reserved"
    if normalized == "vendido":
        return "status-sold"
    return "status-neutral"


def vehicle_status_chart_color(description: str) -> str:
    return VEHICLE_STATUS_CHART_COLORS[vehicle_status_class(description)]
