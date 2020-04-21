; farcall from 0xb87e(2:787d): [EF|06|9A|7A]
Func_1ba9a: ; 1ba9a (6:7a9a)
	xor a
	ld [wd0a6], a
	ld a, $01
.asm_7aa0
	call Func_1bae4
	ret nc
	sla a
	cp $10
	jr z, .asm_7aac
	jr .asm_7aa0
.asm_7aac
	ld a, $03
	call Func_1bae4
	ret nc
	ld a, $05
	call Func_1bae4
	ret nc
	ld a, $09
	call Func_1bae4
	ret nc
	ld a, $06
	call Func_1bae4
	ret nc
	ld a, $0a
	call Func_1bae4
	ret nc
	ld a, $0c
	call Func_1bae4
	ret nc
	ld a, $f7
.asm_7ad2
	call Func_1bae4
	ret nc
	sra a
	cp $ff
	jr z, .asm_7ade
	jr .asm_7ad2
.asm_7ade
	call Func_1bae4
	ret nc
	scf
	ret

Func_1bae4: ; 1bae4 (6:7ae4)
	push af
	ld hl, wd088
	ld b, [hl]
	farcall $2, $7625
	jr c, .asm_7af5
	pop af
	ld [wd0a6], a
	or a
	ret
.asm_7af5
	pop af
	scf
	ret