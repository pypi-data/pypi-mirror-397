# v0.1.15 (2025-12-18)
- allow assigning the `line_spacing` of each style to the element. This would allow for different elements with their respective line spacing.

# v0.1.14 (2025-12-2)
- Adding background to the frame, thanks to the advanced graphical options of `printpdf-rs`.


Other improvements over previous versions, in coordination with genpdf-json and rckive-genpdf:

Add footer

Allow the use of 3 paragraphs in the footer and header

Allow orphaned LinearLayout in the chosen position, avoiding warning.

Allowing Beak() with negative values.

Adjusting the try except block and enabling error output from pygenpdf-json.

Removing temporary files.

Fixing parameters in add fonts, styles, paragraph, text, among others.

Adjusting parameters in genpdf-json improvements:

Choosing which sides of the frame to display,

Style pattern for both frame and table layout lines,

Ability to position and orphan the text element (which has no alignment).

allow automatic font size adjustment with "with_fit_size_to", in case the length of the words or numbers is highly variable
The hyphenation "embed_en-us" was activated.

It was implemented that a word can be forcibly truncated if it doesn't have enough space in its environment, and if more space is needed, the second line is elided on the right.
