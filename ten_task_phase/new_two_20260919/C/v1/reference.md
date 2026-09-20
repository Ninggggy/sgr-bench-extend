# C v1 — RISC-V suspended-task byte layout

Status: first independent review confirmed all eight numeric rows; bounded evidence/scoring repairs submitted for re-review; no blind scores.

## Natural purpose and closed scope

A debugger decoder must distinguish the saved task pointer from the ISR stack and locate variable-width register banks. The eight cases are the complete Cartesian product explicitly requested: XLEN 32/64, FLEN 32/64, VS Clean/Dirty, with FS Dirty throughout. RV32E, task initialization, exception PC advancement, external chip save extensions, nested interrupts and hardware alignment-fault behavior are excluded explicitly, not inferred after testing. This is source-level write analysis, not a claim that every case executes fault-free on a particular chip.

The official release history identifies V11.3.0 (March 2026) as adding both RISC-V floating-point and vector context save; the selected tagged source path establishes GCC identity. V11.2.0 is the preceding stable release and lacks these save macros. V11.3.1 is later and therefore outside the selection rule. This selection is independently checkable via the release notes. The extension selected by the stated chip properties is RISCV_no_extensions, whose additional-context count is zero and save macro is empty.

## Public sources and acquisition

- Release selection: https://github.com/FreeRTOS/FreeRTOS-Kernel/releases — V11.3.0 release notes, additions of FPU and Vector context-save support; native web checked 2026-09-19.
- Entry path and ABI name mapping: https://raw.githubusercontent.com/FreeRTOS/FreeRTOS-Kernel/V11.3.0/portable/GCC/RISC-V/portASM.S — include portContext.h, interrupt handlers, x1/ra table. Original bytes are saved here; native web checked 2026-09-19.
- Save operations: https://raw.githubusercontent.com/FreeRTOS/FreeRTOS-Kernel/V11.3.0/portable/GCC/RISC-V/portContext.h — macro definitions and SAVE_CONTEXT_INTERNAL/SAVE_INTERRUPT_CONTEXT. Original bytes and browser-rendered source DOM saved here; native web and browser checked 2026-09-19.
- Selected chip behavior: https://raw.githubusercontent.com/FreeRTOS/FreeRTOS-Kernel/V11.3.0/portable/GCC/RISC-V/chip_specific_extensions/RISCV_no_extensions/freertos_risc_v_chip_specific_extensions.h — three configuration macros and empty SAVE_ADDITIONAL_REGISTERS. Fetch timestamp in acquisition.json.

These are individual original documents. No bulk export, private cache, data API or browser-only dynamic result is necessary. The browser raw-header navigation failed earlier; the ordinary GitHub blob page was used for supplementary browser inspection. The historical raw-browser error record is unavailable in this package; it is a reported failure and is not counted as success. Fresh reproducibility is documented by browser_replay.json and its complete attached DOMs. The native public-web tool directly read the raw source. Native web line numbering differs from saved-file physical lines, so evidence locations below use stable macro names. Relevant operations were read in both presentations; the different line totals are not themselves evidence of different source content.

## Recalculation and field evidence

Run `python3 recompute.py`. The input is the saved source, not oracle.psv. The source-specific extractor reads allocation expressions, original register-store offsets and FPU store operands, and simulates each vector stack-pointer move. XLEN/FLEN widths, non-E preprocessor selection, FS/VS branches and endpoint semantics are manually verified from the actual definitions; this is not a complete preprocessor/interpreter. It now records vector groups and CSR write spans, adds manually verified final header spans, and intersects all recorded later writes with prior integer-register stores. It emits derived.json with intermediate spans and oracle.psv with final offsets.

Let W=XLEN/8 and F=FLEN/8. The non-E core allocates 31W; entry x1 is stored at core_sp+2W. The FPU macro reserves 33F, writes f0 at new_sp+2W, and writes fcsr at new_sp+2W+32F using store_x (W bytes). A Dirty vector context adds 32*16+4W bytes: the macro first unreserves 2W, saves four groups of eight vectors, reserves four CSR words, then re-reserves 2W. Its v0 begins 6W above final P. Clean VS does not enter that macro. Final mstatus and mepc occupy the reserved header; the empty chip macro does not move sp. The ISR-stack load occurs after the reference point.

Thus frame_bytes = 31W+33F+V, ra_offset = 2W+33F+V, f0_offset = 2W+V, fcsr_range = [2W+32F+V,3W+32F+V), where V is zero or 512+4W. These expressions are an independent manual cross-check of the source-specific extractor plus manual semantic checks, not its inputs.

For RV64F32 the fcsr store overlaps the lower-addressed four bytes of the saved x1 image. The overlap ranges are [148,152) or [692,696), depending on VS. For the other width pairs there is no integer-register overlap. Other potential later writes were checked: vector register/CSR writes are below the FPU bank; mepc and mstatus are in reserved header slots; there are no chip-specific saves. The value of fcsr is not scored, only its write interval.

Field locations: configuration and VS come from the public Cartesian scope; frame_bytes uses portCONTEXT_SIZE, portFPU_CONTEXT_SIZE and every sp move in portcontexSAVE_VPU_CONTEXT; ra_offset uses store_x x1 in SAVE_CONTEXT_INTERNAL; f0_offset and fcsr_range use their respective store lines in portcontexSAVE_FPU_CONTEXT plus the width definitions; v0_offset uses the vs8r.v v0 line and subsequent CSR/header decrements; overwritten_integer_bytes is the interval intersection with prior store_x x-register operations. The final P definition is the store_x sp,0(t0) into pxCurrentTCB.

## Necessary judgments and counterexamples

Release selection controls the source tree: using the preceding stable version gives no optional FPU/VPU frame at all. Confusing task initialization with an interrupted task would incorrectly use a frame that begins with Clean extension states. Treating all stored values as FLEN-sized misses that fcsr uses store_x; treating all reservations as XLEN-sized changes unequal-width rows. Counting the vector header as six newly added words overstates total allocation by two words because those words were first unreserved. Using the ISR sp instead of saved task P makes all offsets refer to the wrong memory region.

No found summary page prints the requested eight layouts or collision intervals. portASM.S has a schematic frame diagram, but it does not establish byte sizes, conditional inclusion or overwrites. Most substantive fields vary across scenarios. A skilled reader can use a short path: release notes → tagged GCC port → included save macros and selected chip header → symbolic writes. The arithmetic is small. However, most semantic work is concentrated in portContext.h, and the chip properties already imply no extra-register intent: whether this is sufficiently discovery-dependent is a specific issue for independent review. Code complexity alone is not evidence that Sol will score low.

## Pairing, scoring and ambiguity rules

CG and GO share the exact scope, assumptions and output. CG adds only a general tracking method; it does not name the selected tag or header. Eight equal-weight fields; composite row key is configuration+VS. An interval is one field; no weighting by its number of bytes. Case, harmless whitespace, hexadecimal numbers and ra/x1 aliases are normalized. NONE means a documented absent vector save or no overlap, not an unknown value. Duplicate rows and extras count against precision. Wrong keys cannot obtain unassociated numeric-field credit. Order and prose affect whole-answer/format reporting; ordinary Markdown is accepted. Item-F1 is checked with integer arithmetic and cannot qualify before the raw trajectory has been audited.

## First-review repair evidence

The tagged directory has four bundled extension subdirectories (browser_chip_directory.txt). Pulpino_Vega_RV32M1RM has MTIME=0 but six extra registers. RISCV_MTIME_CLINT_no_extensions and RV32I_CLINT_no_extensions have MTIME=1 and SIFIVE_CLINT=1. Only RISCV_no_extensions satisfies all three conditions. All four original headers were read with native web; the directory itself failed native retrieval but rendered in the browser. A solver can discover the satisfying header with ordinary search and verify it directly without enumerating the directory. The preceding V11.2.0 portContext.h was now read directly and contains neither FPU nor VPU macros, independently confirming the historical counterexample.

Scoring fixes: field-specific null synonyms; full interval grammar with uppercase hex and register aliases; malformed ranges rejected; syntactic substantive-response check requires a recognized scenario and numeric analysis. The scorer never certifies qualification: trajectory/access/exposure review is separately required. verify.py and verification.json now expose deterministic input fixtures and expected versus observed counts.

Manual/code division: store_x is sd for XLEN64 and sw for XLEN32; store_f is fsw for FLEN32 and fsd for FLEN64. Non-E allocation is the #else branch. SAVE_CONTEXT_INTERNAL tests FS/VS Dirty before the respective macros, invokes the selected extra-save macro, then saves sp in the first TCB member; SAVE_INTERRUPT_CONTEXT stores mepc before ISR-switch. These are semantic source judgments, not inferred from oracle values. No claim of byte-for-byte identity across fetch tools or of general instruction coverage is made.
