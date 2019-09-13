import pytest
import iio_scanner
import iio
import tools

dev_checked = False
found_dev = False
board_config = []

# Create board configuration
board_name = "daq2"
devices = ["axi-ad9680-hpc","axi-ad9144-hpc","ad9523-1","ad7291"]
devices_us = devices+["ams"]
boot_bin = "BOOT.BIN"


def check_dev(name):
    global dev_checked
    global found_dev
    if not dev_checked:
        found_dev, board = iio_scanner.find_device(name)
        if found_dev:
            global URI
            global devices_us
            global devices
            global boot_bin
            global board_name
            global board_config
            URI = board.uri
            board_config = tools.config(board_name, \
                boot_bin, board.uri[3:], devices, devices_us)
        dev_checked = True
    return found_dev


@pytest.mark.skipif(not check_dev("daq2"), reason="PlutoSDR not connected")
@pytest.mark.dependency()
def test_board_available():
    ctx = iio.Context("ip:"+board_config.board_ip)
    found = 0
    for dev in ctx.devices:
        if dev.name in board_config.devices:
            found = found + 1
    if found!=len(board_config.devices):
        assert False

@pytest.mark.dependency(depends=["test_board_available"])
def test_boot_bin_update():
    # Copy BOOT.BIN to board
    board_config.update_boot_bin()

@pytest.mark.dependency(depends=["test_boot_bin_update"])
def test_board_reboot():
    # Start serial logging
    board_config.serial_start()
    # Reboot board
    r = board_config.reboot_board()
    # Save serial data
    board_config.serial_done()
    assert r

@pytest.mark.dependency(depends=["test_board_reboot"])
def test_iio_devices_appear():
    time.sleep(10) # Give time for iiod to start
    ctx = iio.Context("ip:"+board_config.board_ip)
    found = 0
    for dev in ctx.devices:
        if dev.name in board_config.devices:
            found = found + 1
    if found!=len(board_config.devices):
        assert False
