import pynbs
import sys
import math
import mcschematic
from constant import *

def getValidInput(validInputs, prompt):
    while True:
        userInput = input(prompt)
        if userInput in validInputs:
            return userInput
        else:
            print(f'"{userInput}" is not a valid input. Please try again.')


def verifyFormat(song, songName):
    print("Verifying your song...")

    # check custom instruments
    print("Checking for custom instruments...")
    if len(song.instruments) > 0:
        sys.exit(f'Warning: "{songName}" contains custom instruments.')
        
    print("Song verified. Everything looks good!")

def main():
    # get song file from user
    songFile = "Test.nbs" #input("Please enter the file name of your song (include the .nbs): ")
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
    schem = mcschematic.MCSchematic()
    schemNoteBlock = mcschematic.MCSchematic()
    schemNoteBlock2 = mcschematic.MCSchematic()
    CurrentLayer = 0
    NoteblockXPos = 0
    OtherNotesClick = []
    OtherNotesPling = []
    
    for instrument in range(0,16):
        LeftToPlayKey = []
        LeftToPlayTick = []
        for tick, chord in song:
            for note in chord:
                if note.instrument == instrument:
                    LeftToPlayKey.append(note.key)
                    LeftToPlayTick.append(note.tick)
        
        if len(LeftToPlayKey)>0:
            schem.setBlock((-4, CurrentLayer*3, 0), INSTRUMENTS_BLOCK[instrument])
            schem.setBlock((-4, CurrentLayer*3-1, 0), "minecraft:stone")
        
        ToBuildKey = []
        ToBuildTick = []
        LastAddedTick = -2
        while len(LeftToPlayKey)>0:
            temp = 0
            for i in range(len(LeftToPlayKey)):
                if LeftToPlayTick[i-temp]>LastAddedTick+1:
                    LastAddedTick = LeftToPlayTick[i-temp]
                    
                    if LeftToPlayKey[i-temp] < INSRANGE[instrument][0]:
                        shift = LeftToPlayKey[i-temp]
                        while shift < INSRANGE[instrument][0]:
                            shift = shift + 12
                        ToBuildKey.append(shift)
                    elif LeftToPlayKey[i-temp] > INSRANGE[instrument][1]:
                        shift = LeftToPlayKey[i-temp]
                        while shift > INSRANGE[instrument][1]:
                            shift = shift - 12
                        ToBuildKey.append(shift)
                    else:
                        ToBuildKey.append(LeftToPlayKey[i-temp])
                    LeftToPlayKey.pop(i-temp)
                    
                    ToBuildTick.append(LeftToPlayTick[i-temp])
                    LeftToPlayTick.pop(i-temp)
                    temp += 1
                    
            
            #print(INSTRUMENTS[instrument] + ": " + str(ToBuildTick))
            #print(INSTRUMENTS[instrument] + ": " + str(ToBuildKey))
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
                        
                schem.setBlock((XPos, CurrentLayer*3, YPos), "create:redstone_link[facing=up]{FrequencyFirst:{id:\""+MINECRAFT_BLOCKS[ToBuildKey[0]]+"\",Count:1b},FrequencyLast:{id:\""+INSTRUMENTS_BLOCK[CurrentLayer]+"\",Count:1b}}")
                schem.setBlock((XPos, CurrentLayer*3-1, YPos), "minecraft:stone")
                if Direction == "west":
                    XPos = XPos + 1
                else:
                    XPos = XPos - 1
                ToBuildTick.pop(0)
                ToBuildKey.pop(0)
            
            if INSRANGE[instrument][1] == 57:
                if instrument != 15 and instrument != 4:
                    if NoteblockXPos % 2 ==  1:
                        for i in range(0,25):
                            schemNoteBlock.setBlock((math.floor(NoteblockXPos/2),0,i + 26), "minecraft:note_block[note="+str(i)+",instrument="+INSTRUMENTS[CurrentLayer]+"]")
                            schemNoteBlock.setBlock((math.floor(NoteblockXPos/2),-1,i + 26), INSTRUMENTS_BLOCK[instrument])
                            schemNoteBlock.setBlock((math.floor(NoteblockXPos/2),-2,i + 26), "create:redstone_link[facing=down,receiver=true]{FrequencyFirst:{id:\"minecraft:"+MINECRAFT_BLOCKS[i+33]+"\",Count:1b},FrequencyLast:{id:\""+INSTRUMENTS_BLOCK[instrument]+"\",Count:1b}}")
                    else:
                        for i in range(0,25):
                            schemNoteBlock2.setBlock((math.floor(NoteblockXPos/2),0,i), "minecraft:note_block[note="+str(i)+",instrument="+INSTRUMENTS[CurrentLayer]+"]")
                            schemNoteBlock2.setBlock((math.floor(NoteblockXPos/2),-1,i), INSTRUMENTS_BLOCK[instrument])
                            schemNoteBlock2.setBlock((math.floor(NoteblockXPos/2),-2,i), "create:redstone_link[facing=down,receiver=true]{FrequencyFirst:{id:\"minecraft:"+MINECRAFT_BLOCKS[i+33]+"\",Count:1b},FrequencyLast:{id:\""+INSTRUMENTS_BLOCK[instrument]+"\",Count:1b}}")
                    NoteblockXPos = NoteblockXPos + 1
                else:
                    if instrument == 4:
                        OtherNotesClick.append(CurrentLayer)
                    else:
                        OtherNotesPling.append(CurrentLayer)
            
            CurrentLayer = CurrentLayer + 1
            
            ToBuildKey=[]
            ToBuildTick=[]
            LastAddedTick = -2
    
    saveName = songName.lower().replace('(', '').replace(')', '').replace(' ', '_')
    schem.save('', saveName, mcschematic.Version.JE_1_19_2)
    schemNoteBlock.save('', saveName+"Notes", mcschematic.Version.JE_1_19_2)
    schemNoteBlock2.save('', saveName+"Notes2", mcschematic.Version.JE_1_19_2)
    print('Your schematic was successfully generated and saved under "' + saveName + '.schem"')
    
if __name__ == '__main__':
    main()