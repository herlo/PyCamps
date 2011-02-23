#!/bin/bash

# Thanks to Scott Marshall for this script
# clean up device mapper before removing an lv snapshot

## First, force a flush of disc buffers
sync

##
if [ $EUID -ne 0 ]; then
    echo "$0 must be run as root"
    exit 1
fi
if [ $# -lt 1 ]; then
    echo "Usage $0 <lv_to_remove>"
    exit 1
fi

LV_SNAP=$1

## Now we dismount the snapshot file system copies
printf "Unmounting snapshot filesystems...\t"
umount ${LV_SNAP}
printf "Done!\n"

## Pause for a bit so the file systems can complete their dismount
sleep 5 

## Flush any buffers to disc again - just to be sure
sync

## Wait another 10 seconds for everything to stabilise
sleep 5

### I have to use "dmsetup remove" to deactivate the snapshots first
dmsetup remove ${LV_SNAP}
dmsetup remove ${LV_SNAP}-cow
## for some reason, the copy-on-write devices aren't cleaned up auto-magically
## so I have to remove them auto-manually.

## Okay - now we can remove the snapshot logical volumes
lvremove -f ${LV_SNAP}

