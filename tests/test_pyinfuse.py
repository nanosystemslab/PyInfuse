"""Unit tests for Pyinfuse library."""

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import serial

from pyinfuse.pyinfuse import Chain
from pyinfuse.pyinfuse import Pump


@pytest.fixture
def mock_serial() -> MagicMock:
    """Creates a mock of the serial.Serial class."""
    with patch("serial.Serial", autospec=True) as mock_serial:
        yield mock_serial


def test_chain_init(mock_serial) -> None:
    """Test initializing the Chain class."""
    port = "/dev/ttyS0"
    chain = Chain(port=port)

    mock_serial.assert_called_once_with(
        port=port, stopbits=serial.STOPBITS_TWO, parity=serial.PARITY_NONE, timeout=2
    )
    assert chain.port == port


@pytest.fixture
def mock_chain(mock_serial) -> Chain:
    """Fixture to initialize a Chain instance with mocked serial."""
    return Chain(port="/dev/ttyS0")


def test_pump_init(mock_chain: Chain) -> None:
    """Test initializing the Pump class."""
    with patch.object(Pump, "write", MagicMock()) as mock_write, patch.object(
        Pump, "read", MagicMock(return_value="011:")
    ) as mock_read:

        pump = Pump(chain=mock_chain, address=1, name="Pump Test")

        mock_write.assert_called_once_with("VER")
        mock_read.assert_called_once_with(17)
        assert pump.name == "Pump Test"
        assert pump.address == "01"


def test_pump_write(mock_chain: Chain) -> None:
    """Test writing a command to the Pump."""
    pump = Pump(chain=mock_chain, address=1)
    pump.serialcon = MagicMock()

    pump.write("TEST")
    pump.serialcon.write.assert_called_once_with(b"01TEST\r")


def test_pump_read(mock_chain: Chain) -> None:
    """Test reading a response from the Pump."""
    pump = Pump(chain=mock_chain, address=1)
    pump.serialcon = MagicMock()
    pump.serialcon.read.return_value = b"OK"

    response = pump.read(2)
    pump.serialcon.read.assert_called_once_with(2)
    assert response == "OK"


def test_set_diameter(mock_chain: Chain) -> None:
    """Test setting the syringe diameter."""
    pump = Pump(chain=mock_chain, address=1)
    pump.serialcon = MagicMock()

    pump.setdiameter("15.00")
    pump.serialcon.write.assert_called_once_with(b"01diameter 15.00\r")


def test_set_flowrate(mock_chain: Chain) -> None:
    """Test setting the flow rate of the Pump."""
    pump = Pump(chain=mock_chain, address=1)
    pump.serialcon = MagicMock()

    pump.setflowrate("50.0", "ul/min")
    pump.serialcon.write.assert_called_once_with(b"01irate 50.0 ul/min\r")


def test_infuse(mock_chain: Chain) -> None:
    """Test starting the infusion."""
    pump = Pump(chain=mock_chain, address=1)
    pump.serialcon = MagicMock()

    pump.infuse()
    pump.serialcon.write.assert_called_once_with(b"01run\r")


def test_withdraw(mock_chain: Chain) -> None:
    """Test starting the withdrawal."""
    pump = Pump(chain=mock_chain, address=1)
    pump.serialcon = MagicMock()
    pump.serialcon.read.side_effect = [b":", b"<"]

    pump.withdraw()
    pump.serialcon.write.assert_any_call(b"01REV\r")
    pump.serialcon.write.assert_any_call(b"01RUN\r")


def test_stop(mock_chain: Chain) -> None:
    """Test stopping the Pump."""
    pump = Pump(chain=mock_chain, address=1)
    pump.serialcon = MagicMock()

    pump.stop()
    pump.serialcon.write.assert_called_once_with(b"01STP\r")


def test_set_target_volume(mock_chain: Chain) -> None:
    """Test setting the target volume for the Pump."""
    pump = Pump(chain=mock_chain, address=1)
    pump.serialcon = MagicMock()

    pump.settargetvolume("1.0", "ml")
    pump.serialcon.write.assert_called_once_with(b"01tvolume 1.0 ml\r")


def test_set_target_time(mock_chain: Chain) -> None:
    """Test setting the target time for the Pump."""
    pump = Pump(chain=mock_chain, address=1)
    pump.serialcon = MagicMock()

    pump.settargettime(120)
    pump.serialcon.write.assert_called_once_with(b"01ttime 120\r")
