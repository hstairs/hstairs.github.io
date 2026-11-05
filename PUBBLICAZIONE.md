# Pubblicazione su GitHub Pages

Account: **hstairs**. Repository previsto: **hstairs/hstairs.github.io**.

## Stato della preparazione

Il sito e il workflow sono pronti localmente. Il repository GitHub remoto e
l'attivazione di Pages devono ancora essere completati nell'account autenticato;
non sono stati creati o verificati. I record DNS di hstairs.com non sono cambiati.

## Primo caricamento

Una volta creato il repository **pubblico e vuoto** `hstairs.github.io` nell'account
`hstairs` (senza README, licenza o .gitignore generati da GitHub), aprire le sue
impostazioni **Settings → Pages → Source → GitHub Actions**.

Il repository locale è configurato affinché questo comando carichi il commit
preparato su `main` del repository remoto:

```sh
git push
```

Eseguirlo dalla cartella locale `Personal Webpage`. Il push richiede naturalmente
che Git sul computer sia autenticato a GitHub. Non ci sono credenziali nei file.
Non è stato eseguito alcun push da Codex.

Il workflow `.github/workflows/pages.yml` ricostruisce il sito con Python e
pubblica esclusivamente `public/`. Gli snapshot delle pagine di origine, il README
e gli script rimangono nel repository ma non sono inclusi nel sito pubblicato.
Il sito sarà disponibile su **https://hstairs.github.io/** a pubblicazione riuscita.

## Aggiornamenti successivi

Modificare `content/*.html`, poi:

```sh
python3 scripts/build.py
git add content public google-sites
git commit -m "Update website content"
git push
```

La verifica di migrazione `python3 scripts/verify.py` confronta il testo con il
vecchio sito: dopo modifiche intenzionali del contenuto può segnalare differenze.
Per questo non viene usata per bloccare gli aggiornamenti nel workflow.

## Collegamento di hstairs.com

Quando il sito su GitHub Pages funziona:

1. In GitHub, **Settings dell'account → Pages**, verificare `hstairs.com` con il
   record TXT fornito da GitHub. Il valore è specifico dell'account.
2. Nelle **Settings del repository → Pages → Custom domain**, impostare
   `hstairs.com`.
3. Nel pannello DNS del gestore del dominio, configurare questi record per il sito:

   | Nome | Tipo | Valore |
   | --- | --- | --- |
   | @ | A | 185.199.108.153 |
   | @ | A | 185.199.109.153 |
   | @ | A | 185.199.110.153 |
   | @ | A | 185.199.111.153 |
   | www | CNAME | hstairs.github.io |

   Conservare i record di posta e gli altri servizi. Eventuali record web A/AAAA
   incompatibili già presenti vanno riconciliati nel pannello del provider.
4. Attendere la verifica DNS e attivare **Enforce HTTPS** su GitHub Pages.

Con la pubblicazione tramite GitHub Actions il dominio va configurato nelle
impostazioni di Pages: un file CNAME nel repository non è necessario e non
sostituisce quella configurazione.

Documentazione ufficiale (verificata il 5 novembre 2026):
- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site

## Anteprima locale

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory public
```

Aprire **http://127.0.0.1:8000/index.html**. Pubblicazione e anteprima non richiedono
Node.js, npm o librerie Python aggiuntive.
