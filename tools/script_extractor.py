#!/usr/bin/env python3
###############################################################################
###### Use: python3 tools/script_extractor --noauto --error location     ######
###### --noauto  turns off automatic script parsing (enter to continue)  ######
###### --error   stops execution if an error occurs                      ######
###### location can be local to bank or global. This program assumes     ######
###### every script is in bank 3, which seems to be the case.            ######
######                                                                   ######
###### Script list is a work in progress. The following arguments are    ######
###### accepted and accounted for.                                       ######
###### b - byte    w - word    j - jump (within script)    t - text (tx) ######
###### f - flag    d - direction    i - decimal byte    m - npc move ptr ######
###### q - Used when the script's arguments have not been determined yet ######
###############################################################################
import argparse

# Quit Types
DO_NOT_QUIT = 0
QUIT_CONTINUE_CODE = 1
QUIT_JUMP = 2
QUIT_SPECIAL = 3
QUIT_DEBUG = -1

dir_list = ["NORTH","EAST","SOUTH","WEST"]

def printHeader(loc, prefix):
		ls = format(loc,"04x")
		lsa = format(loc-0x8000,"04x")
		print(prefix + ls + ": ; " + ls + " (3:" + lsa + ")" )

def extractMovement(game_data, loc, errQuit):
	printHeader(loc, "NPCMovement_")
	loc -= 1 # so we can continue without breaking things
	while game_data[loc+1] != 0xff:
		loc += 1
		dirLow = game_data[loc] & 0x0f
		if dirLow > 3:
			print("ERROR: [" + format(loc,"04x") + "] was not a valid direction. Got: " +  format(game_data[loc],"02x"))
			if errQuit:
				return QUIT_DEBUG
			continue
		lineStr = "\tdb " + dir_list[dirLow]
		dirHigh = game_data[loc] & 0xf0
		if dirHigh == 0x80:
			lineStr += " | NO_MOVE"
		elif dirHigh != 0x00:
			print("ERROR: [" + format(loc,"04x") + "] was not a valid direction. Got: " +  format(game_data[loc],"02x"))
			if errQuit:
				return QUIT_DEBUG
			continue
		print(lineStr)
	print("\tdb $ff")
	print("; " + format(loc+2,"04x"))
	return DO_NOT_QUIT

def decodeLine(scriptList, game_data, loc, ignore_broken, locList):
	currLine = scriptList[game_data[loc]]
	ret = "\trun_script " + currLine[0] + "\n"
	loc+=1
	quit = currLine[2]
	for c in currLine[1]:
		if c == "b":
			ret += "\tdb $" + format(game_data[loc],"02x") + "\n"
			loc += 1
		elif c == "i":
			ret += "\tdb " + str(game_data[loc]) + "\n"
			loc += 1
		elif c == "w":
			ret += "\tdw $" + format((game_data[loc] + (game_data[loc+1]<<8)),"04x") + "\n"
			loc += 2
		elif c == "j":
			wordLoc = (game_data[loc] + (game_data[loc+1]<<8))
			if wordLoc == 0000:
				ret += "\tdw NO_JUMP\n"
			else:
				ret += "\tdw .ows_" + format(wordLoc+0x8000,"04x") + "\n"
				locList.append(wordLoc)
			loc += 2
		elif c == "t":
			addr = (game_data[loc] + (game_data[loc+1]<<8))
			if addr == 0:
				ret += "\tdw $0000\n"
			else:
				ret += "\ttx Text" + format(addr,"04x") + "\n"
			loc += 2
		elif c == "f":
			ret += "\tdb EVENT_FLAG_" + format(game_data[loc],"02X") + "\n"
			loc += 1
		elif c == "d":
			ret += "\tdb " + dir_list[game_data[loc]] + "\n"
			loc += 1
		elif c == "m":
			wordLoc = (game_data[loc] + (game_data[loc+1]<<8))
			ret += "\tdw NPCMovement_" + format(wordLoc + 0x8000, "04x") + "\n"
			loc += 2
		elif c == "q":
			print("haven't updated data for this yet")
			if not ignore_broken:
				quit = QUIT_DEBUG
		else:
			print("UNACCEPTED CHARACTER: " + c)
	return (loc, ret, quit)

def main():
	scriptList = createList()
	locList = []

	parser = argparse.ArgumentParser(description='Pokemon TCG Script Extractor')
	parser.add_argument('--noauto', action='store_true', help='turns off automatic script parsing')
	parser.add_argument('--error', action='store_true', help='stops execution if an error occurs')
	parser.add_argument('-m', '--movement', action='store_true', help='interprets bytes as a movement script rather than an OWSequence')
	parser.add_argument('-r', '--rom', default="baserom.gbc", help='rom file to extract script from')
	parser.add_argument('locations', nargs="+", help='locations to extract from. May be local to bank or global.')
	args = parser.parse_args()
	for locStr in args.locations:
		loc = int(locStr,0)
		if loc > 0x7fff:
			# Must be a global location
			loc -= 0x8000
		locList.append(loc)

	# this is a list of every start location we've read to avoid infinite loops
	exploredList = []

	with open(args.rom, "rb") as file:
	    game_data = file.read()

	auto = not args.noauto
	end = DO_NOT_QUIT
	ignore_broken = not args.error
	while (len(locList) > 0 and end != QUIT_DEBUG):
		locList.sort() # export parts in order somewhat
		loc = locList.pop(0) + 0x8000
		if args.movement:
			end = extractMovement(game_data,loc, args.error)
		else:
			end = printScript(game_data, loc, auto, ignore_broken, scriptList,\
			locList, exploredList)

def printScript(game_data, loc, auto, ignore_broken, scriptList, \
				locList, exploredList):
	if loc in exploredList:
		return
	exploredList.append(loc)
	script = ""
	end = DO_NOT_QUIT
	if game_data[loc] != 0xe7:
		#print("Error: first byte was not start_script")
		print(".ows_" + format(loc,"04x"))
	else:
 		
		# TODO this is hacky please don't do this 
		printHeader(loc, "OWSequence_")
		loc += 1
		print("\tstart_script")
	while end == DO_NOT_QUIT:
		loc, outstr, end = decodeLine(scriptList,game_data,loc,ignore_broken,locList)
		outstr = outstr[:-1] # [:-1] strips the newline at the end
		if auto:
			print(outstr)
		else:
			input(outstr)
	warning = ""
	if end == QUIT_CONTINUE_CODE:
		warning = " WARNING: There is probably regular assembly here"

	print("; " + hex(loc) + warning)

	# if the next byte is a ret, print it for the continue_code case
	if game_data[loc] == 0xc9:
		print("\tret")

	return end

def createList(): # this is a func just so all this can go at the bottom
	# name, arg list, is an ender
	return [
	("OWScript_EndScriptLoop1", "", QUIT_CONTINUE_CODE),
	("OWScript_CloseAdvancedTextBox", "", DO_NOT_QUIT),
	("OWScript_PrintTextString", "t", DO_NOT_QUIT),
	("Func_ccdc", "t", DO_NOT_QUIT),
	("OWScript_AskQuestionJump", "tj", DO_NOT_QUIT), # more complex behavior too (jumping)
	("OWScript_StartBattle", "bbb", DO_NOT_QUIT),
	("OWScript_PrintVariableText", "tt", DO_NOT_QUIT),
	("Func_cda8", "bbbb", DO_NOT_QUIT),
	("OWScript_PrintTextQuitFully", "t", QUIT_SPECIAL),
	("Func_cdcb", "", DO_NOT_QUIT),
	("OWScript_MoveActiveNPCByDirection", "w", DO_NOT_QUIT),
	("OWScript_CloseTextBox", "", DO_NOT_QUIT),
	("OWScript_GiveBoosterPacks", "bbb", DO_NOT_QUIT),
	("Func_cf0c", "bj", DO_NOT_QUIT), # more complex behavior too (jumping)
	("Func_cf12", "bj", DO_NOT_QUIT),
	("OWScript_GiveCard", "b", DO_NOT_QUIT),
	("OWScript_TakeCard", "b", DO_NOT_QUIT),
	("Func_cf53", "w", DO_NOT_QUIT), # more complex behavior too (jumping)
	("Func_cf7b", "", DO_NOT_QUIT),
	("Func_cf2d", "bbbb", DO_NOT_QUIT), # more complex behavior too (jumping + ??)
	("Func_cf96", "w", DO_NOT_QUIT), # only jumps? still needs args to do that though
	("Func_cfc6", "b", DO_NOT_QUIT),
	("Func_cfd4", "", DO_NOT_QUIT),
	("Func_d00b", "", DO_NOT_QUIT), # includes something with random and extra data
	("Func_d025", "w", DO_NOT_QUIT), # possibly only jumps, still needs args
	("Func_d032", "w", DO_NOT_QUIT), # see above
	("Func_d03f", "", DO_NOT_QUIT),
	("OWScript_Jump", "j", QUIT_JUMP), # jumps to d
	("OWScript_TryGiveMedalPCPacks", "", DO_NOT_QUIT),
	("OWScript_SetPlayerDirection", "d", DO_NOT_QUIT),
	("OWScript_MovePlayer", "db", DO_NOT_QUIT),
	("OWScript_ShowCardReceivedScreen", "b", DO_NOT_QUIT),
	("OWScript_SetDialogName", "b", DO_NOT_QUIT),
	("OWScript_SetNextNPCandOWSequence", "bj", DO_NOT_QUIT),
	("Func_d095", "bbb", DO_NOT_QUIT),
	("Func_d0be", "bb", DO_NOT_QUIT),
	("OWScript_DoFrames", "i", DO_NOT_QUIT),
	("Func_d0d9", "bbw", DO_NOT_QUIT), # jumps but still needs args
	("OWScript_JumpIfPlayerCoordMatches", "iij", DO_NOT_QUIT), # jumps but still needs args
	("OWScript_MoveActiveNPC", "m", DO_NOT_QUIT),
	("OWScript_GiveOneOfEachTrainerBooster", "", DO_NOT_QUIT),
	("Func_d103", "q", DO_NOT_QUIT),
	("Func_d125", "b", DO_NOT_QUIT),
	("Func_d135", "b", DO_NOT_QUIT),
	("Func_d16b", "b", DO_NOT_QUIT),
	("Func_cd4f", "bbb", DO_NOT_QUIT),
	("Func_cd94", "q", DO_NOT_QUIT),
	("OWScript_MoveWramNPC", "m", DO_NOT_QUIT),
	("Func_cdd8", "", DO_NOT_QUIT),
	("Func_cdf5", "bb", DO_NOT_QUIT),
	("Func_d195", "", DO_NOT_QUIT),
	("Func_d1ad", "", DO_NOT_QUIT),
	("Func_d1b3", "", DO_NOT_QUIT),
	("OWScript_QuitScriptFully", "", QUIT_SPECIAL),
	("Func_d244", "q", DO_NOT_QUIT),
	("Func_d24c", "q", DO_NOT_QUIT),
	("OWScript_OpenDeckMachine", "b", DO_NOT_QUIT),
	("Func_d271", "q", DO_NOT_QUIT),
	("OWScript_EnterMap", "bbood", DO_NOT_QUIT),
	("OWScript_MoveArbitraryNPC", "bm", DO_NOT_QUIT),
	("Func_d209", "", DO_NOT_QUIT),
	("Func_d38f", "b", DO_NOT_QUIT),
	("Func_d396", "b", DO_NOT_QUIT),
	("Func_cd76", "", DO_NOT_QUIT),
	("Func_d39d", "b", DO_NOT_QUIT),
	("Func_d3b9", "", DO_NOT_QUIT),
	("OWScript_TryGivePCPack", "b", DO_NOT_QUIT),
	("OWScript_nop", "", DO_NOT_QUIT),
	("Func_d3d4", "q", DO_NOT_QUIT),
	("Func_d3e0", "", DO_NOT_QUIT),
	("Func_d3fe", "q", DO_NOT_QUIT),
	("Func_d408", "b", DO_NOT_QUIT),
	("Func_d40f", "q", DO_NOT_QUIT),
	("OWScript_PlaySFX", "b", DO_NOT_QUIT),
	("OWScript_PauseSong", "q", DO_NOT_QUIT),
	("OWScript_ResumeSong", "q", DO_NOT_QUIT),
	("Func_d41d", "", DO_NOT_QUIT),
	("OWScript_WaitForSongToFinish", "q", DO_NOT_QUIT),
	("Func_d435", "b", DO_NOT_QUIT),
	("OWScript_AskQuestionJumpDefaultYes", "tj", DO_NOT_QUIT),
	("Func_d2f6", "q", DO_NOT_QUIT),
	("Func_d317", "", DO_NOT_QUIT),
	("Func_d43d", "q", DO_NOT_QUIT),
	("OWScript_EndScriptLoop2", "q", QUIT_CONTINUE_CODE),
	("OWScript_EndScriptLoop3", "q", QUIT_CONTINUE_CODE),
	("OWScript_EndScriptLoop4", "q", QUIT_CONTINUE_CODE),
	("OWScript_EndScriptLoop5", "q", QUIT_CONTINUE_CODE),
	("OWScript_EndScriptLoop6", "q", QUIT_CONTINUE_CODE),
	("OWScript_SetFlagValue", "fb", DO_NOT_QUIT),
	("OWScript_JumpIfFlagZero1", "fj", DO_NOT_QUIT),
	("OWScript_JumpIfFlagNonzero1", "q", DO_NOT_QUIT),
	("OWScript_JumpIfFlagEqual", "fbj", DO_NOT_QUIT), # also capable of jumping
	("OWScript_JumpIfFlagNotEqual", "fbj", DO_NOT_QUIT), # jumps
	("OWScript_JumpIfFlagNotLessThan", "fbj", DO_NOT_QUIT),
	("OWScript_JumpIfFlagLessThan", "fbj", DO_NOT_QUIT),
	("OWScript_MaxOutFlagValue", "f", DO_NOT_QUIT),
	("OWScript_ZeroOutFlagValue", "f", DO_NOT_QUIT),
	("OWScript_JumpIfFlagNonzero2", "fj", DO_NOT_QUIT),
	("OWScript_JumpIfFlagZero2", "fj", DO_NOT_QUIT),
	("OWScript_IncrementFlagValue", "f", DO_NOT_QUIT),
	("OWScript_EndScriptLoop7", "q", QUIT_CONTINUE_CODE),
	("OWScript_EndScriptLoop8", "q", QUIT_CONTINUE_CODE),
	("OWScript_EndScriptLoop9", "q", QUIT_CONTINUE_CODE),
	("OWScript_EndScriptLoop10", "q", QUIT_CONTINUE_CODE)
	]

main()
