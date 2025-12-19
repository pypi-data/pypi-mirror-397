from math import nan

from dataclasses import dataclass
from dataclass_wizard import YAMLWizard

@dataclass
class PduHost:

    name: str
    type: str
    IP: str                                     # pylint: disable=invalid-name
    username: str = ""
    password: str = ""
    chain_length: int = 1



@dataclass
class PduInput:

    pdu_host_name: str
    outlet: int
    in_chain: int = 0
    # not in the YAML, will be located
    # after loading
    # pdu_host: PduHost = None






@dataclass
class PduDevice:
    name: str
    inputs: list[PduInput]
    description: str = ""
    ssh_hostname: str = ""
    ssh_username: str = "root"
    # will be maintained by actions made
    status_cache: bool | None = None
    # if set to True, the device will be turned off when the testbed is idle
    auto_turn_off: bool = False
    icon_x_rank: float = nan
    icon_y_rank: float = nan
    icon_units: str = "grid"  # can be set to 'grid' or 'rank'
    location_x_grid: float = nan
    location_y_grid: float = nan
    label: str = ""





@dataclass
class InventoryPdus(YAMLWizard):

    pdu_hosts: list[PduHost]
    devices: list[PduDevice]


    @staticmethod
    def load() -> "InventoryPdus":
        the_config = Config()
        yaml_path = the_config.value('testbed', 'inventory_pdus_path')
        try:
            with open(yaml_path) as feed:
                return InventoryPdus.from_yaml(feed.read()).solve_references()
        except FileNotFoundError:
            # not all deployments have pdus
            logger.warning(f"file not found {yaml_path}")
            return InventoryPdus([], [])
        except KeyError as exc:
            print(f"something wrong in config file {yaml_path}, {exc}")
            raise


    def solve_references(self):
        """
        fill all PduInput instances with their pdu_host attribute
        """
        hosts_by_name = {pdu_host.name: pdu_host for pdu_host in self.pdu_hosts}
        for device in self.devices:
            for input_ in device.inputs:
                input_.pdu_host = hosts_by_name[input_.pdu_host_name]
        return self


    def status(self):
        """
        displays the status for all known devices
        works sequentially on all hosts so that the output is readable
        """
        print(f"we have {len(self.pdu_hosts)} PDUs and {len(self.devices)} devices. ")
        pdu_host_width = max(len(pdu_host.name) for pdu_host in self.pdu_hosts)
        type_width = max(len(pdu_host.type) for pdu_host in self.pdu_hosts)
        sep = 10 * '='

        async def status_all():
            for pdu_host in self.pdu_hosts:
                print(f"{sep} {pdu_host.name:>{pdu_host_width}} ({pdu_host.type:<{type_width}}) {sep}")
                print(f"{pdu_host.oneline()}")

                await pdu_host.probe()
        with asyncio.Runner() as runner:
            runner.run(status_all())


    def list2(self, names=None):
        """
        if no name: list all pdu hosts
        otherwise, list all pdu_hosts AND all pdu_devices
        whose name is in the list (case ignored)
        """
        if not names:
            print(f"we have {len(self.pdu_hosts)} PDUs and {len(self.devices)} devices. "
                  f"(*) means auto_turn_off")

        names = [] if names is None else [n.lower() for n in names]
        pdu_host_width = max(len(pdu_host.name) for pdu_host in self.pdu_hosts)
        type_width = max(len(pdu_host.type) for pdu_host in self.pdu_hosts)
        device_width = max(len(device.name) for device in self.devices)
        sep = 10 * '='
        indent_empty = 5 * ' '
        indent_auto = ' (*) '
        for pdu_host in self.pdu_hosts:
            # if no name was passed, list all pdu_hosts
            if names and pdu_host.name.lower() not in names:
                continue
            print(f"{sep} {pdu_host.name:>{pdu_host_width}} ({pdu_host.type:<{type_width}}) {sep}")
            print(f"{pdu_host.oneline()}")
            for device in self.devices:
                for input_ in device.inputs:
                    indent = indent_auto if device.auto_turn_off else indent_empty
                    if input_.pdu_host_name == pdu_host.name:
                        print(f"{indent}{input_.oneline()} "
                              f"→ {device.name:<{device_width}}")

        # if no name was passed, stop here
        if not names:
            return
        for device in self.devices:
            if device.name.lower() not in names:
                continue
            print(f"{sep} device {device.name:^{device_width}} {sep}")
            for input_ in device.inputs:
                indent = indent_auto if device.auto_turn_off else indent_empty
                print(f"{indent}{input_}")

    def _get_object(self, name, attribute, kind):
        l_objs = getattr(self, attribute)
        for obj in l_objs:
            if obj.name == name:
                return obj
        raise ValueError(f"unknown {kind} '{name}'")
    def get_device(self, name) -> PduDevice:
        return self._get_object(name, 'devices', 'device')
    def get_pdu_host(self, name) -> PduHost:
        return self._get_object(name, 'pdu_hosts', 'pdu_host')
