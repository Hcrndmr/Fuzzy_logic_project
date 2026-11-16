# References and how each one was checked

The IEEE-formatted list is in `report/refs.tex` (it is part of `report/report.pdf`).  The yönerge (§15) forbids
unverified or non-existent sources, so the status of every entry is recorded here.

| Status | Meaning |
|---|---|
| **P** | Bibliographic data copied from the reference list of the reference paper [1] (Soft Computing 28:7227-7249), which was read in full. The cited work itself was **not** opened. These works are cited only for what [1] says about them (Table 1 of the report). |
| **V** | Looked up online during this project; title, authors, venue, volume and DOI/article number were read from the publisher / index page. |
| **C** | Classic reference cited from memory for a textbook-level statement (definition of fuzzy sets, Sugeno model, PSO, DE, ...). Bibliographic data were **not** re-checked online: please look them up (e.g. Google Scholar) before submission. |

| Key | Reference | Status |
|---|---|---|
| ref_paper | Korkmaz & Akgüngör, Soft Comput. 28:7227-7249, 2024, doi 10.1007/s00500-024-09643-w | P (paper header, read in full) |
| korkmaz2021a | Korkmaz & Akgüngör, Soft Comput. 25:4243-4259, 2021 | P |
| dogan2016 | Doğan & Akgüngör, Simulation 92:1013-1023, 2016 | P |
| trabia1999 | Trabia, Kaseko, Ande, Transp. Res. C 7:353-367, 1999 | P |
| chen2006 | Chen & Xu, ICARCV 2006, pp. 1-7 | P |
| balaji2009 | Balaji & Srinivasan, IEEE FUZZ 2009, pp. 1627-1632 | P |
| bi2014 | Bi, Srinivasan, Lu et al., Expert Syst. Appl. 41:7338-7349, 2014 | P |
| araghi2017 | Araghi, Khosravi, Creighton, Nahavandi, Expert Syst. Appl. 71:493-503, 2017 | P |
| khooban2017 | Khooban et al., ISA Trans. 66:335-343, 2017 | P |
| lin2022, islam2022, zhao2022 | 2022 studies listed in Table 1 / reference list of [1] | P |
| zadeh1975, liang2000, askarzadeh2016, yang2012, hcm2000 | as listed in [1] | P |
| koukol2015 | Koukol, Zajíčková, Marek, Tuček, Math. Probl. Eng. 2015, 979160 (doi 10.1155/2015/979160) | V (IDEAS/RePEc record) |
| agrahari2024 | Agrahari et al., Electronics 13(19):3875, 2024 (doi 10.3390/electronics13193875) | V (MDPI page) |
| bi2024 | Bi, Ding, Du, Liu, Ren, Electronics 13(19):3894, 2024 (doi 10.3390/electronics13193894); Type-2 fuzzy controller + DQN, SUMO simulation; reports -19.4 % queue length, -18.9 % waiting time, -10.1 % delay vs DQN | V (MDPI page, section 4) |
| li2018nt | Li, John, Coupland, Kendall, IEEE TFS 26(2):1036-1039, 2018 (doi 10.1109/TFUZZ.2017.2666842) - analysis of the Nie-Tan operator | V (University of Stirling record). The *original* Nie & Tan (FUZZ-IEEE 2008) paper is deliberately not cited because its page numbers could not be verified. |
| mendel2017 | Mendel, *Uncertain Rule-Based Fuzzy Systems*, 2nd ed., Springer 2017 | V (publisher record) |
| zadeh1965, takagi1985, karnik2001, mantegna1994, kennedy1995, storn1997, webster1958 | classics | C |

Official code of the reference paper: none found; the authors' simulator KU-Trsim is not public. **No code from the
authors or from any third party was used**; all code in `src/` was written for this project (see the Generative AI
Usage Disclosure in the report for how it was produced).
