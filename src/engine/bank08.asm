	INCROM $20000, $200e5

; 0 - e4 is a big set of data, seems to be one entry for each card

Func_200e5: ; 200e5 (8:40e5)
	ld [wce18], a
	call CreateHandCardList
	ld hl, wDuelTempList
	ld de, wTempHandCardList
	call CopyBuffer
	ld hl, wTempHandCardList
	ld a, [hli]
	ld [wce16], a
	cp $ff
	ret z
	push hl
	ld a, [wce18]
	ld d, a
	ld hl, $4000
.asm_4106
	xor a
	ld [wce21], a
	ld a, [hli]
	cp $ff
	jp z, $41b1
	cp d
	jp nz, .incHL5
	ld a, [hli]
	ld [wce17], a
	ld a, [wce16]
	call LoadCardDataToBuffer1_FromDeckIndex
	cp $d2
	jr nz, .asm_2012b
	ld b, a
	ld a, [wce20]
	and $2
	jr nz, .incHL4
	ld a, b

.asm_2012b
	ld b, a
	ld a, [wce17]
	cp b
	jr nz, .incHL4
	push hl
	push de
	ld a, [wce16]
	ldh [hTempCardIndex_ff9f], a
	bank1call CheckCantUseTrainerDueToHeadache
	jp c, $41a8
	call LoadNonPokemonCardEffectCommands
	ld a, EFFECTCMDTYPE_INITIAL_EFFECT_1
	call TryExecuteEffectCommandFunction
	jp c, $41a8
	farcall $5, $743b
	jr c, .asm_201a8
	pop de
	pop hl
	push hl
	call CallIndirect
	pop hl
	jr nc, .incHL4
	inc hl
	inc hl
	ld [wce19], a
	push de
	push hl
	ld a, [wce16]
	ldh [hTempCardIndex_ff9f], a
	ld a, $6
	bank1call $67be
	pop hl
	pop de
	jr c, .incHL2
	push hl
	call CallIndirect
	pop hl
	inc hl
	inc hl
	ld a, [wce20]
	ld b, a
	ld a, [wce21]
	or b
	ld [wce20], a
	pop hl
	and $8
	jp z, $40f7
	call CreateHandCardList
	ld hl, wDuelTempList
	ld de, wTempHandCardList
	call $697b
	ld hl, wTempHandCardList
	ld a, [wce20]
	and $f7
	ld [wce20], a
	jp $40f7

.incHL5
	inc hl

.incHL4
	inc hl
	inc hl

.incHL2
	inc hl
	inc hl
	jp .asm_4106

.asm_201a8
	pop de
	pop hl
	inc hl
	inc hl
	inc hl
	inc hl
	jp .asm_4106
; 0x201b1

	INCROM $201b1, $2297b

; copies $ff terminated buffer from hl to de
CopyBuffer: ; 2297b (8:697b)
	ld a, [hli]
	ld [de], a
	cp $ff
	ret z
	inc de
	jr CopyBuffer
; 0x22983

	INCROM $22983, $22990

; counts number of energy cards found in hand
; and outputs result in a
; sets carry if none are found
; output:
; 	a = number of energy cards found
CountEnergyCardsInHand: ; 22990 (8:6990)
	farcall CreateEnergyCardListFromHand
	ret c
	ld b, -1
	ld hl, wDuelTempList
.loop
	inc b
	ld a, [hli]
	cp $ff
	jr nz, .loop
	ld a, b
	or a
	ret
; 0x229a3

Func_229a3 ; 229a3 (8:69a3)
	INCROM $229a3, $24000
