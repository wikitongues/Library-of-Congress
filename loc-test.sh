#!/bin/bash
#
# The loc-test script makes a dummy Oral History folder to test scripting with.
# Sample Oral History:
# Edgar_20180728_gwr.jpg
# Edgar_20180728_gwr.mp4
# readme.txt
# raws/
#   Premier Project/
#     Adobe Premiere Pro Audio Previews/
#       Edgar_20180728_gwr.PRV/
#         Peak Files/
#           b922c631-0361-4fdc-a8b2-6fd7c7c9d154+ab00e26f-28d9-653a-ebf7-6dee00000049 48000.pek
#         b922c631-0361-4fdc-a8b2-6fd7c7c9d154+ab00e26f-28d9-653a-ebf7-6dee00000049 48000.cfa
#     Adobe Premiere Pro Captured Audio/
#       Edgar_20180728_gwr/
#     Edgar_20180728_gwr.prproj
#   footage/
#     audio/
#       edgar_lugwere Audio Extracted.pkf
#       edgar_lugwere Audio Extracted.wav
#       edgar_lugwere.aiff
#     captions/
#     clips/
#       MVI_1728.MOV
#       MVI_1728.THM
#     converted/
#       MVI_1728.mov
#   thumbnail/
#       Screen Shot 2018-09-17 at 8.22.30 PM.png

today=`date +"%Y%m%d"`
name=`whoami`
l=`date | md5`
l=${l//[[:digit:]]/}
language=`echo $l | cut -c1-3`
filename="${name}_${today}_${language}"
mkdir ${filename}
cd ${filename}
echo "New directory created: ${filename}"
printf "Location: " && pwd
touch ${filename}.jpg ${filename}.mp4 readme.txt
mkdir raws
cd raws
  mkdir Premier\ Project footage thumbnail
  cd Premier\ Project && mkdir Adobe\ Premiere\ Pro\ Audio\ Previews Adobe\ Premiere\ Pro\ Captured\ Audio && touch ${filename}.prproj && cd ..
  cd footage && mkdir audio captions clips converted
    cd audio && touch ${name}.pkf ${name}.wav ${name}.aiff && cd ..
    cd captions && touch ${name}.srt && cd ..
    cd clips && touch ${name}.MOV ${name}.THM && cd ..
    cd converted && touch ${name}.mov && cd ..
  cd ..
  cd thumbnail && touch thumbnail.png && cd ..

cd ..
# cd .. && loc-prepare $filename
echo "Next, run loc-prepare ${filename} to create a copy of the desired oral history folder from Seed_Bank parent directory to LOC_PreRelease directory."