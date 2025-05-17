on mac os:

```
brew install cdrdao
```

then create a TOC.toc

e.g. 

```

CD_DA

CD_TEXT {
  LANGUAGE 0 {
    TITLE "Your Album Title"
    PERFORMER "Docents"
  }
}


TRACK AUDIO
    FILE "track1.wav" 0
    TITLE "Your Song"
    PERFORMER "Your Band"
    ISRC ""
    FLAGS DCP
    CD_TEXT {
        TITLE "song"
        PERFORMER "artist"
    }



TRACK AUDIO
    FILE "track2.wav" 0
    TITLE "Another Song"
    PERFORMER "Your Band"
    ISRC ""
    FLAGS DCP
    CD_TEXT {
        TITLE "song"
        PERFORMER "artist"
    }


```

where ISRC is your track's ISRC code (commonly assigned by digital distribution services, like distrokid) and DCP means digital copy is permitted for the track
if you do not care about ISRC, include the flag but keep it empty

CD_TEXT embeds metadata for offline use, like in a car stereo

next, 

find your cd writer by running

```
drutil status
```

in the cli

you should see something like

```
 Vendor   Product           Rev 
 HL-DT-ST DVDRW  GS23N      SB00

           Type: CD-R                 Name: /dev/disk4
   Write Speeds: 10x, 16x, 24x
   Overwritable:   79:57:71         blocks:   359846 / 736.96MB / 702.82MiB
     Space Free:   79:57:71         blocks:   359846 / 736.96MB / 702.82MiB
     Space Used:   00:00:00         blocks:        0 /   0.00MB /   0.00MiB
    Writability: appendable, blank, overwritable
```

on mac osx. you're interested in the diskN, e.g. disk4 in this example

next, verify the device with diskutl in the cli:

```
diskutil list
```

and look for the same disk here. copy the path e.g. ```/dev/disk4``` to use in the burn command

sample:

```
sudo cdrdao write --device /dev/rdisk4 --driver generic-mmc --eject --speed 8 your_cd_text.toc
```

keep speed <= 8 to avoid artifacts in the output

note: make sure the drive isn't in use in any way - you may need to use sudo