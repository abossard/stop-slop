# Visuals

A visual must add information the prose does not state, or cut it. A visual adds information when it shows an order, a relation or a comparison that the reader would otherwise assemble from sentences. Default to prose.

## Choosing a representation

Pick the row that matches the structure of the content, not its topic.

| Content | Best representation | Source |
|---------|---------------------|--------|
| Sequence or process with branches | Flowchart or sequence diagram when 3 or more steps branch, merge or hand off between actors; a numbered list when the steps run straight | Larkin & Simon 1987; Tversky et al. 2000 |
| Comparison of 2+ items on 2+ attributes | Table | Vessey 1991 |
| Hierarchy | Tree diagram or nested list | Shneiderman 1996 |
| Relationships | Node-link diagram up to about 20 nodes, with few edge crossings; a matrix or table past that | Ghoniem et al. 2004; Purchase 1997 |
| Quantities or trends | Bar or line chart for a trend; a table for exact values | Cleveland & McGill 1984; Vessey 1991 |
| Single fact | One sentence | Microsoft Writing Style Guide |
| Causal argument | Prose; a diagram only for a chain of 3 or more linked causes | Tversky et al. 2000; Sweller et al. 2019 |
| Definitions | Prose under headings | Lorch 1989 |

See the README's Evidence section for full sources.

## Visual slop

| Pattern | Fix | `tools/analyze.py` finding |
|---------|-----|----------------------------|
| Decorative visual: a diagram, table or picture that restates the prose | Cut it, or make it carry the order, relation or comparison the prose lacks | Review by eye; tag it 🖼️ in the Wall of Shame |
| Mermaid diagram with 11 to 20 nodes | Keep only the nodes the reader needs | `Mermaid diagram has N nodes` |
| Mermaid diagram past 20 nodes | Split it, or switch to a table | `Split Mermaid diagram (N nodes)` |
| Node label line past 7 words (each `<br/>` line counts alone) | Aim for 5 words or fewer; move the rest into prose | `Mermaid label has more than 7 words` |
| Subgraphs nested deeper than 2 | Flatten or split the diagram | `Mermaid subgraph nesting exceeds depth 2` |
| Emoji on a heading, list marker or node label | Delete it; an emoji inside a sentence stays | `Emoji as decoration` |
| Bold on many phrases | Bold only what a skimming reader needs to find | `bold_density` metric, no finding |
| Three or more sequence words (first, then, next, finally) in one paragraph | Make a numbered list | `Steps in prose: use a numbered list` |
