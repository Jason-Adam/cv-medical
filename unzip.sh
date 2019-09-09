#!/bin/sh
for zip in *.zip
do
    unzip -d "scans/" $zip
done
