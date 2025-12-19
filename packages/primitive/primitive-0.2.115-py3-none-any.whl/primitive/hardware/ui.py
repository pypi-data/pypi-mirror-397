from rich.console import Console
from rich.table import Table


def render_hardware_table(hardware_list) -> None:
    console = Console()

    table = Table(show_header=True, header_style="bold #FFA800")
    table.add_column("Organization")
    table.add_column("Name | Slug")
    table.add_column("Status")
    table.add_column("Reservation")

    for hardware in hardware_list:
        name = hardware.get("name")
        slug = hardware.get("slug")
        print_name = name
        if name != slug:
            print_name = f"{name} | {slug}"
        child_table = Table(show_header=False, header_style="bold #FFA800")
        child_table.add_column("Organization")
        child_table.add_column("Name | Slug")
        child_table.add_column("Status")
        child_table.add_column("Reservation", justify="right")

        table.add_row(
            hardware.get("organization").get("name"),
            print_name,
            hardware_status_string(hardware),
            f"{hardware.get('activeReservation').get('createdBy').get('username')} | {hardware.get('activeReservation').get('status')}"
            if hardware.get("activeReservation", None)
            else "",
        )

        if len(hardware.get("children", [])) > 0:
            for child in hardware.get("children"):
                name = child.get("name")
                slug = child.get("slug")
                print_name = name
                if name != slug:
                    print_name = f"└── {name} | {slug}"
                table.add_row(
                    hardware.get("organization").get("name"),
                    print_name,
                    hardware_status_string(hardware),
                    f"{hardware.get('activeReservation').get('createdBy').get('username')} | {hardware.get('activeReservation').get('status')}"
                    if hardware.get("activeReservation", None)
                    else "",
                )

    console.print(table)


def hardware_status_string(hardware) -> str:
    if activeReservation := hardware.get("activeReservation"):
        if activeReservation.get("status", None) == "in_progress":
            return "Reserved"
    if hardware.get("isQuarantined"):
        return "Quarantined"
    if not hardware.get("isOnline"):
        return "Offline"
    if not hardware.get("isHealthy"):
        return "Not healthy"
    if not hardware.get("isAvailable"):
        return "Not available"
    else:
        return "Available"


def render_gpu_table(gpu_list) -> None:
    console = Console()

    table = Table(show_header=True, header_style="bold #FFA800")
    table.add_column("#", justify="right")
    table.add_column("Name")
    # table.add_column("State")
    table.add_column("Total Memory (MB)")
    table.add_column("GPU BDF")
    table.add_column("Bridge BDF")
    table.add_column("Bridge Control")
    table.add_column("Register Access")
    table.add_column("Speed (Cur/Max)")
    table.add_column("Width (Cur/Max)")

    for index, gpu in enumerate(gpu_list):
        table.add_row(
            str(index),
            gpu.get("name"),
            str(gpu.get("memory_total")),
            gpu.get("gpu_bdf"),
            gpu.get("bridge_bdf"),
            gpu.get("bridge_control_state"),
            gpu.get("register_access_status"),
            gpu.get("link_speed"),
            gpu.get("link_width"),
        )

    console.print(table)
