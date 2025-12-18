# TTS Footnote Handling Logic Memo

## Core Design Principles

### 1. Visual and Auditory Decoupling Design
**Core Design Insight**: Human visual and auditory processing mechanisms have fundamental differences. E-book readers must adopt different processing strategies for these two senses.

- **Visual Processing**: When reading, humans have a wide field of view, and the brain can instantly recognize and ignore footnote markers `[7]`, directly connecting the preceding and following text.
- **Auditory Processing**: Auditory is a linear time flow, once sound is emitted, it cannot be taken back, and ears cannot "instantly skip" sound like eyes can.

### 2. Dual Role of the `〘7〙` Symbol
This Unicode symbol is not designed to conform to dictionary standards, but specifically as a "mute symbol":

- **Visual Preservation**: Display `〘7〙` on screen so readers know there's a footnote reference.
- **Auditory Filtering**: Completely delete during TTS synthesis, not uttering the sound "seven".
- **Program Logic**: Give the computer a clear instruction: whenever this special encoding is seen, "keep it when displaying, kill it when speaking".

## Physiological Mechanism Basis

### Visual Processing (Parallel Processing)
- Humans have a wide field of view when reading, able to process multiple visual elements simultaneously.
- The brain automatically categorizes in millisecond-level time: this is a footnote, this is supplementary information.
- Keeping markers visually is completely fine, and even has a prompting effect.

### Auditory Processing (Linear Processing)
- Auditory depends on time sequence, can only process one sound element at a time.
- Once sound is emitted, it's "spilled water", cannot be taken back.
- If "seven" is heard, the listener will try to integrate it into sentence semantics (become "ceremony ticket seven").
- Ears have no concept of "brackets", cannot automatically filter noise like eyes can.

## Design Conclusion

The current code logic completely conforms to human brain operation physiology:

**TUI display to satisfy visual marking, TTS deletion to match auditory linearity**

This is not for the computer's convenience, but to compensate for the physiological limitation that "auditory cannot filter noise like visual".

## Developer Notes

1. **Do not question this design**: This logic has been deeply analyzed and fully conforms to human cognitive science.
2. **Maintain visual-auditory decoupling**: Any modifications must consider both visual and auditory processing differences simultaneously.
3. **Test verification**: Ensure modifications do not break existing visual preservation/auditory filtering mechanisms.
4. **Backward compatibility**: New developers should understand and follow this core design principle.

## Related Code Locations

- `speakub/utils/text_utils.py`: `clean_text_for_tts()` function responsible for removing footnote markers.
- `speakub/tts/integration.py`: Text cleanup logic before TTS synthesis.
- Test cases: Ensure `〘7〙` is displayed in TUI but not pronounced in TTS.

---

**Final Conclusion**: This design is the correct implementation for e-book readers, fully based on human cognition and physiological mechanisms. Do not overturn this verified design with rigid logic.
