# Console screenshots

The screenshots in `public/screenshots/console/` are real gg console screens. `run.sh` drives the console in a pseudo-terminal against `fakeplane.py`, a fake control plane that serves invented example data (Example Org, Ada Lovelace, `example-org/web-app`), and `shoot.py` renders each screen as an SVG.

```sh
pip install pyte==0.8.2
scripts/console-screenshots/run.sh "$(command -v gg)"
```

- `shots.json` lists the keys pressed and the screens saved.
- The console never sees a real organisation's data, so the screenshots can be published as they are.
- After a gg release changes the console, rerun this and check every image before committing.
