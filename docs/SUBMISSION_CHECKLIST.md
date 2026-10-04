# Submission checklist (manual steps for the team)

These steps cannot be done by the build scripts. Tick each one.

## Before recording

- [ ] Open Xathon **My Progress** and confirm the exact submission deadline (date, time and time zone).
      Plan to finish at least **30 minutes early**.
- [ ] Verify every assumption in `config.py` tagged `# ASSUMPTION - verify before submission`
      (see `docs/ASSUMPTIONS.md`): baseline depth and interval, pump head, pump efficiency,
      electricity tariff, grid emission factor, sensitivity heads.
      Record the source for each in `docs/ASSUMPTIONS.md` and change its status.
- [ ] If any assumption changes: run `python analyze.py && python build_deck.py` so README, video script,
      charts and deck update together. Run `pytest`.
- [ ] Replace `[TEAM NAME]` and `[MEMBERS]` on deck slide 1 (edit `build_deck.py` and rebuild, or edit the
      .pptx directly as the last step).

## Video

- [ ] Record the demo video following `docs/VIDEO_SCRIPT.md` (2 to 3 minutes).
- [ ] Confirm the video includes the sentence that the results are simulated.
- [ ] Upload the video where Xathon accepts it (or as an unlisted link if allowed) and check it plays
      while logged out.

## Repository

- [ ] Create a **public** GitHub repository and push this folder (`git remote add origin ...`, `git push -u origin main`).
- [ ] Open the repo page in a browser and confirm the README renders, including the three chart images
      and the tables.
- [ ] Confirm `results/`, `deck/SmartIrrigate_Deck.pptx` and `docs/` are in the pushed repo.

## Upload on Xathon

- [ ] Repository link
- [ ] Demo video
- [ ] Presentation deck (`deck/SmartIrrigate_Deck.pptx`, or a PDF export if required)
- [ ] Documentation (README link and/or `docs/` files) and impact measurement (`results/impact.json`,
      README results section)
- [ ] Confirm the submission shows as **completed** in My Progress. Screenshot it.
- [ ] Leave a **30-minute buffer** before the deadline for upload problems.
