# Must do items before publishing

- [X] Remove the `example_project` and supporting `docker-compose.[override.].yml`, `Dockerfile`, and `vendor`
- [X] Provide copyright and license info in the `README.md` with a copy of the `LICENSE`
- [X] Replace all references to `django_ssf_core` (do project search)

- [X] Add `app_name` to the urls to namespace them
- [X] Replace use of `project` context variable in templatetag that uses `list_techniques_for_tactic.html`
- [X] Remove all `outputcattle` or `metis` references
- [X] Remove use of `UpstreamProjectViewMixin`
- [X] Replace any oddly named paths, like `detail_by_collection_matrix` with `matrix_detail_by_collection`

- [X] Comb through the `README.md` for weird bits of information
- [X] Address all `FIXME` and `XXX` tags
- [X] Look at all `TODO` tags

- [X] Remove `noqa` and `flake8` comment tags
- [X] Tests are passing?

# Post-rework

- [X] Bring back pagination
- [X] Reproduce ordering of table results (removed because ordering is part of
django-ssf-core)

# Next release

- [X] Move `MitreIdentifiableMixin` classes in attack and mbc into the core package
- [ ] Add table header filter form (feature)

## Nice-to-have

- [X] Write the following as issues in github
- [-] Move `mitreattack_tags` templatetags to `django_mitre.core.templatetags.mitrecore.tags`
- [/] Correct the usage of the `markdown` templatetag to remove requirement to use `markdown | safe`
- [-] Replace `.gitlab-ci.yml` with the github actions equivalent
- [-] Provide minimal styling on the example (feature)
- [-] Convert tests to `pytest`
- [-] Upgrade MBC to use https://github.com/MBCProject/mbc-stix2.1

- [-] Look at allowing multiline load syntax `{% load \n\tX\n\tY\n from tt %}` in upstream django
