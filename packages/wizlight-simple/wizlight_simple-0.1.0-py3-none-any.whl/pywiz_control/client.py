import asyncio
import json
import logging

logger = logging.getLogger(__name__)

class WizProtocol(asyncio.DatagramProtocol):
    """Protokoll für die aktive Anfrage-Antwort-Kommunikation (UDP)."""
    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost
        self.transport = None
        self.response = None

    def connection_made(self, transport):
        self.transport = transport
        self.transport.sendto(self.message.encode())

    def datagram_received(self, data, addr):
        self.response = data.decode()
        self.transport.close()

    def error_received(self, exc):
        logger.error(f"UDP Fehler bei Anfrage: {exc}")

    def connection_lost(self, exc):
        if not self.on_con_lost.done():
            self.on_con_lost.set_result(True)

class WizPushListener(asyncio.DatagramProtocol):
    """Protokoll zum Empfangen spontaner Status-Updates (syncPilot)."""
    def __init__(self, callback):
        self.callback = callback

    def datagram_received(self, data, addr):
        try:
            msg = json.loads(data.decode())
            # WiZ sendet 'syncPilot' bei manuellen Änderungen am Gerät
            if msg.get("method") == "syncPilot":
                ip = addr[0]
                params = msg.get("params", {})
                # Falls ein Callback registriert ist, führe ihn aus
                if asyncio.iscoroutinefunction(self.callback):
                    asyncio.create_task(self.callback(ip, params))
                else:
                    self.callback(ip, params)
        except Exception as e:
            logger.debug(f"Ungültiges Push-Paket von {addr}: {e}")

class SimpleWizDevice:
    def __init__(self, ip: str, mac: str = None, source: str = None):
        self.ip = ip
        self.mac = mac
        self.source = source
        self.port = 38899

    async def _send(self, method: str, params: dict = None, timeout: float = 2.0):
        """Kern-Methode für asynchrone Befehle."""
        if params is None: params = {}
        payload = json.dumps({"method": method, "params": params})

        loop = asyncio.get_running_loop()
        on_con_lost = loop.create_future()

        try:
            transport, protocol = await asyncio.wait_for(
                loop.create_datagram_endpoint(
                    lambda: WizProtocol(payload, on_con_lost),
                    remote_addr=(self.ip, self.port)
                ),
                timeout=timeout
            )
            await on_con_lost
            return json.loads(protocol.response) if protocol.response else None
        except Exception as e:
            logger.debug(f"Kommunikationsfehler mit {self.ip}: {e}")
            return None

    # --- STEUERUNG ---
    async def turn_on(self):
        return await self._send("setPilot", {"state": True})

    async def turn_off(self):
        return await self._send("setPilot", {"state": False})

    async def set_brightness(self, level: int):
        """Helligkeit von 10 bis 100 setzen."""
        level = max(10, min(100, level))
        return await self._send("setPilot", {"dimming": level})

    # --- ABFRAGEN ---
    async def get_status(self):
        """Fragt den aktuellen Status aktiv ab."""
        res = await self._send("getPilot")
        return res.get("result", {}) if res else {}

    async def get_power(self) -> float:
        """Gibt den aktuellen Verbrauch in Watt zurück."""
        status = await self.get_status()
        return status.get("power", 0) / 1000

    # --- STATISCHE METHODE FÜR DEN LISTENER ---
    @staticmethod
    async def start_push_listener(callback):
        """
        Startet einen globalen UDP-Server, der auf Status-Updates wartet.
        :param callback: Eine Funktion mit Signatur (ip, params_dict)
        """
        loop = asyncio.get_running_loop()
        try:
            transport, protocol = await loop.create_datagram_endpoint(
                lambda: WizPushListener(callback),
                local_addr=('0.0.0.0', 38899)
            )
            logger.info("WiZ Push-Listener auf Port 38899 gestartet.")
            return transport
        except OSError as e:
            logger.error(f"Listener konnte nicht starten (Port belegt?): {e}")
            return None
