#!/bin/bash

find '/mnt/d/Projects/COPOEM/MEI Materials/db phrases only/MIDIs' -maxdepth 1 -type f -exec midi2abc {} -s -o "{}.abc" \;
