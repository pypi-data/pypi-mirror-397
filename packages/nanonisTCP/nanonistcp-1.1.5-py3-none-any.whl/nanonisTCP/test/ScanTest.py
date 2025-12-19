# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 12:24:35 2022

@author: Julian Ceddia
"""
"""
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!WARNING: RUNNING run_test() WILL CHANGE SETTINGS IN NANONIS. RUN IT ON A SIM!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""

from nanonisTCP import nanonisTCP
from nanonisTCP.Scan import Scan
import traceback

def run_test(TCP_IP='127.0.0.1', TCP_PORT=6501, debug=False, version=13520):

    NTCP = nanonisTCP(TCP_IP, TCP_PORT, version=version)
    scan = Scan(NTCP)

    try:
        # ---------------------------------------------------------------
        # PropsSet / PropsGet — version-aware
        # ---------------------------------------------------------------

        if version > 14000:
            scan.PropsSet(
                continuous_scan=1,
                bouncy_scan=1,
                autosave=1,
                series_name="TEST_SERIES",
                comment="Scan test comment",
                modules_names=["Current", "Bias"],
                autopaste="all"
            )
        else:
            # Old protocol → no modules_names or autopaste
            scan.PropsSet(
                continuous_scan=1,
                bouncy_scan=1,
                autosave=1,
                series_name="TEST_SERIES",
                comment="Scan test comment"
            )

        result = scan.PropsGet()

        if version > 14000:
            (
                continuous_scan,
                bouncy_scan,
                autosave,
                series_name,
                comment,
                modules_names,
                autopaste
            ) = result

            if debug:
                print("PropsGet (new protocol):")
                print("continuous_scan:", continuous_scan)
                print("bouncy_scan:", bouncy_scan)
                print("autosave:", autosave)
                print("series_name:", series_name)
                print("comment:", comment)
                print("modules_names:", modules_names)
                print("autopaste:", autopaste)
                print("----------------------------------------------------------")

        else:
            (
                continuous_scan,
                bouncy_scan,
                autosave,
                series_name,
                comment,
                _,  # modules_names placeholder
                _   # autopaste placeholder
            ) = result

            if debug:
                print("PropsGet (old protocol):")
                print("continuous_scan:", continuous_scan)
                print("bouncy_scan:", bouncy_scan)
                print("autosave:", autosave)
                print("series_name:", series_name)
                print("comment:", comment)
                print("----------------------------------------------------------")

        # ---------------------------------------------------------------
        # Start scan + WaitEndOfScan
        # ---------------------------------------------------------------
        scan.Start()

        timeout, file_path_size, file_path = scan.WaitEndOfScan(timeout=5000)

        if debug:
            print("WaitEndOfScan:")
            print("timeout:", timeout)
            print("file_path:", file_path)
            print("----------------------------------------------------------")

        # ---------------------------------------------------------------
        # FrameDataGrab — unchanged protocol
        # ---------------------------------------------------------------
        try:
            channel_name, data, direction = scan.FrameDataGrab(0, 1)
            if debug:
                print("FrameDataGrab channel:", channel_name)
                print("FrameDataGrab direction:", direction)
        except Exception as e:
            print("Warning in FrameDataGrab:", e)

        # ---------------------------------------------------------------
        # BufferGet — unchanged
        # ---------------------------------------------------------------
        try:
            num_channels, channel_indexes, pixels, lines = scan.BufferGet()
            if debug:
                print("BufferGet:")
                print("num_channels:", num_channels)
                print("channel_indexes:", channel_indexes)
                print("pixels:", pixels)
                print("lines:", lines)
                print("------------------------------------------------------")
        except Exception as e:
            print("Warning in BufferGet:", e)

        # ---------------------------------------------------------------
        # Stop scan
        # ---------------------------------------------------------------
        scan.Stop()

    except:
        NTCP.close_connection()
        return traceback.format_exc()

    NTCP.close_connection()
    return "success"