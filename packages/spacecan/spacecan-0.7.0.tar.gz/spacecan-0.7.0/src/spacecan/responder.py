import json

from .primitives.can_frame import (
    FULL_MASK,
    ID_HEARTBEAT,
    ID_REP,
    ID_REQ,
    ID_SCET,
    ID_SYNC,
    ID_UTC,
    CanFrame,
)
from .primitives.heartbeat import HeartbeatConsumer
from .primitives.network import Network
from .primitives.packet import PacketAssembler

DEFAULT_HEARTBEAT_PERIOD = 0.5
DEFAULT_MAX_MISS_HEARTBEAT = 3
DEFAULT_MAX_BUS_SWITCH = False
DEFAULT_USE_PACKETS = False


class Responder:
    def __init__(
        self,
        interface,
        channel_a,
        channel_b,
        node_id,
        heartbeat_period=DEFAULT_HEARTBEAT_PERIOD,
        max_miss_heartbeat=DEFAULT_MAX_MISS_HEARTBEAT,
        max_bus_switch=DEFAULT_MAX_BUS_SWITCH,
        use_packets=DEFAULT_USE_PACKETS,
    ):
        if node_id < 1 or node_id > 127:
            raise ValueError("node id must be in range 1..127")
        self.node_id = node_id
        self.interface = interface
        self.channel_a = channel_a
        self.channel_b = channel_b
        self.heartbeat_period = heartbeat_period
        self.max_miss_heartbeat = max_miss_heartbeat
        self.max_bus_switch = max_bus_switch
        self.use_packets = use_packets

        self.network = None
        self.heartbeat = HeartbeatConsumer(self) if heartbeat_period else None

        self.packet_assembler = PacketAssembler(self) if use_packets else None

    @classmethod
    def from_file(cls, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            config = json.load(f)
        return cls.from_json(config)

    @classmethod
    def from_json(cls, config):
        minimum_config = {"interface", "channel_a", "channel_b", "node_id"}
        if not minimum_config <= set(config):
            raise ValueError(
                f"Missing configuration for {minimum_config - set(config)}"
            )
        return cls(
            interface=config.get("interface"),
            channel_a=config.get("channel_a"),
            channel_b=config.get("channel_b"),
            node_id=config.get("node_id"),
            heartbeat_period=config.get("heartbeat_period", DEFAULT_HEARTBEAT_PERIOD),
            max_miss_heartbeat=config.get(
                "max_miss_heartbeat", DEFAULT_MAX_MISS_HEARTBEAT
            ),
            max_bus_switch=config.get("max_bus_switch", DEFAULT_MAX_BUS_SWITCH),
            use_packets=config.get("use_packets", DEFAULT_USE_PACKETS),
        )

    def connect(self):
        if self.interface == "socketcan":
            from .transport.socketcan import SocketCanBus

            bus_a = SocketCanBus(self, channel=self.channel_a)
            bus_b = SocketCanBus(self, channel=self.channel_b)

        elif self.interface == "gs_usb":
            from .transport.gs_usb import GsUsbBus

            bus_a = GsUsbBus(self, channel=self.channel_a)
            bus_b = GsUsbBus(self, channel=self.channel_b)

        else:
            raise NotImplementedError

            # receive sync, heartbeat, and telecommands from controller node
        filters = [
            {"can_id": ID_HEARTBEAT, "can_mask": FULL_MASK},
            {"can_id": ID_SYNC, "can_mask": FULL_MASK},
            {"can_id": ID_SCET, "can_mask": FULL_MASK},
            {"can_id": ID_UTC, "can_mask": FULL_MASK},
            {"can_id": ID_REQ + self.node_id, "can_mask": FULL_MASK},
        ]
        bus_a.set_filters(filters)
        bus_b.set_filters(filters)
        self.network = Network(self, self.node_id, bus_a, bus_b)

    def disconnect(self):
        self.network.bus_a.disconnect()
        self.network.bus_b.disconnect()

    def start(self):
        self.network.start()
        if self.heartbeat:
            self.heartbeat.start(
                self.heartbeat_period, self.max_miss_heartbeat, self.max_bus_switch
            )

    def stop(self):
        if self.heartbeat:
            self.heartbeat.stop()
        self.network.stop()

    def switch_bus(self):
        self.network.stop()
        if self.network.selected_bus == self.network.bus_a:
            self.network.selected_bus = self.network.bus_b
        elif self.network.selected_bus == self.network.bus_b:
            self.network.selected_bus = self.network.bus_a
        self.network.start()
        self.on_bus_switch()

    def get_active_bus(self):
        return self.network.selected_bus.channel

    def on_bus_switch(self):
        # to be overwritten
        pass

    def send_data(self, data):
        can_id = ID_REP + self.node_id
        can_frame = CanFrame(can_id, data)
        self.network.send(can_frame)

    def send_packet(self, packet):
        can_id = ID_REP + self.node_id
        for data in packet.split():
            can_frame = CanFrame(can_id, data)
            self.network.send(can_frame)

    def received_frame(self, can_frame):
        func_id = can_frame.get_func_id()
        node_id = can_frame.get_node_id()

        if func_id == ID_HEARTBEAT:
            if self.heartbeat:
                self.heartbeat.received()

        elif func_id == ID_SYNC:
            self.received_sync()

        elif func_id == ID_SCET:
            fine_time = int.from_bytes(can_frame.data[0:3])
            coarse_time = int.from_bytes(can_frame.data[3:7])
            self.received_scet(coarse_time, fine_time)

        elif func_id == ID_UTC:
            sub_ms = int.from_bytes(can_frame.data[0:2])
            ms_of_day = int.from_bytes(can_frame.data[2:6])
            day = int.from_bytes(can_frame.data[6:8])
            self.received_utc(day, ms_of_day, sub_ms)

        # responder node receives TC
        elif func_id == ID_REQ and node_id == self.node_id:
            if self.use_packets:
                # feed data into packet assembler
                packet = self.packet_assembler.process_frame(can_frame)
                # if packet is complete
                if packet:
                    self.received_packet(packet)
            else:
                self.received_data(can_frame.data)

    def received_heartbeat(self):
        # to be implemented by higher layer application
        pass

    def received_sync(self):
        # to be implemented by higher layer application
        pass

    def received_scet(self, coarse_time, fine_time):
        # to be implemented by higher layer application
        pass

    def received_utc(self, day, ms_of_day, sub_ms):
        # to be implemented by higher layer application
        pass

    def received_data(self, data):
        # to be implemented by higher layer application
        pass

    def received_packet(self, packet):
        # to be implemented by higher layer application
        pass
