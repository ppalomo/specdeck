# The fonts, in the repository on purpose

Geist and Geist Mono, as the two variable files that cover every weight the interface uses.

They are here rather than fetched because Specdeck is a local tool that has to work with no
network: a font asked for over the wire either delays the first paint or changes the letters
under someone halfway through reading. The npm package that ships them wants Next.js as a
peer, which this client is not, so the two files it was wanted for are simply kept.

Licensed under the SIL Open Font License 1.1 — see `LICENSE.txt`, which travels with them.
Copyright (c) 2023 Vercel, in collaboration with basement.studio.
