# Study notes: Square Kufic sources (client-supplied)

## 1. Nihad Nadam: «تعلم الخط الكوفي المربع» (nihad.me/learn-arabic-square-kufic) and letter sheet (nihad.me/download/10793)
The article teaches method rather than geometry. Its priority order is text → letter structure and joins → negative space → dots
(«ابدأ بالنص الصحيح، ثم هيكل الحروف ووصلاتها، وبعدها اضبط الفراغ والنقاط»).

Rules adopted:
- **Grid:** choose one square module first. Making the stroke equal to the gap is a starting point, not a law (it cites al-Sabbagh, *Principles of Square Kufic*). Try a second version with a different gap and compare the eye of the mim and the spacing between words.
- **Non-joiners:** ا د ذ ر ز و never join the next letter. Never fill that gap with an extra stroke, and never let a decorative extension suggest a join that does not exist in the language.
- **Position forms:** a form that works alone may fail once joined, so test every letter in its real position.
- **Dots:** dots are distinguishing marks. Keep them, separate from the letter body, and check them in one colour. Colour must never be the only thing that separates a dot. Removing dots "may change the reading of a word". Many square-Kufic letters (ب ت ث ن ي) are identical apart from their dots.
- **Mim eye:** a counter that is too narrow or too wide is a common fault.
- **Composition:**
  - Do not force a phrase into a square if that disorders the word.
  - Symmetry ranks below word integrity.
  - Lengthening one leg or shortening another to balance the form is allowed, but the change must still make sense inside the word.
  - A frame alone does not make a composition.
- **Reading-path test:** draw arrows along the reading order, remove them, and check that the start and order are still clear. Rotation and repetition can hide the starting point.
- **Size test:** judge at final size and medium, not only enlarged. Ask a reader who has not seen the steps to read it.
- **Alif:** may be lengthened up or down as the design needs.

Letter sheet compared with the F.o.K.S. chart (`tools/foks.py`):
- و, ف/ق (initial/medial), ت/ن cups, final ه with top flag, final م (loop with a tail falling from the top-left), medial ه (two counters), ي medial (tooth with 2 dots below): **same construction** in both charts.
- ك: F.o.K.S. draws the inner hook as a separate stroke. Nihad's main form is a single connected "S" (top bar, left stub, middle bar, right drop, base). Both are valid. The one-piece form is safer at small sizes.
- Final ي: «LJ» body with 2 dots below. This is new, so it should be added and checked before use.

## 2. Free Islamic Calligraphy: Square Kufic gallery
A gallery page only, with no technical text and no licence terms on the listing. Subjects on page 1:
- Basmala (several)
- Four Qur'an chapters
- السلام عليكم
- Tasbih
- Al-Ikhlas 112:1–4
- Shahada (two)
- الله أكبر

Use it as general inspiration only. Nothing from it is copied.

## Pipeline changes resulting from this study
1. Add a **one-colour proof**: dots drawn in the ink colour, to confirm they still read through the gap alone.
2. Add a **small-size proof**: about 3 cm wide on screen.
3. Add a **reading-path proof**: arrows in reading order over the letters.
4. Treat ك as two documented constructions, and choose per design.
5. Keep the automated checks: sequence, joins, dot count and ownership, no false joins.
