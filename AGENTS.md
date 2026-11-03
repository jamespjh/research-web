# Notes for agents working in this repo

This is the Jekyll source for https://research.jh.arc.ucl.ac.uk (theme `UCL-ARC/indigo-jekyll`). It is deployed by the sibling repo [jamespjh/jh-infrastructure](https://github.com/jamespjh/jh-infrastructure), normally checked out next to this one at `../jh-infrastructure`; read its `AGENTS.md` for how to reach the machines (VPN, kubectl contexts, ansible venv, AWS profiles).

## How a change gets deployed

1. Push to `main` runs `.github/workflows/build_site.yml`: a Jekyll build on GitHub-hosted runners. This only checks the site builds; its artifact is not what gets served.
2. On success, `.github/workflows/deploy.yml` dispatches `deploy_web.yml` in `jh-infrastructure`, using the `INFRA` secret (a fine-grained PAT).
3. `deploy_web.yml` runs on the self-hosted runner labelled `bootstrap` (the bootstrap VM). It checks out both repos and runs this repo's `ansible/web.yml` against `jh-infrastructure`'s Condenser inventory (`-i ../../ansible/inventory/sl-p02-kubevirt.yml`), failing if the inventory won't load.
4. This repo's `ansible/roles/web` role, on the `web` VM: clones this repo into `~/builds/<sha>`, builds it there with rbenv using the Ruby version in `.ruby-version`, copies `_site` to `/var/www/builds/research/<sha>/` (where SELinux labels it for Apache by default), repoints `/var/www/html/research` at that copy, and installs the Apache vhost (`files/web.conf`).
5. `deploy_tests/test_web.py` fetches the live site and checks for the `Introduction` heading.

So `.ruby-version` and `Gemfile` changes take effect on the server, not just in CI.

## Split of responsibilities

- Here: site content, the site's `web` role (clone, build, symlink, vhost) and the deploy test.
- In `jh-infrastructure`: the web VM itself and its base setup (`ansible/web.yml` with roles `jh-base`, `ruby`, `cloudflare`, and its own `web` role that installs httpd and the main `httpd.conf`), the inventory, and the deploy workflow. Both repos have a role called `web`; they are different.

## Running things locally

- Build the site: `bundle install && bundle exec jekyll build` (or `jekyll serve`).
- Run the playbook by hand from `ansible/`, using `jh-infrastructure`'s venv and inventory, e.g. `source ../../jh-infrastructure/ansible/.venv/bin/activate && ansible-playbook -i ../../jh-infrastructure/ansible/inventory/sl-p02-kubevirt.yml web.yml`. This changes the live site; ask before doing it.
- Run the deploy test: `cd deploy_tests && python -m venv test_venv && source test_venv/bin/activate && pip install -r requirements.txt && pytest test_web.py`.
