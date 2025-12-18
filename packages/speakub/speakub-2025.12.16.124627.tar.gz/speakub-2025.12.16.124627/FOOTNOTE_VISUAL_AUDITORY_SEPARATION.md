# Footnote Visual-Auditory Separation Design Logic Memo

## Core Design Principles

### 1. Visual and Auditory Should Be Decoupled by Nature
This is the smartest design point in the entire system:
- **Visual (TUI)**: Keep `〘7〙` on screen because human eyes need to know "there's a footnote here" when reading
- **Auditory (TTS)**: Completely delete sound because human ears hearing "footnote seven" when listening to books feels very noisy and disruptive

### 2. `〘 〙` Is Just a "Mute Symbol" for Computers to See
Developers chose this symbol to give the program a strict instruction:
- Whenever this special Unicode encoding wrapping numbers is seen, **keep it when displaying, but kill it when speaking**
- This is not to conform to any bullshit dictionary standards, simply to find a symbol **that humans absolutely won't use when reading novels**, as a "visual preservation, auditory filtering" marking tool

## Physiological Mechanism Basis

### Visual Processing (Parallel Processing)
When humans read, the field of view is broad. Eyes see `〘7〙`, the brain will determine in **millisecond-level** time "this is a footnote, this is supplementary information", then **automatically ignore** it, directly connecting the preceding and following text for understanding. This process is automatically completed by the brain, so visually keeping it is completely fine, and even has a prompting effect.

### Auditory Processing (Linear Processing)
Auditory is a **time flow**. Once sound is emitted, it's spilled water. If TTS reads "seven", the listener's immediate reaction will absolutely be trying to **integrate it into sentence semantics** (become "ceremony ticket seven"). **Ears have no concept of "brackets"**, listeners cannot "instantly skip" sound like eyes can. By the time the listener realizes "ah, that seven is a footnote", sentence coherence has already been interrupted, immersion has already been destroyed.

## Conclusion

The current code logic——**"TUI display to satisfy visual marking, TTS deletion to match auditory linear characteristics"**——completely conforms to human brain operation physiological mechanisms.

This is not for the computer's convenience, but to compensate for the physiological limitation that "auditory cannot filter noise like visual".

## Subsequent Maintenance Reminders

- Anyone modifying this logic, please carefully read the physiological mechanism basis above first
- If questioning this design, please refer back to the "human cognitive differences" angle, not from the data processing perspective
- This design is completely for serving human user experience (eyes can see, ears cannot hear)
- Don't try to fit it with rigid logic, spout a bunch of useless nonsense

## Implementation Details

- Use `clean_text_for_tts()` function to remove `〘7〙` symbols before TTS processing
- Keep symbols when displaying in TUI to provide visual hints
- This design is logically sound, and very practical
