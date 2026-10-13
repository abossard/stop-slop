# Evidence

These sources back the analyzer signals and the clarity and visual rules. Strong means replicated, a meta-analysis, a large corpus or an official standard. Moderate means one good study. Practitioner means style guides, agent skills or lab policy.

## AI-writing signals

| Source | Signal | Citation |
|--------|--------|----------|
| Kobak et al. (2025) | AI vocabulary excess words, frequency ratios | *Science Advances* Vol.11 No.27; arXiv:2406.07016 |
| Opara (StyloAI, 2024) | TTR, hapax legomena ratio as top-4 features; contraction count | AIED 2024; arXiv:2405.10129 |
| Mahapatra (2026) | Language entropy collapse, punctuation suppression, distinct-N | arXiv:2605.28826 |
| Przystalski et al. (2025) | Stylometric features on short texts (10 sentences), grammatical standardization | *Expert Systems with Applications* 296; arXiv:2507.00838 |
| Ochab et al. (StylOch, 2025) | POS n-gram frequencies, dependency parse features | arXiv:2507.12064 |
| Aityan et al. (NEULIF, 2025) | Stylometric + readability features achieve 97% accuracy with 25MB CNN | arXiv:2511.21744 |
| chepdor2-ai/humara-s-clean-canvas | Calibrated thresholds for burstiness, Yule's K, hapax ratio, Guiraud's R | github.com/chepdor2-ai/humara-s-clean-canvas |
| Retengart/entropy-analysis | Yule's K, MTLD, burstiness B-index formulas | github.com/Retengart/entropy-analysis |
| Reinhart et al. (2025) | Present participle clauses, nominalizations and passive voice separate LLM from human text | *PNAS* 122, e2422455122; arXiv:2410.16107 |
| Muñoz-Ortiz et al. (2024) | LLM news text has longer dependency distances | *Artificial Intelligence Review* 57, 265; arXiv:2308.09067 |
| Geng & Trotta (2025) | Word lists decay: "delve" fell after its overuse was publicized | ACL Findings 2025; arXiv:2502.09606 |

Key findings:
- **Top 4 discriminating features** (Opara 2024): UniqueWordCount, StopWordCount, TTR, HapaxLegomenonRate
- **Kobak "common 10" words** whose aggregate frequency predicts LLM use: across, additionally, comprehensive, crucial, enhancing, exhibited, insights, notably, particularly, within
- **LLM text has collapsed entropy** (Mahapatra 2026): 1,949–16,853% amplification of certain patterns, complex punctuation suppressed to 3.2–23.2% of baseline

## Clarity

| Rule | Finding | Level | Source |
|------|---------|-------|--------|
| Average 15 to 20 words, split past 25 | Shorter average sentences improve comprehension; guides converge on 15 to 25 words | strong | Cook et al. 2023, [PLOS ONE](https://doi.org/10.1371/journal.pone.0282146); [GOV.UK style guide](https://www.gov.uk/guidance/style-guide); EU DGT Clear Writing; [Plain English Campaign](https://www.plainenglish.co.uk) |
| Rhythm as an AI tell only | No study shows that varied sentence length helps readers | unverified | Meister et al. 2021, [EMNLP](https://doi.org/10.18653/v1/2021.emnlp-main.74), has no sentence-length claim |
| Name the actor, passive when the object is the topic | Passive is slower on average and faster when the object is the topic | strong | Slobin 1966, [doi](https://doi.org/10.1016/S0022-5371(66)80023-3); Olson & Filby 1972, [doi](https://doi.org/10.1016/0010-0285(72)90013-8) |
| Zombie nouns | Nominalized sentences are harder to understand | strong | Coleman 1964, [doi](https://doi.org/10.1037/h0040440) |
| Negation tails | Negation adds a processing step | strong | Clark & Chase 1972, [doi](https://doi.org/10.1016/0010-0285(72)90019-9); Kaup et al. 2006, [doi](https://doi.org/10.1016/j.pragma.2005.09.012) |
| Subject-verb distance | Longer distance makes integration harder | strong | Gibson 1998, [doi](https://doi.org/10.1016/S0010-0277(98)00034-1); Grodner & Gibson 2005, *Cognitive Science* 29(2) |
| Plain words | Needlessly complex words lower judged author intelligence | strong | Oppenheimer 2006, [doi](https://doi.org/10.1002/acp.1178); swap list from [plainlanguage.gov Simple Words and Phrases](https://web.archive.org/web/20161223073724/http://www.plainlanguage.gov/howto/wordsuggestions/simplewords.cfm) and the [Plain English Campaign A to Z](https://web.archive.org/web/20200109034429/http://www.plainenglish.co.uk/files/alternative.pdf) |
| Adverbs: empty intensifiers and assertion adverbs only | No evidence against adverbs as a class; filler hedges cost credibility | weak | Hosman 1989, [doi](https://doi.org/10.1111/j.1468-2958.1989.tb00190.x); Durik et al. 2008, [doi](https://doi.org/10.1177/0261927X08317947) |
| Readability formulas as a comparison | FKGL R² 0.27, SMOG 0.32, Dale-Chall 0.31 on 4,724 texts | strong | Crossley et al. 2023, [doi](https://doi.org/10.3758/s13428-022-01802-x) |
| Readability formulas as a comparison | About half of 36 studies improved comprehension by chasing the score | strong | Klare 1976 via Redish 2000, *ACM J. Computer Documentation* 24(1) |
| Length follows information | Concise text scored 58% better on usability; concise, scannable and objective text scored 124% better | strong | [Morkes & Nielsen 1997](https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/) |
| Overview first, details after | Headings and previews improve memory for the content they cue | moderate | Lorch 1989, [doi](https://doi.org/10.1007/BF01320135) |
| Dropped: "8 words = 100% comprehension" | No primary source; absent from Gunning 1952 and American Press Institute archives | folklore | none found |

## Visuals

| Rule | Finding | Level | Source |
|------|---------|-------|--------|
| Diagram for linked steps and relations | Diagrams group related information by location and cut search | strong | Larkin & Simon 1987, [doi](https://doi.org/10.1111/j.1551-6708.1987.tb00863.x) |
| Arrows for sequence and causality | Arrows encode direction, time and cause | moderate | Tversky et al. 2000, [doi](https://doi.org/10.1007/3-540-44590-0_21) |
| Table for lookup, chart for trends | Tables fit point lookup; charts fit trends | strong | Vessey 1991, [doi](https://doi.org/10.1111/j.1540-5915.1991.tb00344.x); Cleveland & McGill 1984, *JASA* 79(387) |
| Tree or nested list for hierarchy; overview first | Tree and network data need their own overview and drill-down | strong | Shneiderman 1996, [doi](https://doi.org/10.1109/VL.1996.545307) |
| A visual must add information | A redundant second source hurts learning; decorative pictures add nothing | strong | Sweller et al. 2019, [doi](https://doi.org/10.1007/s10648-019-09465-5), Table 1; Carney & Levin 2002, [doi](https://doi.org/10.1023/A:1013176309260) |
| Headings as signals | Signaling helps a little, r = 0.17 over 27 studies | strong | Richter et al. 2016, [doi](https://doi.org/10.1016/j.edurev.2015.12.003) |
| Split Mermaid past 20 nodes | Above about 20 nodes, matrices beat node-link diagrams on most tasks | strong | Ghoniem et al. 2004, [doi](https://doi.org/10.1109/INFVIS.2004.1) |
| Few edge crossings | Edge crossings hurt graph reading most | moderate | Purchase 1997, [doi](https://doi.org/10.1007/3-540-63938-1_67) |
| Subgraph depth 2 | Working memory holds about 4 chunks | strong, applied by inference | Cowan 2001, [doi](https://doi.org/10.1017/S0140525X01003922) |
| Labels up to about 5 words, flag past 7 | Agent skills converge on 5 words per label | practitioner | [bentossell/visualise](https://github.com/bentossell/visualise) |
| Single fact as a sentence | A list or table needs more than one item | practitioner | [Microsoft Writing Style Guide](https://learn.microsoft.com/style-guide/scannable-content/lists) |
| Emoji and bold as AI tells | Named tells; Anthropic's system prompt avoids both by default | practitioner, lab policy | [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing); [Claude system prompts](https://platform.claude.com/docs/en/release-notes/system-prompts) |
| Why models over-format | Arena votes reward length and markdown; the same model scored 18.3 points apart by style alone | strong | [LMSYS style control 2024](https://lmsys.org/blog/2024-08-28-style-control/); arXiv:2406.11939 |
| Dropped: ADHD readers prefer visuals | No study found; learning-style matching is a known neuromyth | unverified | [Frontiers in Education 2023 review](https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2023.1147498/full) |

## Technical documentation

| Rule | Basis | Level | Source |
|------|-------|-------|--------|
| Explain design choices; reference recoverable source details | Comments should add non-obvious information; decision records preserve context and consequences | practitioner | [Ousterhout, Writing Comments](https://web.stanford.edu/~ouster/cgi-bin/cs190-spring16/lecture.php?topic=comments); [Nygard, Documenting Architecture Decisions](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions) |
| Keep needed contracts, instructions, and examples | Explanation, reference, and how-to guides serve different reader needs | practitioner | [Diataxis explanation](https://diataxis.fr/explanation/), [reference](https://diataxis.fr/reference/), and [how-to guides](https://diataxis.fr/how-to-guides/) |

These rules require source-aware review. The analyzer does not compare prose with code or verify design rationale.
