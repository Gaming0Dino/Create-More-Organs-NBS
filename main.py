import pynbs
import sys
import mcschematic
from constant import *

#def getValidInput(validInputs, prompt):
#    while True:
#        userInput = input(prompt)
#        if userInput in validInputs:
#            return userInput
#        else:
#            print(f'"{userInput}" is not a valid input. Please try again.')


def verifyFormat(song, songName):
    print("Verifying your song...")

    # check custom instruments
    print("Checking for custom instruments...")
    if len(song.instruments) > 0:
        sys.exit(f'Warning: "{songName}" contains custom instruments.')
        
    print("Song verified. Everything looks good!")

def main():
    # get song file from user
    songFile = input("Please enter the file name of your song (include the .nbs): ")
    if not songFile.endswith(".nbs"):
        sys.exit('Your song file must end with ".nbs".')

    try:
        song = pynbs.read(songFile)
        songName = songFile[:-4]
    except Exception as e:
        sys.exit(
            f'An error occurred while reading the song file "{songFile}".\nError name: {e.__class__.__name__}\nExact error (search this up for help): {e}'
        )

    verifyFormat(song, songName)
    saveName = songName.lower().replace('(', '').replace(')', '').replace(' ', '_')
    
    schem = mcschematic.MCSchematic()
    
    ToBuildNotesIns = []
    ToBuildNotesCurrentLayer = []
    CurrentLayer = 0
    
    for instrument in range(0,16):
        LeftToPlayKey = []
        LeftToPlayTick = []
        for tick, chord in song:
            for note in chord:
                if note.instrument == instrument:
                    if note.key < INSRANGE[instrument][0]:
                        shift = note.key
                        while shift < INSRANGE[instrument][0]:
                            shift = shift + 12
                        LeftToPlayKey.append(shift)
                            
                    elif note.key > INSRANGE[instrument][1]:
                        shift = note.key
                        while shift > INSRANGE[instrument][1]:
                            shift = shift - 12
                        LeftToPlayKey.append(shift)
                            
                    else:
                        LeftToPlayKey.append(note.key)
                        
                    LeftToPlayTick.append(note.tick)
        
        if len(LeftToPlayKey)>0:
            schem.setBlock((-4, CurrentLayer*3, 0), INSTRUMENTS_BLOCK[instrument])
            if INSTRUMENTS_BLOCK[instrument] == "minecraft:sand":
                schem.setBlock((-4, CurrentLayer*3-1, 0), "minecraft:tripwire")
        
        while len(LeftToPlayKey)>0:
            ToBuildKey = []
            ToBuildTick = []
            LastAddedTick = -5
            
            temp = 0
            for i in range(len(LeftToPlayKey)):
                ltpK = LeftToPlayKey[i-temp]
                if LeftToPlayTick[i-temp]>LastAddedTick+1 and LeftToPlayTick[i-temp]>LastAddedTick+2 and LeftToPlayTick[i-temp]>LastAddedTick+3 and LeftToPlayTick[i-temp]>LastAddedTick+4:
                    
                    LastAddedTick = LeftToPlayTick[i-temp]
                    
                    ToBuildKey.append(ltpK)
                    LeftToPlayKey.pop(i-temp)
                                                
                    ToBuildTick.append(LeftToPlayTick[i-temp])
                    LeftToPlayTick.pop(i-temp)
                    temp += 1
            
            XPos = 0
            YPos = 0
            CurrentTick = 0
            Direction = "west"
            
            schem.setBlock((-1, CurrentLayer*3-2, 0), "minecraft:stone")
            schem.setBlock((-2, CurrentLayer*3-2, 0), "minecraft:stone")
            schem.setBlock((-1, CurrentLayer*3-1, 0), "minecraft:repeater[delay=1,facing=west]")
            schem.setBlock((-2, CurrentLayer*3-1, 0), "create:redstone_link[facing=up,receiver=true]{FrequencyFirst:{id:\"minecraft:lever\",Count:1b},FrequencyLast:{id:\"minecraft:lever\",Count:1b}}")
            
            while len(ToBuildTick)>0:
                while CurrentTick != ToBuildTick[0]:
                    if XPos > 100 and Direction == "west" or XPos < 0 and Direction == "east":
                        Direction = "west" if Direction == "east" else "east"
                        schem.setBlock((XPos, CurrentLayer*3-2, YPos), "minecraft:stone")
                        schem.setBlock((XPos, CurrentLayer*3-2, YPos+1), "minecraft:stone")
                        schem.setBlock((XPos, CurrentLayer*3-2, YPos+2), "minecraft:stone")
                        schem.setBlock((XPos, CurrentLayer*3-1, YPos), "minecraft:redstone_wire")
                        schem.setBlock((XPos, CurrentLayer*3-1, YPos+1), "minecraft:redstone_wire")
                        schem.setBlock((XPos, CurrentLayer*3-1, YPos+2), "minecraft:redstone_wire")
                        YPos = YPos + 2
                        if Direction == "west":
                            XPos = XPos + 1
                        else:
                            XPos = XPos - 1
                        
                    if ToBuildTick[0] - CurrentTick >= 4:
                        schem.setBlock((XPos, CurrentLayer*3-1, YPos), "minecraft:repeater[delay=4,facing="+Direction+"]")
                        schem.setBlock((XPos, CurrentLayer*3-2, YPos), "minecraft:stone")
                        CurrentTick = CurrentTick + 4
                    elif ToBuildTick[0] - CurrentTick >= 3:
                        schem.setBlock((XPos, CurrentLayer*3-1, YPos), "minecraft:repeater[delay=3,facing="+Direction+"]")
                        schem.setBlock((XPos, CurrentLayer*3-2, YPos), "minecraft:stone")
                        CurrentTick = CurrentTick + 3
                    elif ToBuildTick[0] - CurrentTick >= 2:
                        schem.setBlock((XPos, CurrentLayer*3-1, YPos), "minecraft:repeater[delay=2,facing="+Direction+"]")
                        schem.setBlock((XPos, CurrentLayer*3-2, YPos), "minecraft:stone")
                        CurrentTick = CurrentTick + 2
                    else:
                        schem.setBlock((XPos, CurrentLayer*3-1, YPos), "minecraft:repeater[delay=1,facing="+Direction+"]")
                        schem.setBlock((XPos, CurrentLayer*3-2, YPos), "minecraft:stone")
                        CurrentTick = CurrentTick + 1
                    if Direction == "west":
                        XPos = XPos + 1
                    else:
                        XPos = XPos - 1
                        
                schem.setBlock((XPos, CurrentLayer*3, YPos), "create:redstone_link[facing=up]{FrequencyFirst:{id:\""+MINECRAFT_BLOCKS[ToBuildKey[0]]+"\",Count:1b},FrequencyLast:{id:\""+MINECRAFT_BLOCKS[CurrentLayer]+"\",Count:1b}}")
                schem.setBlock((XPos, CurrentLayer*3-1, YPos), "minecraft:stone")
                if Direction == "west":
                    XPos = XPos + 1
                else:
                    XPos = XPos - 1
                ToBuildTick.pop(0)
                ToBuildKey.pop(0)
            
            ToBuildNotesIns.append(instrument)
            ToBuildNotesCurrentLayer.append(CurrentLayer)
            
            CurrentLayer = CurrentLayer + 1
    
    
    NotesCount = 0
    OtherNotesCurrentLayer = []
    OtherNotesIns = []
    NoteblockXPos = 0
    isFar = False
    
    for p in range(0,len(ToBuildNotesIns)):
        if isFar == False:
            schemNoteBlock = mcschematic.MCSchematic()
        
        if INSRANGE[ToBuildNotesIns[p]][1] == 57:
            if ToBuildNotesIns[p] != 15 and ToBuildNotesIns[p] != 4:
                if isFar ==  True:
                    temp = 26
                    isFar = False
                else:
                    temp = 0
                    isFar = True
                    NoteblockXPos = NoteblockXPos + 1
                    
                for i in range(0,25):
                    schemNoteBlock.setBlock((-NoteblockXPos,-1,i + temp), "minecraft:note_block[note="+str(i)+",instrument="+INSTRUMENTS[ToBuildNotesIns[p]]+"]")
                    schemNoteBlock.setBlock((-NoteblockXPos,-2,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]])
                    schemNoteBlock.setBlock((-NoteblockXPos,-3,i + temp), "create:redstone_link[facing=down,receiver=true]{FrequencyFirst:{id:\"minecraft:"+MINECRAFT_BLOCKS[i+33]+"\",Count:1b},FrequencyLast:{id:\""+MINECRAFT_BLOCKS[ToBuildNotesCurrentLayer[p]]+"\",Count:1b}}")
                
                if isFar == False:
                    NotesCount = NotesCount + 1
                    schemNoteBlock.save('./player', saveName+"Notes"+str(NotesCount), mcschematic.Version.JE_1_19_2)
                    print('Your notes saved under "' + saveName+"Notes"+str(NotesCount) + '.schem"')
            else:
                OtherNotesCurrentLayer.append(ToBuildNotesCurrentLayer[p])
                OtherNotesIns.append(ToBuildNotesIns[p])
    if isFar == True:
        NotesCount = NotesCount + 1
        schemNoteBlock.save('./player', saveName+"Notes"+str(NotesCount), mcschematic.Version.JE_1_19_2)
        print('Your notes saved under "' + saveName+"Notes"+str(NotesCount) + '.schem"')
    
    NoteblockXPos = NoteblockXPos - 1
    isFar = False
    for p in range(0,len(OtherNotesIns)):
        if isFar == False:
            schemNoteBlock = mcschematic.MCSchematic()

        if isFar ==  True:
            temp = 26
            isFar = False
        else:
            temp = 0
            isFar = True
            NoteblockXPos = NoteblockXPos + 3
            
        for i in range(0,25):
            schemNoteBlock.setBlock((-NoteblockXPos,-1,i + temp), "minecraft:note_block[note="+str(i)+",instrument="+INSTRUMENTS[OtherNotesIns[p]]+"]")
            schemNoteBlock.setBlock((-NoteblockXPos,-2,i + temp), INSTRUMENTS_BLOCK[OtherNotesIns[p]])
            schemNoteBlock.setBlock((-NoteblockXPos-1,-1,i + temp), "minecraft:stone")
            schemNoteBlock.setBlock((-NoteblockXPos-1,-2,i + temp), "create:redstone_link[facing=down,receiver=true]{FrequencyFirst:{id:\"minecraft:"+MINECRAFT_BLOCKS[i+33]+"\",Count:1b},FrequencyLast:{id:\""+MINECRAFT_BLOCKS[OtherNotesCurrentLayer[p]]+"\",Count:1b}}")
                
        if isFar == False:
            NotesCount = NotesCount + 1
            schemNoteBlock.save('./player', saveName+"Notes"+str(NotesCount), mcschematic.Version.JE_1_19_2)
            print('Your noteblocks saved under "' + saveName+"Notes"+str(NotesCount) + '.schem"')
    if isFar == True:
        NotesCount = NotesCount + 1
        schemNoteBlock.save('./player', saveName+"Notes"+str(NotesCount), mcschematic.Version.JE_1_19_2)
        print('Your noteblocks saved under "' + saveName+"Notes"+str(NotesCount) + '.schem"')
    
    
    
    OrganCount = 0
    OrganblockXPos = 1
    isFar = 0
    temp = 0
    for p in range(0,len(ToBuildNotesIns)):
        if isFar == 0:
            schemNoteBlock = mcschematic.MCSchematic()
        
        if p == 0:
            schemNoteBlock.setBlock((1,0,-3), "create:redstone_link[facing=up,receiver=false]{FrequencyFirst:{id:\"minecraft:stone_button\",Count:1b},FrequencyLast:{id:\"minecraft:stone_button\",Count:1b}}")
            schemNoteBlock.setBlock((1,-1,-3), "minecraft:stone")
            schemNoteBlock.setBlock((1,-1,-4), "minecraft:stone_button[face=wall,facing=north]")
        
        if INSRANGE[ToBuildNotesIns[p]][1] != 57:
            for r in range(0,4):
                if ToBuildNotesIns[p] == 10:
                    if r != 3:
                        for i in range(0,12):
                            schemNoteBlock.setBlock((OrganblockXPos+(r*2),-1 + r,i + temp), "create:fluid_tank")
                            schemNoteBlock.setBlock((OrganblockXPos+(r*2),-2 + r,i + temp), "create:lit_blaze_burner")
                            schemNoteBlock.setBlock((OrganblockXPos+(r*2),0 + r,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]]+"[facing=east,size="+ORGAN_SIZES[r+1]+"]")
                                
                            if r != 2:
                                schemNoteBlock.setBlock((OrganblockXPos+(r*2)+1,0 + r,i + temp), "create:redstone_link[facing=west,receiver=true]{FrequencyFirst:{id:\"minecraft:stone_button\",Count:1b},FrequencyLast:{id:\"minecraft:stone_button\",Count:1b}}")
                            
                            if r % 2 == 0:
                                h = i+1
                                schemNoteBlock.setBlock((OrganblockXPos+(r*2)+1,-1 + r,i + temp), "create:redstone_link[facing=east,receiver=true]{FrequencyFirst:{id:\"minecraft:"+MINECRAFT_BLOCKS[INSRANGE[ToBuildNotesIns[p]][1]-i-(12*r)]+"\",Count:1b},FrequencyLast:{id:\""+MINECRAFT_BLOCKS[ToBuildNotesCurrentLayer[p]]+"\",Count:1b}}")
                            else:
                                h = 12-i
                                schemNoteBlock.setBlock((OrganblockXPos+(r*2)+1,-1 + r,(11-i) + temp), "create:redstone_link[facing=east,receiver=true]{FrequencyFirst:{id:\"minecraft:"+MINECRAFT_BLOCKS[INSRANGE[ToBuildNotesIns[p]][1]-i-(12*r)]+"\",Count:1b},FrequencyLast:{id:\""+MINECRAFT_BLOCKS[ToBuildNotesCurrentLayer[p]]+"\",Count:1b}}")
                            hight = 1
                            while h != 0:
                                if h>2:
                                    schemNoteBlock.setBlock((OrganblockXPos+(r*2),hight + r,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]]+"_extension[shape=double_connected,size="+ORGAN_SIZES[r+1]+"]")
                                    hight = hight + 1
                                    h = h -2
                                if h==2:
                                    schemNoteBlock.setBlock((OrganblockXPos+(r*2),hight + r,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]]+"_extension[shape=double,size="+ORGAN_SIZES[r+1]+"]")
                                    hight = hight + 1
                                    h = h -2
                                if h==1:
                                    schemNoteBlock.setBlock((OrganblockXPos+(r*2),hight + r,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]]+"_extension[shape=single,size="+ORGAN_SIZES[r+1]+"]")
                                    hight = hight + 1
                                    h = h - 1
                                        
                else:
                    for i in range(0,12):
                        schemNoteBlock.setBlock((OrganblockXPos+(r*2),-1 + r,i + temp), "create:fluid_tank")
                        schemNoteBlock.setBlock((OrganblockXPos+(r*2),-2 + r,i + temp), "create:lit_blaze_burner")
                        if ToBuildNotesIns[p] == 1 or ToBuildNotesIns[p] == 6:
                            schemNoteBlock.setBlock((OrganblockXPos+(r*2),0 + r,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]]+"[facing=east,size="+ORGAN_SIZES[r+1]+"]")
                        else:
                            schemNoteBlock.setBlock((OrganblockXPos+(r*2),0 + r,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]]+"[facing=east,size="+ORGAN_SIZES[r]+"]")
                            
                        if r != 3:
                            schemNoteBlock.setBlock((OrganblockXPos+(r*2)+1,0 + r,i + temp), "create:redstone_link[facing=west,receiver=true]{FrequencyFirst:{id:\"minecraft:stone_button\",Count:1b},FrequencyLast:{id:\"minecraft:stone_button\",Count:1b}}")
                        
                        if r % 2 == 0:
                            h = i+1
                            schemNoteBlock.setBlock((OrganblockXPos+(r*2)+1,-1 + r,i + temp), "create:redstone_link[facing=east,receiver=true]{FrequencyFirst:{id:\"minecraft:"+MINECRAFT_BLOCKS[INSRANGE[ToBuildNotesIns[p]][1]-i-(12*r)]+"\",Count:1b},FrequencyLast:{id:\""+MINECRAFT_BLOCKS[ToBuildNotesCurrentLayer[p]]+"\",Count:1b}}")
                        else:
                            h = 12-i
                            schemNoteBlock.setBlock((OrganblockXPos+(r*2)+1,-1 + r,(11-i) + temp), "create:redstone_link[facing=east,receiver=true]{FrequencyFirst:{id:\"minecraft:"+MINECRAFT_BLOCKS[INSRANGE[ToBuildNotesIns[p]][1]-i-(12*r)]+"\",Count:1b},FrequencyLast:{id:\""+MINECRAFT_BLOCKS[ToBuildNotesCurrentLayer[p]]+"\",Count:1b}}")
                        hight = 1
                        if ToBuildNotesIns[p] == 8:
                            while h != 0:
                                if h>4:
                                    schemNoteBlock.setBlock((OrganblockXPos+(r*2),hight + r,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]]+"_extension[shape=quad_connected,size="+ORGAN_SIZES[r]+"]")
                                    hight = hight + 1
                                    h = h -4
                                if h==4:
                                    schemNoteBlock.setBlock((OrganblockXPos+(r*2),hight + r,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]]+"_extension[shape=quad,size="+ORGAN_SIZES[r]+"]")
                                    hight = hight + 1
                                    h = h -4
                                if h==3:
                                    schemNoteBlock.setBlock((OrganblockXPos+(r*2),hight + r,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]]+"_extension[shape=triple,size="+ORGAN_SIZES[r]+"]")
                                    hight = hight + 1
                                    h = h -3
                                if h==2:
                                    schemNoteBlock.setBlock((OrganblockXPos+(r*2),hight + r,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]]+"_extension[shape=double,size="+ORGAN_SIZES[r]+"]")
                                    hight = hight + 1
                                    h = h -2
                                if h==1:
                                    schemNoteBlock.setBlock((OrganblockXPos+(r*2),hight + r,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]]+"_extension[shape=single,size="+ORGAN_SIZES[r]+"]")
                                    hight = hight + 1
                                    h = h - 1
                        elif ToBuildNotesIns[p] == 1:
                            while h != 0:
                                if h>1:
                                    schemNoteBlock.setBlock((OrganblockXPos+(r*2),hight + r,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]]+"_extension[shape=quad_connected,size="+ORGAN_SIZES[r+1]+"]")
                                    hight = hight + 1
                                    h = h -1
                                if h==1:
                                    schemNoteBlock.setBlock((OrganblockXPos+(r*2),hight + r,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]]+"_extension[shape=quad,size="+ORGAN_SIZES[r+1]+"]")
                                    hight = hight + 1
                                    h = h -1
                        elif ToBuildNotesIns[p] == 6:
                            while h != 0:
                                if h>2:
                                    schemNoteBlock.setBlock((OrganblockXPos+(r*2),hight + r,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]]+"_extension[shape=quad_connected,size="+ORGAN_SIZES[r+1]+"]")
                                    hight = hight + 1
                                    h = h -2
                                if h==2:
                                    schemNoteBlock.setBlock((OrganblockXPos+(r*2),hight + r,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]]+"_extension[shape=quad,size="+ORGAN_SIZES[r+1]+"]")
                                    hight = hight + 1
                                    h = h -2
                                if h==1:
                                    schemNoteBlock.setBlock((OrganblockXPos+(r*2),hight + r,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]]+"_extension[shape=double,size="+ORGAN_SIZES[r+1]+"]")
                                    hight = hight + 1
                                    h = h - 1
                        else:
                            while h != 0:
                                if h>2:
                                    schemNoteBlock.setBlock((OrganblockXPos+(r*2),hight + r,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]]+"_extension[shape=quad_connected,size="+ORGAN_SIZES[r]+"]")
                                    hight = hight + 1
                                    h = h -2
                                if h==2:
                                    schemNoteBlock.setBlock((OrganblockXPos+(r*2),hight + r,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]]+"_extension[shape=quad,size="+ORGAN_SIZES[r]+"]")
                                    hight = hight + 1
                                    h = h -2
                                if h==1:
                                    schemNoteBlock.setBlock((OrganblockXPos+(r*2),hight + r,i + temp), INSTRUMENTS_BLOCK[ToBuildNotesIns[p]]+"_extension[shape=double,size="+ORGAN_SIZES[r]+"]")
                                    hight = hight + 1
                                    h = h - 1
                            
                    
            if isFar == 3:
                OrganCount = OrganCount + 1
                schemNoteBlock.save('./player', saveName+"Organ"+str(OrganCount), mcschematic.Version.JE_1_19_2)
                print('Your organs saved under "' + saveName+"Organ"+str(OrganCount) + '.schem"')
                    
            if isFar ==  0:
                temp = 13
                isFar = 1
            elif isFar ==  1:
                temp = 26
                isFar = 2
            elif isFar ==  2:
                temp = 39
                isFar = 3 
            else:
                temp = 0
                isFar =0
                OrganblockXPos = OrganblockXPos + 8
                
    if isFar != 0:# and isFar != 2:
        OrganCount = OrganCount + 1
        schemNoteBlock.save('./player', saveName+"Organ"+str(OrganCount), mcschematic.Version.JE_1_19_2)
        print('Your organs saved under "' + saveName+"Organ"+str(OrganCount) + '.schem"')
    
    
    schem.setBlock((-6,-2,0), "minecraft:stone")
    schem.setBlock((-6,-1,0), "create:redstone_link[facing=up,receiver=false]{FrequencyFirst:{id:\"minecraft:lever\",Count:1b},FrequencyLast:{id:\"minecraft:lever\",Count:1b}}")
    
    schem.setBlock((-7,-2,0), "minecraft:stone")
    schem.setBlock((-7,-1,0), "minecraft:comparator[facing=west,mode=subtract]")
    
    schem.setBlock((-8,-2,0), "minecraft:stone")
    schem.setBlock((-8,-1,0), "minecraft:redstone_wire[east=side,north=none,south=none,west=side]")
    
    schem.setBlock((-9,-2,0), "minecraft:stone")
    schem.setBlock((-9,-1,0), "minecraft:oak_button[face=floor,facing=south]")
    
    schem.setBlock((-7,-2,-1), "minecraft:stone")
    schem.setBlock((-7,-1,-1), "minecraft:redstone_wire[east=none,north=none,south=side,west=side]")
    
    schem.setBlock((-8,-2,-1), "minecraft:stone")
    schem.setBlock((-8,-1,-1), "minecraft:repeater[delay=2,facing=west]")
    
    schem.setBlock((-9,-2,-1), "minecraft:stone")
    schem.setBlock((-9,-1,-1), "minecraft:redstone_wire[east=side,north=none,south=side,west=none]")
    

    schem.save('./player', saveName, mcschematic.Version.JE_1_19_2)
    print('Your schematic was generated and saved under "' + saveName + '.schem"')
    
    print()
    print("You have "+str(OrganCount)+" organs and "+str(NotesCount)+" noteblocks to paste in!")
    print("You need to stand on a block and place all the organs and noteblocks.")
    print("You can then paste in the player!")
    temp = input("Press ENTER to quit.")
    
if __name__ == '__main__':
    main()
