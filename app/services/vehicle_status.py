VEHICLE_STATUS_CHART_COLORS = {
    "status-available": "#10b981",
    "status-reserved": "#f59e0b",
    "status-sold": "#f43f5e",
    "status-neutral": "#64748b",
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
