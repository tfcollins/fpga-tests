import pytest
import iio
import tools

# Create board configuration
board_name = "daq2"
username = "root"
password = "analog"
board_ip = "192.168.86.40"
devices = ["axi-ad9680-hpc","axi-ad9144-hpc","ad9523-1","ad7291"]
devices_us = devices+["ams"]
boot_bin = "BOOT.BIN"

board_config = tools.config(board_name, username, password, board_ip, devices, \
devices_us, boot_bin)

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
    ctx = iio.Context("ip:"+board_config.board_ip)
    found = 0
    for dev in ctx.devices:
        if dev.name in board_config.devices:
            found = found + 1
    if found!=len(board_config.devices):
        assert False
