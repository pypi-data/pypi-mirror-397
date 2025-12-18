# Footnote Handling Logic Memo

## Problem Background

In the SpeakUB e-book reader, we focus on processing HTML footnote markers in EPUB (usually marked with specific classes, such as footnote links or content). These markers are converted by ContentRenderer to a unified Unicode symbol `〘7〙` as internal representation.

However, when content is played through text-to-speech (TTS), directly reading out footnote numbers (such as "seven") would seriously disrupt the audiobook experience. To solve this problem, we designed a "visual preservation, audio filtering" mechanism.

**Why is this mechanism needed?**
- **Visual Reading**: Human eyes can quickly scan and ignore footnote markers, maintaining reading fluency.
- **Audio Playback**: Ears cannot "skip" sounds. Once TTS reads out footnotes, listeners will mistakenly integrate them into sentences, causing confusion.

The core of this design is recognizing **human visual and auditory cognitive differences** and optimizing the experience accordingly.

**Project Scope Limitations**:
- This mechanism only applies to footnote formats defined by the project (standard EPUB footnotes mainly based on HTML classes).
- Non-standard formats (such as `[1]` or other variants) are not processed, because the project assumes EPUB has been standardized.
- If EPUB does not comply with standards, please convert first through ContentRenderer or other tools.

## Mechanism Principles

### 1. Visual and Auditory Decoupling

We divide footnote processing into two independent pipelines:

- **Visual Pipeline (TUI Display)**: Completely display `〘7〙` on screen, letting readers know footnotes exist.
- **Auditory Pipeline (TTS Playback)**: Automatically delete `〘7〙` and its content to ensure clean audio output.

**Example**:
- Original text: "This is an important concept〘7〙."
- Visual display: This is an important concept〘7〙.
- TTS playback: "This is an important concept." (footnotes completely removed)

### 2. Technical Implementation: Mute Markers

We selected Unicode symbol `〘 〙` as "mute markers", giving the program a simple rule:
- **When displaying**: Preserve the symbol, let human eyes see the hint.
- **When playing**: Delete content when encountering this symbol to avoid interference.

**Why choose this symbol?**
- It rarely appears in novel reading, won't confuse with normal content.
- Computers only recognize binary, this symbol is purely a technical marker, not dictionary or language specification.

## Why Design This Way? (Based on Human Cognition)

### Advantages of Visual Processing
- **Parallel Processing**: When reading, the brain can simultaneously process entire page content, quickly identifying `〘7〙` as footnotes and automatically ignoring them.
- **Instant Judgment**: Completed in milliseconds, reading flows smoothly without obstacles.

### Limitations of Auditory Processing
- **Linear Processing**: Sound is a time sequence, playing word by word in order, cannot "fast-forward" to skip.
- **Lack of Bracket Concept**: Ears hearing "seven" will try to understand it as part of a sentence, for example becoming "coupon seven", breaking semantic coherence.
- **Cannot Go Back**: Sound disappears once uttered, too late when listeners realize it's a footnote.

**Actual Impact**:
- If TTS reads out footnotes: "This is an important concept seven." → Listener confused: "What is seven? Is it a number or footnote?"
- Immersion instantly shattered, audiobook experience greatly discounted.

### Conclusion: Physiology-Mechanism Oriented Design

This mechanism is not technical optimization, but based on human brain operation:
- **Visual**: Can automatically filter noise → Preserve markers.
- **Auditory**: Cannot filter → Delete markers.

This ensures eyes see hints, ears hear pure content, perfectly balancing both senses.

## Implementation Details

- **Program Logic**: Before TTS synthesis, scan content, remove all text surrounded by `〘...〙`.
- **User Experience**: Readers can freely switch between visual/audio modes for seamless experience.
- **Edge Cases**: If footnote content is longer, still apply same logic to avoid audio interference.

## Important Reminders

Before modifying this mechanism, please consider:
- Does it affect audiobook immersion?
- Reference cognitive science: visual parallel vs. auditory linear.
- Test TTS output to ensure no unexpected noise.

If in doubt, prioritize thinking "how humans perceive" rather than "how programs operate".

## Related Files
- Implementation Location: `speakub/core/content_renderer.py` (estimated, please search for footnote processing related code for actual location)
- Test Files: Related TTS tests under `tests/` directory

## Version History
- v1.0 (2025-11-29): Initial creation, record footnote handling logic to avoid future questions.
- v1.1 (2025-11-29): Polished content, strengthened "why establish mechanism" explanation, added actual examples and cognitive science basis.
- v1.2 (2025-11-29): Added project scope limitations, clarified mechanism only applies to standard EPUB footnote formats, avoid misunderstanding as universal compatibility design.
