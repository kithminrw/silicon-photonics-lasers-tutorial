---
title: References
nav_order: 13
permalink: /references/
---

# References

This list is kept in [`_data/references.yml`](https://github.com/kithminrw/silicon-photonics-lasers-tutorial/blob/main/_data/references.yml); the numbers in the text are positions in that file. The tutorial cites these works and links to them; it does not reproduce their text or figures.

<ol class="references">
{%- for r in site.data.references %}
  <li id="ref-{{ r.key }}">{{ r.text | markdownify | remove: "<p>" | remove: "</p>" | strip }}</li>
{%- endfor %}
</ol>
