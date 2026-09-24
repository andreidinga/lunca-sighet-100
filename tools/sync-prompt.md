# Prompt pentru sarcina programată de sincronizare

Se rulează ca **routine** Claude Code (sarcină programată permanentă, în cloud):
<https://claude.ai/code/routines> → **New routine**.

| câmp | valoare |
| --- | --- |
| Repositories | `andreidinga/lunca-sighet-100` |
| Schedule | două declanșatoare zilnice: **9:20** și **18:20**, ora locală (se introduce ora locală, se convertește automat) — sau un cron `20 9,18 * * *` setat cu `/schedule update` dintr-un terminal local |
| Instructions | textul de sub linia orizontală, copiat integral |
| Connectors | niciunul — sincronizarea nu are nevoie de conectori |
| Environment | Default (Trusted) e suficient |

Fără setare de aprobare: routine-ele rulează autonom, fără prompturi de permisiune.
Rulările pornesc cu câteva minute întârziere față de ora fixată (stagger constant).

Fiecare rulare clonează repo-ul de la zero, de pe branch-ul implicit `main`.
Push-ul direct pe `main` e acceptat pentru că toate commit-urile de acolo sunt ale tale;
dacă `main` devine branch protejat, routine-ul nu va mai putea face push și promptul
trebuie schimbat să deschidă un PR dintr-un branch `claude/...`.

Textul de mai jos e de sine stătător — se copiază ca prompt („Instructions") al routine-ului.

---

Sincronizează site-ul static Lunca Sighet 100 cu ultima versiune a artifactelor.

Repo: `andreidinga/lunca-sighet-100`, branch `main`. Lucrează în clona locală a sesiunii.

**1. Descarcă HTML-ul brut al celor 6 artifacte.** Folosește tool-ul `Artifact` cu
`action: "read_file"` și `path: "index.html"` — NU `action: "read"`, care pentru pagini mari
returnează doar un fragment. Salvează fiecare artifact în subfolderul lui, într-un director
de lucru curat din scratchpad (de exemplu `<scratchpad>/raw/`):

| subfolder | artifact |
| --- | --- |
| `index/` | https://claude.ai/code/artifact/c19277be-c3ad-4d4d-be15-2f6724d8bf06 |
| `jurnal/` | https://claude.ai/code/artifact/8b7c86f6-01bc-422c-b485-a5659e6b8da4 |
| `planse/` | https://claude.ai/code/artifact/30feb1be-4f26-43d1-b971-3bb3360a3b9d |
| `instalatii/` | https://claude.ai/code/artifact/5eabaa01-5252-4b02-8e82-e504c36e313a |
| `randari/` | https://claude.ai/artifact/JNY9ydoCZZKjirvHU8GDW6 |
| `poze/` | https://claude.ai/artifact/Dj8kLEd6hurnXFohZkhFST |

Linkurile de artifact apar în două forme — `claude.ai/code/artifact/<uuid>` și
`claude.ai/artifact/<id scurt>`. Ambele sunt tratate de `tools/build.py`.

Artifactul „Casa Lunca Sighet 100" (`c028d713`) este **privat** — nu îl citi și nu îl publica.

**2. Rulează build-ul** din rădăcina repo-ului:

    python3 tools/build.py <director_raw> .

Scriptul taie învelișul artifactului (tot până la primul `<body>` inclusiv și
`</body></html>` de la final), rescrie link-urile `claude.ai/code/artifact/...` în căi
relative păstrând fragmentele, scoate `target="_blank" rel="noopener"` și reîmpachetează
fiecare pagină cu `<head>`-ul propriu, cu `noindex,nofollow`.

**3. Verifică.** Scriptul își verifică singur rezultatul și trebuie să scrie
`VERIFICARE OK` — adică niciun link `claude.ai/code/artifact` rămas, niciun
`target="_blank"`/`rel="noopener"`, și niciun preț (`€`, `EUR`, `lei`, `RON`, `buget`)
în textul vizibil. Dacă raportează orice problemă, **nu face commit și nu face push** —
oprește-te și spune exact ce a găsit.

**4. Push doar dacă s-a schimbat ceva.** Rulează `git status --porcelain`. Dacă e gol,
termină fără commit, fără push și fără mesaj — nu e nimic de raportat. Dacă sunt
modificări: commit cu mesajul `Actualizează paginile din artifacte (<data>)` și
`git push -u origin main`. Raportează pe scurt ce pagini s-au schimbat.

**5.** Dacă GitHub Pages e activat, confirmă și că
<https://andreidinga.github.io/lunca-sighet-100/> răspunde cu HTTP 200. Dacă domeniul
e blocat de politica de rețea a mediului, spune asta și treci mai departe — nu e o eroare.
