# Example queries and expected outputs

**No sources uploaded:**
> "What is a neural network?"

Expected: a general, correct explanation from Claude's own training. Nothing gets retrieved,
since there's nothing in the store yet.

**After uploading a source file with facts Claude couldn't otherwise know**

I tested this with a text file describing a made-up project, "Project Zephyrine-9," with
invented details (a 94.7% recovery rate, a made-up inventor, etc).

> "What is Project Zephyrine-9 and what recovery rate does it achieve?"

Expected: the answer includes those specific invented details. If it does, that's proof the
answer came from the uploaded file, not a guess — there's no other way it could know a fact I
made up myself. This is the actual test I ran to confirm retrieval works, not just assumed.

**Query unrelated to any uploaded source**

Right now, if something's been uploaded but the question is about a different topic entirely,
the backend still retrieves and injects whatever chunks are "closest" in the store. Even if
they're not actually relevant, since there's no similarity cutoff yet. Claude is usually good
at noticing irrelevant context and ignoring it, but that's Claude compensating for a gap in the
retrieval logic, not something I've built and can guarantee. Documented as a known limitation
rather than pretended away; see [ARCHITECTURE.md](ARCHITECTURE.md).
