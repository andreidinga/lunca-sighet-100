# Lunca Sighet 100 — site static

Pagini statice generate din artifactele Claude ale casei, publicate pe GitHub Pages:
<https://andreidinga.github.io/lunca-sighet-100/>

| Pagina | Sursa (artifact) |
| --- | --- |
| `index.html` | Șantier Lunca Sighet 100 — `c19277be` |
| `jurnal.html` | Jurnal de șantier — `8b7c86f6` |
| `planse.html` | Planșe proiect — `30feb1be` |
| `instalatii.html` | Planșe instalații — `5eabaa01` |

## Cum se regenerează

1. Se descarcă `index.html` din fiecare artifact (tool-ul Artifact, `action: "read_file"`)
   într-un director cu subfolderele `index/`, `jurnal/`, `planse/`, `instalatii/`.
2. `python3 tools/build.py <dir_cu_html_brut> .`

Scriptul taie învelișul artifactului (tot până la `<body>` inclusiv și `</body></html>`
de la final), rescrie link-urile dintre pagini în căi relative, scoate
`target="_blank" rel="noopener"` și reîmpachetează cu un `<head>` propriu
(`noindex,nofollow`). La final verifică automat că nu a rămas niciun link
`claude.ai/code/artifact` și că nu apar prețuri sau buget în textul vizibil.

Actualizarea rulează zilnic la 9:20 și 18:20 (ora României) și face push doar dacă
s-a schimbat ceva.

`.nojekyll` este necesar ca GitHub Pages să servească fișierele ca atare, fără Jekyll.
