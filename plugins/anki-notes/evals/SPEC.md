# anki-notes eval spec

What the [`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals.md) suite in this folder tests, and what counts as passing. The case list below is generated from the case files by `gen_spec.py`; everything else here is written by hand.

## What it protects

The skill's job is to turn what Claude teaches into cards worth studying. The first cases each reproduce one mistake found while reviewing real cards by hand. The rest test the card-formulation checks, charter guide, questionnaire and note-type guide added from the spaced-repetition literature. A passing suite means none of those mistakes came back and the guides are followed.

The cases tagged `themes` cover deck themes: the look question in a new charter, drafting and building themes with `build_theme.py`, choosing font families, and saving or changing a theme's note types.

## How a run works

1. A fresh, headless Claude Code session starts with only this plugin and `ankimcp` loaded.
2. The Anki server is replaced by a mock (`mocks/anki/`): every Anki tool call gets a canned reply, and no real deck is touched. `_tools.json` holds the real server's tool descriptions so Claude sees the real tools.
3. The case's user message is sent, and Claude answers as it normally would.
4. Each grader checks one thing about that run and passes or fails.

Every case runs 3 times with the plugin and 3 times without it, on the plain model, to show what the plugin adds. All graders here apply to the with-plugin runs only.

## Scoring and the pass bar

- A run's score is the share of its graders that passed (all graders weigh the same). A case's score is the average over its runs.
- **Kinds of grader:**
  - **tool check:** whether an Anki tool was called, and how often.
  - **text search:** a pattern that must never appear in what Claude sent to the Anki tools. It sees every call, but understands nothing.
  - **LLM judge:** a model applies a plain-English rule and votes PASS or FAIL three times; the majority wins. It understands nuance, but sees only the first and last 12 messages of a transcript, which is why some rules also have a text search.
- **Pass bar: 1.00** for every case, which is the harness default: every grader passes in every run.
- The suite costs about $60 a run, so it runs by hand, not in CI. CI only checks that this file matches the cases.

## Not covered

- The Anki inbox doc itself: eval sessions have no docs tools. The no-Anki cases (`inbox-path`, `charter-away`, `charter-change-away`) mock every Anki tool as unreachable, so Claude falls back to giving the queued blocks in its reply, and the graders read them there. `charter-from-inbox` pastes the inbox contents into the prompt.
- The questionnaire through `AskUserQuestion`: headless eval runs drop that tool even when a case allows it, so the questionnaire cases grade the numbered-list fallback.
- Anything after the user's yes in a multi-turn flow (a case has one user message). Cases either test that nothing is written before the yes, or put the approval in the prompt.
- Whether the LLM judges agree with a human reviewer (see Ideas in the plugin README).
- `scripts/apply_stage.py` and the real AnkiMCP server.
- How a theme looks on a real phone (AnkiMobile).
- Fetching fonts: that is `fetch_font.py`'s job and has unit tests, and the eval sandbox usually can't run npm. The font cases grade the family names Claude chooses (in its `fetch_font.py --info` calls, theme.json drafts and reply), not whether they downloaded.

## Known failures

From the first full run (2026-11-20, overall 0.78, 23 of 49 cases passing) and a re-run of 16 cases after fixing the mocks. The scores of every run since are in `history.jsonl`; `record_run.py diff` shows the latest movement. To fix in later PRs; delete each line once its case passes.

**The skill is at fault:**

- `charter-save` (0.88): saves the deck, stages and charter but never syncs afterwards, though `charters.md` step 7 says to.
- `charter-lean` (0.50): drafts run well past 250 words, carrying note-type designs and long question lists. `charter-test-cases` (0.89) also leaves out the three test topics now and then.
- `charter-change-proposed` (0.78): fixes leeches that share a cause (prices, context sizes, rankings) card by card instead of proposing a charter change.
- `nt-field-change` (0.44): warns about the full sync correctly but never counts the notes that use the type, which `note-types.md` asks for first.
- `no-giveaway` (0.50): some fronts nearly answer themselves ("Is a score measured on the tuning examples too high or too low?").
- `one-right-answer` (0.50): most cards are tight scenarios, but a few why/what fronts allow several right answers.
- `q-why-work` (0.67): one run in three doesn't tie the charter to the user's work.

**The case or grader is at fault:**

- `no-lone-cards` (0.67): the criterion counts each cloze blank as a card, so 4 or 5 good cards from distinct angles fail the "two to four" limit. Count notes instead.
- `stale-fact` (0.50): the judge objects to numbers given in a scenario ("your context window is 1M tokens"); only an undated model figure in the answer should fail.
- `restate-then-draft` (0.50): the judge treats a two-blank cloze as mixing two points, but Anki makes one card per blank.
- `nt-repo` (0.87): the real `Reconocimiento` type already has a `Notas` field and back section, so Claude correctly changes nothing. Ask for a field that doesn't exist yet.
- `charter-away`, `charter-change-away` (0.00) and `inbox-path` (0.33): without Anki or the inbox, the skill says nothing was saved instead of showing the queued charter block. Left as is: a planned server-side Anki client will make the no-Anki path moot.

**Fixed in the mocks since that run, so re-check:**

- `charter-overlap` (0.75) never saw the AI Engineering charter: the fixture lookup rejects a deck name with a space. It passed once with an agent mock.

**Cause unknown:**

- `nt-propose` (0.67): proposals have a hint field, the answer typed once and a sample note, yet the judge fails all three runs. Re-run with `--keep-temp` to see which of its five rules fails.
- `nt-fill` (0.94) and `project-specific` (0.89): one run added no card.

## Running and updating

From the repo root:

```
claude plugin eval . --trust-plugin                    # the whole suite
claude plugin eval . --trust-plugin --case <name>      # one case
python3 -I plugins/anki-notes/evals/gen_spec.py        # after changing a case: regenerate the list below
python3 -I plugins/anki-notes/evals/record_run.py add evals/results/<time>/aggregate-result.json --note "<why>"
```

Most `themes` cases run `build_theme.py`, which needs shell and file tools that a case can't grant itself:

```
claude plugin eval . --trust-plugin --tag themes --allow-tools Write Bash
```

`history.jsonl` keeps every recorded run: when it started, the commit it measured, the Claude version, cost, and each case's score. Recording a run prints what moved since each case's last recorded score. Commit it with the change it measured.

## Cases

<!-- generated:start -->
| case | what it checks |
|---|---|
| [`ask-mode-deck`](#ask-mode-deck) | In a deck whose charter says Ask, cards are offered, not added. |
| [`charter-assumes`](#charter-assumes) | A charter's Assumes line stops prerequisite cards for basics the user already knows, but not for missing deck concepts. |
| [`charter-away`](#charter-away) | Away from Anki, an approved charter is queued as a charter block ahead of the cards for its deck. |
| [`charter-change-away`](#charter-change-away) | Away from Anki, a charter change is queued as the user's request, not as guessed charter text. |
| [`charter-change-consequences`](#charter-change-consequences) | Narrowing a charter's scope reports how many cards fall out and offers to tag them, without tagging first. |
| [`charter-change-minimal`](#charter-change-minimal) | A charter change touches only the relevant section and is shown, with the cards it affects, before saving. |
| [`charter-change-proposed`](#charter-change-proposed) | Leeches that share a charter-level cause lead to a proposed charter change, not a silent save. |
| [`charter-from-inbox`](#charter-from-inbox) | Emptying the inbox saves a queued charter first, without re-asking, then adds its cards. |
| [`charter-lean`](#charter-lean) | A draft charter is short, doesn't restate the skill's rules, marks overrides, and describes every stage. |
| [`charter-overlap`](#charter-overlap) | A new deck whose scope overlaps an existing one gets the overlap flagged and settled in both Out of scope sections. |
| [`charter-save`](#charter-save) | An approved charter creates the deck and every stage, saves the full text as Markdown, then syncs. |
| [`charter-test-cases`](#charter-test-cases) | A new charter is shown with three test topics, how it decides each, and a sample note card by card. |
| [`closed-list`](#closed-list) | A fixed list is never asked for whole; its members are carded one at a time or as one ordered cloze. |
| [`coined-term`](#coined-term) | A term coined in the session must not become a card's premise or answer. |
| [`doing-not-teaching`](#doing-not-teaching) | Helping with a task, as opposed to teaching a concept, makes no cards. |
| [`inbox-path`](#inbox-path) | Without Anki, drafted cards still pass the formulation checks and are reported as not saved. |
| [`language-disagree`](#language-disagree) | When the second reader questions a sentence in a language card, the disagreement goes to the user and neither version is added. |
| [`leech-first-rebuild`](#leech-first-rebuild) | A stage rebuild starts with the leech and marked cards and names the rule each rewrite fixes. |
| [`look-away`](#look-away) | Away from Anki, the queued charter carries the picked theme. |
| [`look-away-empty`](#look-away-empty) | Emptying a queued charter with a theme creates its note types before saving the description. |
| [`look-change`](#look-change) | Changing a theme recovers its spec from the CSS, rebuilds, previews, and applies to both note types only on a yes. |
| [`look-choices`](#look-choices) | Any feeling answer gets two or three distinct theme.json drafts, each built and previewed front and back. |
| [`look-cjk`](#look-cjk) | A Japanese deck keeps the system font (both fonts null) and still gets themed colors. |
| [`look-contrast`](#look-contrast) | A palette under 4.5:1 contrast fails the build, and Claude picks new colors and rebuilds instead of hand-writing CSS. |
| [`look-cyrillic`](#look-cyrillic) | A Russian deck's themes include the cyrillic subset and only families checked to have Cyrillic. |
| [`look-fill`](#look-fill) | Cards for a themed deck use its own Basic or Cloze copy with the stock fields. |
| [`look-font-literary`](#look-font-literary) | A deck of example sentences gets pairings whose body font is a text serif with italics on. |
| [`look-font-technical`](#look-font-technical) | An AI Engineering deck gets pairings with a sans body, at least one with a monospace label. |
| [`look-invert`](#look-invert) | A user who says studying makes them anxious gets calm themes with no motion, and the reply doesn't mirror the anxiety. |
| [`look-motion`](#look-motion) | Motion stays off on a pick until the user says yes after seeing it. |
| [`look-pairings`](#look-pairings) | Mixing one option's palette with another's fonts gives a theme with A's colors and B's font families, previewed in the deck's language. |
| [`look-question`](#look-question) | Creating a charter asks the look question once, in round two, optional, about both how studying feels and how it should feel. |
| [`look-repo`](#look-repo) | Theming a deck whose note types live in a repo proposes a change to the repo's stylesheet, not new or restyled note types. |
| [`look-save`](#look-save) | Saving a picked theme creates both note types from models.json, then the deck, with the charter naming them. |
| [`look-skip`](#look-skip) | Skipping the look question still gets themes drafted from the subject, with "none" offered. |
| [`metric-concept`](#metric-concept) | Teaching an AI-engineering concept in an Automatic deck should produce one-fact, self-contained cards with no arithmetic drills. |
| [`missing-prereq`](#missing-prereq) | A card may only rely on concepts the deck already teaches; missing ones are taught first or flagged. |
| [`name-the-options`](#name-the-options) | A two-option idea becomes a card that names both options in its question. |
| [`near-neighbor`](#near-neighbor) | When the deck holds a similar concept, the new card names what sets it apart, or a contrast card is added. |
| [`no-giveaway`](#no-giveaway) | A card's front must not hint at its answer through wording, an obviously right option or a visible cloze. |
| [`no-lone-cards`](#no-lone-cards) | A new concept in an Automatic deck gets two to four cards from different angles, not one. |
| [`nt-costs`](#nt-costs) | A note-type proposal that needs script says JavaScript isn't officially supported and asks for a test on every device. |
| [`nt-field-change`](#nt-field-change) | Adding a field counts the affected notes, warns about the full sync, and waits for a yes. |
| [`nt-fill`](#nt-fill) | A card in a deck with a custom note type uses the charter's default type and fills its fields as Conventions says. |
| [`nt-move-up`](#nt-move-up) | A word the user keeps getting wrong is recommended for production per the charter, and the user is told to move it. |
| [`nt-no-leak`](#nt-no-leak) | In a proposed note type, no card's front shows its own answer. |
| [`nt-none`](#nt-none) | A technical subject with varied card shapes stays on Basic and Cloze. |
| [`nt-propose`](#nt-propose) | A subject needing both recognition and production gets a well-designed note type proposed with a sample, not built. |
| [`nt-repo`](#nt-repo) | When note types live in a repo, changes are proposed as repo edits, not made in Anki. |
| [`nt-reuse`](#nt-reuse) | When the collection already has fitting note types, the charter reuses them with a default and a move-up rule. |
| [`one-right-answer`](#one-right-answer) | A front that several correct answers would fit gets the context that leaves only one. |
| [`open-set`](#open-set) | Members of an open set are carded by what they do; no card asks for the whole set or for an example of the category. |
| [`procedure`](#procedure) | A procedure is carded at its decision points, not as a sequence of steps or commands. |
| [`project-specific`](#project-specific) | Lessons learned in a project become general cards without the project's names. |
| [`q-how-class`](#q-how-class) | When new material comes from conversation classes, the charter sources cards from phrases met in class. |
| [`q-how-kindle`](#q-how-kindle) | When new material comes from the user's reading, the charter sources cards from sentences they met there. |
| [`q-no-tool`](#q-no-tool) | Setting up a deck starts with the four-question questionnaire, as a numbered list with options, before anything is drafted or written. |
| [`q-second-round`](#q-second-round) | The follow-up questions after a draft are few and never repeat the first round. |
| [`q-skip-answered`](#q-skip-answered) | Questions the user already answered are not asked again. |
| [`q-traceable`](#q-traceable) | Every questionnaire answer shows up in at least one line of the drafted charter. |
| [`q-why-exam`](#q-why-exam) | When the user studies for an exam, the charter's scope and stages follow the syllabus. |
| [`q-why-work`](#q-why-work) | When the user learns for work, the charter selects by what changes how they work, not by a syllabus. |
| [`regression`](#regression) | Known-bad drafts are rewritten into the reviewed good shapes, and paired-relationship clozes are left alone. |
| [`rescued-tag`](#rescued-tag) | A stage rebuild tags each rewritten leech `rescued` in the plan. |
| [`restate-then-draft`](#restate-then-draft) | A multi-point explanation becomes cards that each test exactly one point. |
| [`source-question`](#source-question) | Cards about something read in an article ask about the subject, never about what the article said. |
| [`stale-fact`](#stale-fact) | An answer that depends on a date, model or benchmark says so in the question, or the card tests the durable principle instead. |
| [`support-missing`](#support-missing) | A card whose answer the source passage doesn't state is not added, even when the fact is true. |
| [`support-reversed`](#support-reversed) | A drafted card that reverses what its source passage says is held and shown to the user, not added or reworded to fit. |
| [`variety-image-giveaway`](#variety-image-giveaway) | A diagram whose visible label gives away the answer is not put on the card's front. |
| [`variety-mnemonic`](#variety-mnemonic) | A mnemonic is offered for an arbitrary fact and not for a fact the learner can reason out. |
| [`variety-none`](#variety-none) | A charter with "Variety: none" keeps every new card in the deck's one format. |
| [`variety-one-shape`](#variety-one-shape) | Content with one right shape keeps it even when that shape is the deck's most common format. |
| [`variety-scenario`](#variety-scenario) | In a deck where 95% of notes are plain definitions, content that fits a definition or a scenario equally well gets a scenario. |
| [`yes-no-rewrite`](#yes-no-rewrite) | A fact that invites a yes/no question becomes a what, why or which question. |

### ask-mode-deck

In a deck whose charter says Ask, cards are offered, not added.

**User message:**

> In Spanish, what's the difference between ser and estar?

**Deck:** the shared mock deck, with this case's own `get_deck_description`.

| grader | kind | passes when |
|---|---|---|
| `no-cards` | tool check | `add_notes` is never called |
| `offers-cards` | LLM judge, reads the final reply | PASS if the reply answers the question and offers to make Anki cards (in any wording), without claiming any were added. FAIL if it says cards were added, or never mentions making cards. |

### charter-assumes

A charter's Assumes line stops prerequisite cards for basics the user already knows, but not for missing deck concepts.

**User message:**

> Explain what an F1 score is.

**Deck:** the shared mock deck, with this case's own `get_deck_description`.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `no-basics-in-calls` | tool check | `add_notes` with input matching `[wW][hH][aA][tT] [iI][sS] ([aA] \|[aA][nN] \|[tT][hH][eE] )?([aA][rR][iI][tT][hH][mM][eE][tT][iI][cC] )?([mM][eE][aA][nN]\|[mM][eE][dD][iI][aA][nN]\|[rR][aA][tT][iI][oO]\|[pP][eE][rR][cC][eE][nN][tT][aA][gG][eE]\|[aA][vV][eE][rR][aA][gG][eE])\\b` is never called |
| `respects-assumes` | LLM judge, reads the transcript | The deck's charter says it assumes basic statistics (mean, median, ratio, percentage), and the deck has no cards on precision or recall. Look at the cards in every add_notes call. PASS if no card teaches mean, average, ratio or percentage as a concept of its own, and either cards introducing precision and recall are added before or with the F1 cards, or the reply says they're missing. FAIL if a card teaches a basic statistics term, or F1 cards rely on precision and recall with no card or note about them. |

### charter-away

Away from Anki, an approved charter is queued as a charter block ahead of the cards for its deck.

**User message:**

> Set up an Anki deck for Spanish. Why: I'm moving to Madrid next year. How: I read novels on my Kindle with lookups and review on my phone. What I know: I'm about B1 and comfortable with the present and past tenses. And I need both to understand Spanish and to speak it. I already approved this charter in another chat, use it as is:
>
> ## Scope
> Spanish for living in Madrid: everyday grammar, common verbs, and words met in reading. In: verb tenses, ser vs estar, por vs para.
>
> Assumes: present and past tense forms.
>
> ## Out of scope
> Latin American slang (nowhere). Travel logistics (looked up).
>
> ## Adding
> Ask.
>
> ## Stages
> `01 Sounds and spelling` — accents and stress.
> `02 Present tense` — irregular verbs, ser/estar and por/para.
> `03 Past tenses` — preterite vs imperfect.
>
> ## Conventions
> - Prefer cloze sentences from my reading.
> - Tags: `es::<area>::<topic>`.
>
> Then make two cards in it: ser vs estar for a location (estar), and por vs para for a deadline (para).

**Deck:** the shared mock deck, with this case's own `add_notes`, `card_reposition`, `create_deck`, `create_model`, `find_notes`, `get_deck_description`, `list_decks`, `model_field_add`, `model_field_names`, `model_field_rename`, `model_field_reposition`, `model_names`, `model_templates`, `notes_info`, `sync`, `tag_add`, `update_deck_description`, `update_model_styling`, `update_model_templates`, `update_note_fields`.

| grader | kind | passes when |
|---|---|---|
| `charter-block` | text search | the final reply contain `\"charter\"\\s*:` |
| `charter-first` | LLM judge, reads the final reply | Anki and the Anki inbox doc are both unreachable in this run, so queued blocks end up in the reply. PASS if the reply contains a json block of the form {"charter": {"deck": "Spanish", ...}} with the approved charter text, it comes before any card block for the Spanish deck, and the reply says nothing was saved to Anki or the inbox. FAIL if there is no charter block, a card block comes before it, or the reply claims the deck or cards were created. |

### charter-change-away

Away from Anki, a charter change is queued as the user's request, not as guessed charter text.

**User message:**

> Add slang to my Spanish deck's out-of-scope section.

**Deck:** the shared mock deck, with this case's own `add_notes`, `card_reposition`, `create_deck`, `create_model`, `find_notes`, `get_deck_description`, `list_decks`, `model_field_add`, `model_field_names`, `model_field_rename`, `model_field_reposition`, `model_names`, `model_templates`, `notes_info`, `sync`, `tag_add`, `update_deck_description`, `update_model_styling`, `update_model_templates`, `update_note_fields`.

| grader | kind | passes when |
|---|---|---|
| `change-block` | text search | the final reply contain `\"charter_change\"\\s*:` |
| `users-words` | LLM judge, reads the final reply | Anki and the Anki inbox doc are both unreachable in this run, so the queued block ends up in the reply. PASS if the reply contains a json block {"charter_change": {"deck": "Spanish", "request": ...}} whose request keeps the user's own wording, and the reply doesn't invent the current or new charter text. FAIL if there is no charter_change block, or the reply writes out a guessed full charter or section text. |

### charter-change-consequences

Narrowing a charter's scope reports how many cards fall out and offers to tag them, without tagging first.

**User message:**

> Narrow my Spanish deck to grammar only. No more vocabulary cards.

**Deck:** the shared mock deck, with this case's own `find_notes`, `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `no-save-before-yes` | tool check | `update_deck_description` is never called |
| `no-tags-before-yes` | tool check | `tag_add` is never called |
| `reports-five` | LLM judge, reads the final reply | The deck holds five vocabulary cards (madrugar, la sobremesa, aprovechar, el atasco, empeñarse en). PASS if the reply says five existing cards fall outside the narrowed scope (or lists those five), offers to tag them `to-delete`, and asks before saving the charter or tagging anything. FAIL if it doesn't report the affected cards, gives the wrong count, or says it already tagged or saved anything. |

### charter-change-minimal

A charter change touches only the relevant section and is shown, with the cards it affects, before saving.

**User message:**

> Change my Spanish deck's charter so it stops carding regional slang.

**Deck:** the shared mock deck, with this case's own `find_notes`, `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `minimal-shown` | LLM judge, reads the final reply | The current charter puts "colloquial and regional slang (Spain and Latin America)" in Scope, and the deck has four slang cards (guay, chido, pana, currar). PASS if the reply shows the old and new text of only the section(s) that change (Scope and/or Out of scope), leaves every other line as it was, says how many existing cards the change affects or offers to tag them `to-delete`, and asks before saving. FAIL if it rewrites unrelated sections, doesn't show old and new text, or doesn't mention the existing slang cards. |
| `no-save-before-yes` | tool check | `update_deck_description` is never called |
| `reads-charter` | tool check | `get_deck_description` is called at least once |

### charter-change-proposed

Leeches that share a charter-level cause lead to a proposed charter change, not a silent save.

**User message:**

> I keep failing some cards in my AI Engineering deck. Can you look at my leeches and tell me what's going on?

**Deck:** the shared mock deck, with this case's own `find_notes`, `notes_info`.

| grader | kind | passes when |
|---|---|---|
| `no-save` | tool check | `update_deck_description` is never called |
| `proposes-change` | LLM judge, reads the final reply | The deck's three leeches are a model price, a model's context-window size and a leaderboard position. PASS if the reply names one shared cause at the charter level (the charter doesn't keep fast-changing, model-specific figures like prices, context sizes and rankings out of scope, or doesn't require dating them) and proposes a specific charter change for it, asking before saving. FAIL if it only rewrites or reschedules the three cards, names no shared cause, or says it saved a charter change. |
| `reads-leeches` | tool check | `find_notes` with input matching `tag:leech` is called at least once |

### charter-from-inbox

Emptying the inbox saves a queued charter first, without re-asking, then adds its cards.

**User message:**

> Empty my Anki inbox. The docs tools aren't available here, so here's everything that's in it:
>
> ```json
> {"charter": {"deck": "Spanish", "stages": ["01 Sounds and spelling", "02 Present tense", "03 Past tenses"], "description": "## Scope\nSpanish for living in Madrid: everyday grammar, common verbs, and words met in reading. In: verb tenses, ser vs estar, por vs para.\n\nAssumes: regular present and past conjugations.\n\n## Out of scope\nLatin American slang (nowhere). Travel logistics (looked up).\n\n## Adding\nAsk.\n\n## Stages\n`01 Sounds and spelling` — accents and stress.\n`02 Present tense` — irregular verbs, ser/estar and por/para.\n`03 Past tenses` — preterite vs imperfect.\n\n## Conventions\n- Prefer cloze sentences from my reading.\n- Tags: `es::<area>::<topic>`."}}
> ```
>
> ```json
> {"deck": "Spanish", "stage": null, "model": "Cloze", "fields": {"Text": "La farmacia {{c1::está}} al final de la calle.", "Extra": "estar: location"}, "tags": ["es::grammar::ser-estar", "type::application"]}
> ```

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `adds-card` | tool check | `add_notes` is called at least once |
| `charter-before-cards` | tool check | `update_deck_description` is first called before `add_notes` |
| `deck-before-cards` | tool check | `create_deck` is first called before `add_notes` |
| `saves-charter` | tool check | `update_deck_description` is called at least once |

### charter-lean

A draft charter is short, doesn't restate the skill's rules, marks overrides, and describes every stage.

**User message:**

> Set up an Anki deck for Spanish. Why: I'm moving to Madrid next year. How: I read novels on my Kindle with lookups and review on my phone. What I know: I'm about B1 and comfortable with the present and past tenses. And I need both to understand Spanish and to speak it. Show me the draft.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `lean` | LLM judge, reads the final reply | Judge only the draft charter text in the reply, not the explanation around it. PASS if the charter is roughly 250 words or fewer, doesn't restate general card-writing rules (one fact per card, self-contained fronts, no yes/no questions), starts any line that overrides a general rule with `Overrides:`, and gives every stage a one-line description of what it covers. FAIL if it is clearly longer than about 300 words, repeats general card rules, or lists a stage with no description. |
| `no-save-yet` | tool check | `update_deck_description` is never called |

### charter-overlap

A new deck whose scope overlaps an existing one gets the overlap flagged and settled in both Out of scope sections.

**User message:**

> Set up an Anki deck for Python. I use it at work every day to build data pipelines and LLM eval tooling, I study on my phone, I know the basics, and I need to write it, not just read it. Show me the draft before creating anything.

**Deck:** the shared mock deck, with this case's own `get_deck_description`.

| grader | kind | passes when |
|---|---|---|
| `flags-overlap` | LLM judge, reads the final reply | The existing AI Engineering charter covers the Python tooling used to build AI systems (pandas, Pydantic, async API clients). PASS if the reply points out that the Python deck would overlap AI Engineering on that tooling, asks or proposes which deck owns it, says the overlap goes in both decks' Out of scope, and the draft's tag prefix is not `aie`. FAIL if the overlap isn't mentioned, or the draft claims the same topics as AI Engineering without settling which deck owns them. |
| `no-deck-yet` | tool check | `create_deck` is never called |
| `no-save-yet` | tool check | `update_deck_description` is never called |
| `reads-charters` | tool check | `get_deck_description` is called at least once |

### charter-save

An approved charter creates the deck and every stage, saves the full text as Markdown, then syncs.

**User message:**

> Yes, that charter looks right. Save it for my new Spanish deck exactly as below.
>
> ## Scope
> Spanish for living in Madrid: everyday grammar, common verbs, and words met in reading. In: verb tenses, ser vs estar, por vs para.
>
> Assumes: present and past tense forms.
>
> ## Out of scope
> Latin American slang (nowhere). Travel logistics (looked up).
>
> ## Adding
> Ask.
>
> ## Stages
> `01 Sounds and spelling` — accents and stress.
> `02 Present tense` — irregular verbs, ser/estar and por/para.
> `03 Past tenses` — preterite vs imperfect.
>
> ## Conventions
> - Prefer cloze sentences from my reading.
> - Tags: `es::<area>::<topic>`.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `creates-deck` | tool check | `create_deck` with input matching `\"deck_name\":\\s*\"Spanish\` is called at least once |
| `creates-stage-01` | tool check | `create_deck` with input matching `Spanish::01 Sounds and spelling` is called at least once |
| `creates-stage-02` | tool check | `create_deck` with input matching `Spanish::02 Present tense` is called at least once |
| `creates-stage-03` | tool check | `create_deck` with input matching `Spanish::03 Past tenses` is called at least once |
| `deck-before-description` | tool check | `create_deck` is first called before `update_deck_description` |
| `saves-full-text` | tool check | `update_deck_description` with input matching `Out of scope[\\s\\S]*03 Past tenses[\\s\\S]*Tags` is called at least once |
| `saves-markdown` | tool check | `update_deck_description` with input matching `\"is_markdown\":\\s*true` is called at least once |
| `syncs-after` | tool check | `update_deck_description` is first called before `sync` |

### charter-test-cases

A new charter is shown with three test topics, how it decides each, and a sample note card by card.

**User message:**

> Set up an Anki deck for Spanish. Why: I'm moving to Madrid next year. How: I read novels on my Kindle with lookups and review on my phone. What I know: I'm about B1 and comfortable with the present and past tenses. And I need both to understand Spanish and to speak it. Show me the draft.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `no-deck-yet` | tool check | `create_deck` is never called |
| `no-save-yet` | tool check | `update_deck_description` is never called |
| `tests-shown` | LLM judge, reads the final reply | PASS if, along with the draft charter, the reply shows three example topics (one clearly in scope, one borderline, one adjacent but out), says how the charter's text decides each, and shows one sample note as each of its cards would appear (front and back). The sample cards follow the usual card rules: one fact per answer, self-contained, not answerable yes/no. FAIL if any of the three test topics, the decisions, or the sample note is missing. |

### closed-list

A fixed list is never asked for whole; its members are carded one at a time or as one ordered cloze.

**User message:**

> Explain the four cells of a confusion matrix.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `no-name-all-in-calls` | tool check | `add_notes` with input matching `\\b([nN][aA][mM][eE]\|[lL][iI][sS][tT]\|[wW][hH][aA][tT] [aA][rR][eE]) ([aA][lL][lL]\|[tT][hH][eE]\|[iI][tT][sS]) ([fF][oO][uU][rR]\|4)\\b` is never called |
| `one-per-card` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if no card asks for the whole list ("name the four cells"). Each cell that gets a card is asked for on its own, by what it means; or all four sit in one Cloze note with one blank per cell, in a fixed order, where the visible cells don't give a blank away. FAIL if any card asks for two or more cells in one answer, or asks for the set as a whole. |

### coined-term

A term coined in the session must not become a card's premise or answer.

**User message:**

> On my team we've started calling the run-to-run wobble in eval scores the "jitter band". Explain why a prompt change that gains 2 points might not be real when reruns of an unchanged prompt move the score by 3 points.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `no-coined-term-in-calls` | text search | the inputs sent to the mocked Anki tools never contain `jitter band` (case-insensitive) |
| `no-coined-term` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if no card uses the phrase "jitter band" (in its question, answer or cloze), and the lesson is stated in plain words, such as run-to-run variation. FAIL if any card uses "jitter band", or asks for it as a term to recall. |

### doing-not-teaching

Helping with a task, as opposed to teaching a concept, makes no cards.

**User message:**

> My tmux status bar shows the time in UTC instead of my local time. What do I put in tmux.conf to fix it?

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `no-cards` | tool check | `add_notes` is never called |

### inbox-path

Without Anki, drafted cards still pass the formulation checks and are reported as not saved.

**User message:**

> Explain what LLM-as-a-judge is, and why judge models tend to prefer longer answers. Add it to my AI Engineering deck in Anki.

**Deck:** the shared mock deck, with this case's own `add_notes`, `card_reposition`, `create_deck`, `create_model`, `find_notes`, `get_deck_description`, `list_decks`, `model_field_add`, `model_field_names`, `model_field_rename`, `model_field_reposition`, `model_names`, `model_templates`, `notes_info`, `sync`, `tag_add`, `update_deck_description`, `update_model_styling`, `update_model_templates`, `update_note_fields`.

| grader | kind | passes when |
|---|---|---|
| `drafts-pass` | LLM judge, reads the final reply | Anki and the Anki inbox doc are both unreachable in this run, so Claude should give the drafted cards in its reply. PASS if the reply contains drafted cards, says they weren't saved to Anki or the inbox, and every drafted card has a question that can't be answered yes/no, doesn't give its answer away, asks for one item rather than a list, and has exactly one right answer. FAIL if there are no drafts, the reply claims the cards were added or queued, or any draft breaks one of those checks. |

### language-disagree

When the second reader questions a sentence in a language card, the disagreement goes to the user and neither version is added.

**User message:**

> Yes, add these to Spanish, I've already looked them over:
>
> 1. Cloze: Si {{c1::tuviera}} tiempo, iría contigo.
> 2. Cloze: Si {{c1::tendría}} dinero, me compraría un coche.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-undisputed` | tool check | `add_notes` is called at least once |
| `neither-version-added` | text search | the inputs sent to the mocked Anki tools never contain `tendr[ií]a\\}\\} dinero\|tuviera\\}\\} dinero` (case-insensitive) |
| `reports-disagreement` | LLM judge, reads the final reply | Card 2 uses the conditional after "si" ("Si tendría dinero"), which standard Spanish rejects (the imperfect subjunctive "tuviera" is standard) though some regions use it in speech. PASS if the reply shows card 2 as questioned, gives both the draft and the suggested wording, and leaves the choice to the user. FAIL if the reply reports card 2 as added in either form, or silently drops or rewrites it. |

### leech-first-rebuild

A stage rebuild starts with the leech and marked cards and names the rule each rewrite fixes.

**User message:**

> Please rebuild the 01 Classification metrics stage of my AI Engineering deck. Some of those cards just aren't working for me.

**Deck:** the shared mock deck, with this case's own `find_notes`, `notes_info`.

| grader | kind | passes when |
|---|---|---|
| `leeches-first` | LLM judge, reads the final reply | The stage has a leech card ("Precision vs recall?") and a marked card ("Why F1?"). PASS if the plan Claude shows deals with those two cards first, and for each rewrite it names the rule the old card broke (for example: two facts in one answer, a vague question, no named options). FAIL if the plan doesn't single out the leech and marked cards, or rewrites them without saying which rule each fix addresses. |
| `no-adds-before-review` | tool check | `add_notes` is never called |
| `no-writes-before-review` | tool check | `update_note_fields` is never called |
| `searches-problem-cards` | tool check | `find_notes` with input matching `tag:leech\|tag:marked` is called at least once |

### look-away

Away from Anki, the queued charter carries the picked theme.

**User message:**

> We're setting up my new Portuguese deck. You already drafted its charter and I approved it:
>
> ## Scope
> European Portuguese for living in Lisbon: everyday conversation, pronunciation, core grammar, high-frequency vocabulary.
>
> Assumes: fluent Spanish, no Portuguese.
>
> ## Out of scope
> Brazilian-only usage. Business and legal Portuguese.
>
> ## Adding
> Ask: offer cards and add them only after a yes.
>
> ## Stages
> - `01 Sounds and spelling`: vowels, nasal sounds and how spelling maps to them.
> - `02 Present tense`: regular and common irregular verbs in the present.
>
> ## Conventions
> - Basic and Cloze.
> - Tags: `pt::<area>::<topic>`.
>
> The sample note was Front "Portuguese: how do you say 'I'm leaving tomorrow'?", Back "<b>Vou embora amanhã.</b>".
>
> Second round: Ask mode, Basic and Cloze. I pick this theme, motion off. Save the deck.
>
> ```json
> {"deck": "Portuguese", "mood": "warm, unhurried", "subsets": ["latin", "latin-ext"],
>  "fonts": {"body": null, "accent": null},
>  "light": {"bg": "#FBF3E8", "text": "#3B2316", "accent": "#A24A26", "rule": "#E8CDB4"},
>  "night": {"bg": "#221A15", "text": "#F3E6D8", "accent": "#F0A07A", "rule": "#4A3A30"}}
> ```

**Deck:** the shared mock deck, with this case's own `add_notes`, `card_reposition`, `create_deck`, `create_model`, `find_notes`, `get_deck_description`, `list_decks`, `model_field_add`, `model_field_names`, `model_field_rename`, `model_field_reposition`, `model_names`, `model_styling`, `model_templates`, `notes_info`, `store_media_file`, `sync`, `tag_add`, `update_deck_description`, `update_model_styling`, `update_model_templates`, `update_note_fields`.

| grader | kind | passes when |
|---|---|---|
| `queued-charter` | LLM judge, reads the final reply | PASS if the reply gives one json block of the form {"charter": {"deck": ..., "stages": [...], "description": ..., "theme": {...}}} with the full approved charter text and the picked theme (not null), and says it couldn't be saved to Anki yet. FAIL if the theme is missing or null, the charter is split across several blocks, or Claude claims it saved anything to Anki. |
| `theme-in-block` | text search | the final reply contain `"charter"\s*:[\s\S]*"theme"\s*:\s*\{` |

### look-away-empty

Emptying a queued charter with a theme creates its note types before saving the description.

**User message:**

> Anki is open now. Empty my Anki inbox. Here is everything under "Queued cards" in it:
>
> ```json
> {"charter": {"deck": "Portuguese", "stages": ["01 Sounds and spelling", "02 Present tense"], "description": "## Scope\nEuropean Portuguese for living in Lisbon: everyday conversation, pronunciation, core grammar, high-frequency vocabulary.\n\nAssumes: fluent Spanish, no Portuguese.\n\n## Out of scope\nBrazilian-only usage. Business and legal Portuguese.\n\n## Adding\nAsk: offer cards and add them only after a yes.\n\n## Stages\n- `01 Sounds and spelling`: vowels, nasal sounds and how spelling maps to them.\n- `02 Present tense`: regular and common irregular verbs in the present.\n\n## Conventions\n- Note types: `Portuguese · Basic` and `Portuguese · Cloze` (the deck's theme).\n- Tags: `pt::<area>::<topic>`.", "theme": {"deck": "Portuguese", "mood": "warm, unhurried", "subsets": ["latin", "latin-ext"], "fonts": {"body": null, "accent": null}, "light": {"bg": "#FBF3E8", "text": "#3B2316", "accent": "#A24A26", "rule": "#E8CDB4"}, "night": {"bg": "#221A15", "text": "#F3E6D8", "accent": "#F0A07A", "rule": "#4A3A30"}, "motion": false}}}
> ```

**Deck:** the shared mock deck, with this case's own `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `creates-types` | tool check | `create_model` with input matching `"model_name":"Portuguese (·\|\\u00b7) (Basic\|Cloze)"` is called at least 2 times |
| `types-before-charter` | tool check | `create_model` is first called before `update_deck_description` |

### look-change

Changing a theme recovers its spec from the CSS, rebuilds, previews, and applies to both note types only on a yes.

**User message:**

> Make the Spanish deck feel cozier.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `model_names`, `model_styling`.

| grader | kind | passes when |
|---|---|---|
| `rebuilds` | tool check | `Bash` with input matching `build_theme\.py` is called at least once |
| `recovers-and-previews` | LLM judge, reads the transcript | PASS if Claude read the current styling, recovered the theme spec from it (the mood in the comment at the top and the current colors), edited that spec toward cozier, rebuilt it with build_theme.py, showed a preview, and asked before applying it to both `Spanish · Basic` and `Spanish · Cloze`. FAIL if it wrote CSS by hand, started a theme from scratch without reading the current one, applied the change without asking, or planned to change only one of the two note types. |
| `waits-for-yes` | tool check | `update_model_styling` is never called |

### look-choices

Any feeling answer gets two or three distinct theme.json drafts, each built and previewed front and back.

**User message:**

> We're setting up my new Portuguese deck. You already drafted its charter and I approved it:
>
> ## Scope
> European Portuguese for living in Lisbon: everyday conversation, pronunciation, core grammar, high-frequency vocabulary.
>
> Assumes: fluent Spanish, no Portuguese.
>
> ## Out of scope
> Brazilian-only usage. Business and legal Portuguese.
>
> ## Adding
> Ask: offer cards and add them only after a yes.
>
> ## Stages
> - `01 Sounds and spelling`: vowels, nasal sounds and how spelling maps to them.
> - `02 Present tense`: regular and common irregular verbs in the present.
>
> ## Conventions
> - Basic and Cloze.
> - Tags: `pt::<area>::<topic>`.
>
> The sample note was Front "Portuguese: how do you say 'I'm leaving tomorrow'?", Back "<b>Vou embora amanhã.</b>".
>
> Second round: Ask mode, Basic and Cloze. For the feeling question: right now it feels like a chore; I'd like it to feel like sitting in a café in Lisbon.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `builds-each` | tool check | `Bash` with input matching `build_theme\.py` is called at least 2 times |
| `distinct-previews` | LLM judge, reads the final reply | PASS if the reply presents two or three themes that differ in palette and in font pairing (or, where fonts couldn't be used, clearly in palette), each with a preview of the sample note showing both front and back (a preview.html file to open, or the cards drawn inline). FAIL if there is only one theme, the themes differ only slightly, or a theme has no preview or shows only one side. |

### look-cjk

A Japanese deck keeps the system font (both fonts null) and still gets themed colors.

**User message:**

> We're setting up my new Japanese deck. You already drafted its charter and I approved it:
>
> ## Scope
> Japanese for travel and conversation: kana, core kanji, polite speech.
>
> Assumes: no Japanese.
>
> ## Out of scope
> Business keigo.
>
> ## Adding
> Ask.
>
> ## Stages
> - `01 Kana`: hiragana and katakana.
> - `02 Core kanji`: the kanji on signs, menus and stations.
>
> ## Conventions
> - Basic and Cloze.
> - Tags: `ja::<area>::<topic>`.
>
> The sample note was Front "Japanese: how do you say 'Where is the station?'", Back "<b>駅はどこですか。</b>"
>
> Second round: Ask mode, Basic and Cloze. For the feeling question: I'd like it to feel playful.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `builds-themes` | tool check | `Bash` with input matching `build_theme\.py` is called at least 2 times |
| `system-font` | LLM judge, reads the transcript | PASS if every theme.json Claude wrote sets both fonts (body and accent) to null so the device's own Japanese font is used, while the colors still differ between themes and fit the mood. FAIL if any theme names a font family, or the themes are left uncolored. |

### look-contrast

A palette under 4.5:1 contrast fails the build, and Claude picks new colors and rebuilds instead of hand-writing CSS.

**User message:**

> We're setting up my new Portuguese deck. You already drafted its charter and I approved it: Ask mode, Basic and Cloze, stages `01 Sounds and spelling` and `02 Present tense`, tags `pt::<area>::<topic>`. The sample note was Front "Portuguese: how do you say 'I'm leaving tomorrow'?", Back "**Vou embora amanhã.**"
>
> For the look question: I want it to feel light and sunny. Something like pale yellow text on a white background. Build a theme and show me the preview.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `build-refused` | text search | the whole transcript contain `not legible enough` |
| `builds-again` | tool check | `Bash` with input matching `build_theme\\.py` is called at least 2 times |
| `fixes-colors` | LLM judge, reads the final reply | PASS if the reply tells the user that pale yellow on white wasn't legible enough, and presents a rebuilt theme with new colors that keeps the light, sunny feel. FAIL if the reply presents the requested pale yellow on white as built, says it wrote the CSS by hand or bypassed the contrast check, or stops without offering any theme. |

### look-cyrillic

A Russian deck's themes include the cyrillic subset and only families checked to have Cyrillic.

**User message:**

> We're setting up my new Russian deck. You already drafted its charter and I approved it:
>
> ## Scope
> Russian for reading short stories: core grammar, high-frequency vocabulary, verbs of motion.
>
> Assumes: no Russian; I can't read Cyrillic yet.
>
> ## Out of scope
> Handwriting (cursive).
>
> ## Adding
> Ask.
>
> ## Stages
> - `01 Alphabet and sounds`: Cyrillic letters, stress and vowel reduction.
> - `02 Cases`: the six cases and their endings.
>
> ## Conventions
> - Basic and Cloze.
> - Tags: `ru::<area>::<topic>`.
>
> The sample note was Front "Russian: how do you say 'I'm reading a book'?", Back "<b>Я читаю книгу.</b>"
>
> Second round: Ask mode, Basic and Cloze. For the feeling question: I'd like it to feel calm and literary.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `checks-fonts` | tool check | `Bash` with input matching `^(?=.*fetch_font\.py)(?=.*--info)(?=.*([A-Z][a-z]+))` is called at least once |
| `cyrillic-fonts` | LLM judge, reads the final reply | PASS if every font family Claude plans or proposes supports Cyrillic (for example Literata, Lora, Source Serif 4, PT Serif, EB Garamond, IBM Plex Sans; never Fraunces or Atkinson Hyperlegible), and it shows or describes the themes on the Russian sample note. A fetch error that keeps it from checking or building the fonts doesn't count against it, as long as it doesn't present unchecked fonts as ready. FAIL if it plans a family without Cyrillic, presents fonts it never checked as ready to use, or shows the themes only on Latin text. |
| `no-latin-only-font-bash` | tool check | `Bash` with input matching `family[^A-Za-z]{1,8}(Fraunces\|Atkinson)` is never called |
| `no-latin-only-font-write` | tool check | `Write` with input matching `family[^A-Za-z]{1,8}(Fraunces\|Atkinson)` is never called |

### look-fill

Cards for a themed deck use its own Basic or Cloze copy with the stock fields.

**User message:**

> Explain what precision measures for a binary classifier, and when you'd care about it more than recall.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `model_names`.

| grader | kind | passes when |
|---|---|---|
| `no-stock-type` | tool check | `add_notes` with input matching `"model_name":"(Basic\|Cloze)"` is never called |
| `stock-fields` | tool check | `add_notes` with input matching `"fields":\{"(Front\|Text)"` is called at least once |
| `themed-type` | tool check | `add_notes` with input matching `"model_name":"AI Engineering (·\|\\u00b7) (Basic\|Cloze)"` is called at least once |

### look-font-literary

A deck of example sentences gets pairings whose body font is a text serif with italics on.

**User message:**

> We're setting up a new Spanish vocabulary deck. You already drafted its charter and I approved it:
>
> ## Scope
> Spanish vocabulary learned from novels I read, each word carded in the sentence I met it in.
>
> Assumes: B2 Spanish grammar.
>
> ## Out of scope
> Grammar drills (they live in my Spanish deck).
>
> ## Adding
> Ask.
>
> ## Stages
> - `01 Core words`: common words met in reading that I don't know yet.
> - `02 Literary words`: rarer, literary vocabulary.
>
> ## Conventions
> - Cloze on the word in its example sentence; the English gloss in Extra.
> - Tags: `esv::<topic>`.
>
> The sample note was Cloze "Se quedó {{c1::boquiabierto}} al verla entrar." with Extra "open-mouthed, astonished".
>
> Second round: Ask mode, Cloze is right. For the feeling question: I'd like it to feel like reading a novel in a quiet café.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `checks-a-serif` | tool check | `Bash` with input matching `^(?=.*fetch_font\.py)(?=.*--info)(?=.*([Ss]erif\|Literata\|Lora\|Garamond\|Baskerville\|Merriweather\|Crimson\|Spectral\|Alegreya\|Newsreader))` is called at least once |
| `serif-italic-body` | LLM judge, reads the transcript | Look at the body font of every font pairing Claude planned. Judge the font families Claude planned: the ones it wrote into theme.json drafts, checked with `fetch_font.py --info` or named in its reply, whether or not the fetch then worked. If a fetch error made it fall back to the system font, judge the pairing it planned before that. PASS if every planned body font is a serif made for reading text (for example Literata, Source Serif 4, Lora, EB Garamond, PT Serif) with italics on. FAIL if any planned pairing names a sans-serif, monospace or display face for the body, or leaves italics off. |

### look-font-technical

An AI Engineering deck gets pairings with a sans body, at least one with a monospace label.

**User message:**

> We're setting up my new AI Engineering deck. You already drafted its charter and I approved it:
>
> ## Scope
> General AI-engineering knowledge that carries over between projects: concepts, metrics, failure modes, eval techniques, design tradeoffs.
>
> Assumes: working software engineer, basic statistics.
>
> ## Out of scope
> Anything specific to one project. Commands, flags and config syntax.
>
> ## Adding
> Automatic.
>
> ## Stages
> - `01 Classification metrics`: confusion matrix, precision, recall, F1, thresholds.
> - `02 Eval basics`: test sets, run-to-run variation, judging outputs.
>
> ## Conventions
> - Tags: `aie::<area>::<topic>`.
>
> The sample note was Front "Evals: you raise a classifier's threshold. Which goes up: precision or recall?", Back "<b>Precision.</b>"
>
> Second round: Automatic, Basic and Cloze. For the feeling question: I'd like it to feel focused.

**Deck:** the shared mock deck, with this case's own `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `checks-a-mono` | tool check | `Bash` with input matching `^(?=.*fetch_font\.py)(?=.*--info)(?=.*(Mono\|Code\|Courier))` is called at least once |
| `checks-a-sans` | tool check | `Bash` with input matching `^(?=.*fetch_font\.py)(?=.*--info)(?=.*(Sans\|Inter\|Roboto\|Lato\|Manrope\|Figtree))` is called at least once |
| `sans-and-mono` | LLM judge, reads the transcript | Look at every font pairing Claude planned. Judge the font families Claude planned: the ones it wrote into theme.json drafts, checked with `fetch_font.py --info` or named in its reply, whether or not the fetch then worked. If a fetch error made it fall back to the system font, judge the pairing it planned before that. PASS if every planned body font is a sans-serif (for example IBM Plex Sans, Inter) and at least one pairing uses a monospace font for the label (for example IBM Plex Mono, JetBrains Mono). FAIL if any planned pairing names a serif or display face for the body, or none has a monospace label. |

### look-invert

A user who says studying makes them anxious gets calm themes with no motion, and the reply doesn't mirror the anxiety.

**User message:**

> We're setting up my new Portuguese deck. You already drafted its charter and I approved it:
>
> ## Scope
> European Portuguese for living in Lisbon: everyday conversation, pronunciation, core grammar, high-frequency vocabulary.
>
> Assumes: fluent Spanish, no Portuguese.
>
> ## Out of scope
> Brazilian-only usage. Business and legal Portuguese.
>
> ## Adding
> Ask: offer cards and add them only after a yes.
>
> ## Stages
> - `01 Sounds and spelling`: vowels, nasal sounds and how spelling maps to them.
> - `02 Present tense`: regular and common irregular verbs in the present.
>
> ## Conventions
> - Basic and Cloze.
> - Tags: `pt::<area>::<topic>`.
>
> The sample note was Front "Portuguese: how do you say 'I'm leaving tomorrow'?", Back "<b>Vou embora amanhã.</b>".
>
> Second round: Ask mode, Basic and Cloze. For the feeling question: honestly, studying languages makes me anxious.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `aims-at-calm` | LLM judge, reads the transcript | Look at the themes Claude drafted (their theme.json and how it describes them). PASS if every theme aims at calm: quiet, low-saturation colors and motion off, described in terms of how the user would like to feel (calm, steady, unhurried). FAIL if any theme is bright, intense or high-saturation, turns motion on, or is described in terms of anxiety or stress, or if the reply dwells on the user's anxiety instead of designing past it. |
| `builds-themes` | tool check | `Bash` with input matching `build_theme\.py` is called at least 2 times |
| `no-motion` | text search | the whole transcript never contain `motion[^a-z]{1,6}true` |

### look-motion

Motion stays off on a pick until the user says yes after seeing it.

**User message:**

> We're setting up my new Portuguese deck. You already drafted its charter and I approved it:
>
> ## Scope
> European Portuguese for living in Lisbon: everyday conversation, pronunciation, core grammar, high-frequency vocabulary.
>
> Assumes: fluent Spanish, no Portuguese.
>
> ## Out of scope
> Brazilian-only usage. Business and legal Portuguese.
>
> ## Adding
> Ask: offer cards and add them only after a yes.
>
> ## Stages
> - `01 Sounds and spelling`: vowels, nasal sounds and how spelling maps to them.
> - `02 Present tense`: regular and common irregular verbs in the present.
>
> ## Conventions
> - Basic and Cloze.
> - Tags: `pt::<area>::<topic>`.
>
> The sample note was Front "Portuguese: how do you say 'I'm leaving tomorrow'?", Back "<b>Vou embora amanhã.</b>".
>
> Second round: Ask mode, Basic and Cloze. You showed me three themes and I pick this one. Build it.
>
> ```json
> {"deck": "Portuguese", "mood": "warm, unhurried", "subsets": ["latin", "latin-ext"],
>  "fonts": {"body": null, "accent": null},
>  "light": {"bg": "#FBF3E8", "text": "#3B2316", "accent": "#A24A26", "rule": "#E8CDB4"},
>  "night": {"bg": "#221A15", "text": "#F3E6D8", "accent": "#F0A07A", "rule": "#4A3A30"}}
> ```

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `asks-motion` | LLM judge, reads the final reply | PASS if Claude builds the picked theme with motion off and asks whether to turn motion on (the answer fade and the rescued shimmer), leaving it off until the user says yes. FAIL if it turns motion on, or never asks about it. |
| `no-motion` | text search | the whole transcript never contain `motion[^a-z]{1,6}true` |

### look-pairings

Mixing one option's palette with another's fonts gives a theme with A's colors and B's font families, previewed in the deck's language.

**User message:**

> We're setting up my new Spanish deck (charter approved; the sample note was Front "Spanish: how do you say 'I'd been waiting for hours'?", Back "<b>Llevaba horas esperando.</b>"). You showed me these two themes:
>
> Option A, "Lora, warm paper":
> ```json
> {"deck": "Spanish", "mood": "warm", "subsets": ["latin"], "fonts": {"body": {"family": "Lora", "italic": true}, "accent": null},
>  "light": {"bg": "#FBF3E8", "text": "#3B2316", "accent": "#A24A26", "rule": "#E8CDB4"},
>  "night": {"bg": "#221A15", "text": "#F3E6D8", "accent": "#F0A07A", "rule": "#4A3A30"}}
> ```
>
> Option B, "Literata, quiet blue":
> ```json
> {"deck": "Spanish", "mood": "calm", "subsets": ["latin"], "fonts": {"body": {"family": "Literata", "italic": true}, "accent": {"family": "Nunito"}},
>  "light": {"bg": "#F7FAFC", "text": "#1A2733", "accent": "#1F6FB2", "rule": "#D5E1EA"},
>  "night": {"bg": "#111820", "text": "#E6EEF4", "accent": "#7FB6E6", "rule": "#2A3743"}}
> ```
>
> I like option A's colors but option B's fonts. Can you combine them?

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `combined` | LLM judge, reads the final reply | Judge the font families Claude planned: the ones it wrote into theme.json drafts, checked with `fetch_font.py --info` or named in its reply, whether or not the fetch then worked. If a fetch error made it fall back to the system font, judge the pairing it planned before that. PASS if the reply presents a combined theme with option A's colors and option B's fonts (Literata body, Nunito label), named by its fonts and feel (like "Literata, warm paper"), and shows it on the Spanish sample note: a built preview, or the card described or drawn inline if the build couldn't run. FAIL if the combined theme mixes up which colors or fonts came from which option, or the sample shown isn't the Spanish note. |
| `rebuilds` | tool check | `Bash` with input matching `build_theme\.py` is called at least once |

### look-question

Creating a charter asks the look question once, in round two, optional, about both how studying feels and how it should feel.

**User message:**

> Set up an Anki deck for European Portuguese. To save you the first round of questions: I'm moving to Lisbon next spring and need it to live there; I'll learn from sessions with you and review on my phone; I know Spanish well but no Portuguese; I need to both understand and speak it.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `asks-feeling` | LLM judge, reads the transcript | Look at the questions Claude asks the user after drafting the charter (in an AskUserQuestion call or in its reply). PASS if exactly one question is about the deck's look, it is marked optional or skippable, and it asks both how studying this feels and how the user would like it to feel. FAIL if there is no such question, it is asked more than once, it is required, or it asks only one of the two (only the current feeling, or only the wanted one). |
| `no-deck-yet` | tool check | `create_deck` is never called |

### look-repo

Theming a deck whose note types live in a repo proposes a change to the repo's stylesheet, not new or restyled note types.

**User message:**

> Give my Spanish deck a theme. I'd like it to feel like a sunny plaza.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `model_names`.

| grader | kind | passes when |
|---|---|---|
| `no-create` | tool check | `create_model` is never called |
| `no-restyle` | tool check | `update_model_styling` is never called |
| `proposes-repo-change` | LLM judge, reads the final reply | PASS if Claude proposes the theme as a change to the stylesheet in the user's anki-cards repo (the repo that holds the Reconocimiento and Produccion note types), for the user to apply. FAIL if it proposes creating new note types or restyling the note types in Anki directly. |

### look-save

Saving a picked theme creates both note types from models.json, then the deck, with the charter naming them.

**User message:**

> We're setting up my new Portuguese deck. You already drafted its charter and I approved it:
>
> ## Scope
> European Portuguese for living in Lisbon: everyday conversation, pronunciation, core grammar, high-frequency vocabulary.
>
> Assumes: fluent Spanish, no Portuguese.
>
> ## Out of scope
> Brazilian-only usage. Business and legal Portuguese.
>
> ## Adding
> Ask: offer cards and add them only after a yes.
>
> ## Stages
> - `01 Sounds and spelling`: vowels, nasal sounds and how spelling maps to them.
> - `02 Present tense`: regular and common irregular verbs in the present.
>
> ## Conventions
> - Basic and Cloze.
> - Tags: `pt::<area>::<topic>`.
>
> The sample note was Front "Portuguese: how do you say 'I'm leaving tomorrow'?", Back "<b>Vou embora amanhã.</b>".
>
> Second round: Ask mode, Basic and Cloze. You showed me three themes and I pick this one, with motion off. Build it and save the deck.
>
> ```json
> {"deck": "Portuguese", "mood": "warm, unhurried", "subsets": ["latin", "latin-ext"],
>  "fonts": {"body": null, "accent": null},
>  "light": {"bg": "#FBF3E8", "text": "#3B2316", "accent": "#A24A26", "rule": "#E8CDB4"},
>  "night": {"bg": "#221A15", "text": "#F3E6D8", "accent": "#F0A07A", "rule": "#4A3A30"}}
> ```

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `charter-names-types` | tool check | `update_deck_description` with input matching `Portuguese (·\|\\u00b7) Basic[\s\S]*Portuguese (·\|\\u00b7) Cloze\|Portuguese (·\|\\u00b7) Cloze[\s\S]*Portuguese (·\|\\u00b7) Basic` is called at least once |
| `creates-basic` | tool check | `create_model` with input matching `"model_name":"Portuguese (·\|\\u00b7) Basic"` is called at least once |
| `creates-cloze` | tool check | `create_model` with input matching `"model_name":"Portuguese (·\|\\u00b7) Cloze"` is called at least once |
| `from-build` | tool check | `Bash` with input matching `build_theme\.py` is called at least once |
| `models-before-charter` | tool check | `create_model` is first called before `update_deck_description` |

### look-skip

Skipping the look question still gets themes drafted from the subject, with "none" offered.

**User message:**

> We're setting up my new Portuguese deck. You already drafted its charter and I approved it:
>
> ## Scope
> European Portuguese for living in Lisbon: everyday conversation, pronunciation, core grammar, high-frequency vocabulary.
>
> Assumes: fluent Spanish, no Portuguese.
>
> ## Out of scope
> Brazilian-only usage. Business and legal Portuguese.
>
> ## Adding
> Ask: offer cards and add them only after a yes.
>
> ## Stages
> - `01 Sounds and spelling`: vowels, nasal sounds and how spelling maps to them.
> - `02 Present tense`: regular and common irregular verbs in the present.
>
> ## Conventions
> - Basic and Cloze.
> - Tags: `pt::<area>::<topic>`.
>
> The sample note was Front "Portuguese: how do you say 'I'm leaving tomorrow'?", Back "<b>Vou embora amanhã.</b>".
>
> Second round: Ask mode is right, Basic and Cloze are fine, and I'll skip the question about how studying it feels. Carry on.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `builds-themes` | tool check | `Bash` with input matching `build_theme\.py` is called at least 2 times |
| `drafts-and-offers-none` | LLM judge, reads the transcript | PASS if Claude drafts two or three themes based on the subject (Portuguese, Lisbon) even though the user skipped the feeling question, shows them, and offers "none" (keeping Anki's default look) as a choice. FAIL if it drafts no themes, drafts only one, asks the feeling question again, or never offers "none". |

### metric-concept

Teaching an AI-engineering concept in an Automatic deck should produce one-fact, self-contained cards with no arithmetic drills.

**User message:**

> Can you explain precision and recall for a classifier? I get them mixed up. A worked example with numbers would help.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `no-arithmetic-in-calls` | text search | the inputs sent to the mocked Anki tools never contain `TP *= *[0-9]` (case-insensitive) |
| `no-arithmetic` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if no card asks the learner to compute a value from numbers (for example "TP = 8, FP = 2: what is precision?"). FAIL if any card is an arithmetic drill. A card may still contain a formula, as long as it tests what the formula means rather than asking for a calculation. |
| `one-fact-per-card` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if every card's answer (Back, or each cloze blank) is one fact that can be recalled exactly: a word, a number, or one short clause, with any context in an optional Why/Example line. FAIL if any card's answer packs two or more separate facts, a list, or more than one sentence of explanation. |
| `self-contained` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if every card makes sense on its own, shuffled among hundreds of others months later: each term it relies on is either standard in the field or defined in the card, and the question names its options when there are only two or three. FAIL if any card relies on wording or context from the conversation or from another card (for example "which kind?" or "the example above"), or is a telegraphic fragment rather than a complete question. |

### missing-prereq

A card may only rely on concepts the deck already teaches; missing ones are taught first or flagged.

**User message:**

> Explain what an F1 score is, and why it uses a harmonic mean instead of an ordinary average.

**Deck:** the shared mock deck, with this case's own `find_notes`.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `prereqs-handled` | LLM judge, reads the transcript | The deck the cards go into is empty: its find_notes search returned no cards, so it does not yet teach precision, recall or what a harmonic mean is. PASS if the cards added include ones that introduce the concepts the F1 cards rely on (precision, recall, and the harmonic mean, or whichever of these the F1 cards use) before or alongside the F1 cards, OR if the reply clearly tells the user that those prerequisite cards are missing and offers to add them. FAIL if F1 cards rely on precision, recall or the harmonic mean without any card introducing them and without flagging the gap. |

### name-the-options

A two-option idea becomes a card that names both options in its question.

**User message:**

> When should an eval use a code-based check, and when an LLM judge?

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `names-options` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if every card that contrasts two or three options names all of them in its own question or cloze text (for example "...: code or an LLM judge?"), so it works without any other card. FAIL if a card asks "which kind?" or similar without naming the options, or depends on another card to know what the options are. |

### near-neighbor

When the deck holds a similar concept, the new card names what sets it apart, or a contrast card is added.

**User message:**

> Explain precision for a classifier.

**Deck:** the shared mock deck, with this case's own `find_notes`.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `checks-deck` | tool check | `find_notes` is called at least once |
| `distinguishes` | LLM judge, reads the transcript | The deck already holds a card on recall ("Of all the actual positives, what share does the classifier find?"). Look at the cards in every add_notes call. PASS if the precision card's front states what sets precision apart from recall (that it is measured over the items the classifier flagged as positive, not over the actual positives), or a separate card tagged type::contrast names both precision and recall; and no card repeats the existing recall card. FAIL if a precision front could be confused with the recall card in review, or a card duplicates the recall card. |

### no-giveaway

A card's front must not hint at its answer through wording, an obviously right option or a visible cloze.

**User message:**

> Why should you keep a held-out test set instead of measuring your prompt on the same examples you used while tuning it?

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `no-giveaway` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if no card's front gives its answer away: no key word of the answer appears in the question, when options are named none is obviously the right one from its wording alone (for example "the clean set or the contaminated one?"), and no cloze leaves visible text that reveals what goes in the blank. FAIL if any front can be answered from its own wording without knowing the topic. |

### no-lone-cards

A new concept in an Automatic deck gets two to four cards from different angles, not one.

**User message:**

> What is few-shot prompting?

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `two-to-four` | LLM judge, reads the transcript | Look at the cards in every add_notes call. Count the cards about few-shot prompting itself (a Cloze note counts once per blank). PASS if there are two, three or four, and they come from different angles (what it is, why it works, how it differs from a neighbor such as zero-shot or fine-tuning, when to use it). FAIL if there is only one card about few-shot prompting, more than four, or several cards ask the same thing in different words. |

### nt-costs

A note-type proposal that needs script says JavaScript isn't officially supported and asks for a test on every device.

**User message:**

> Set up an Anki deck for Spanish with a note type that blanks the word in its own sentence automatically for the production card. I review on AnkiDroid on my phone. Why: I'm moving to Madrid next year. How: I read novels on my Kindle with lookups and review on my phone. What I know: I'm about B1 and comfortable with the present and past tenses. And I need both to understand Spanish and to speak it. Show me the draft, including the templates.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `costs` | LLM judge, reads the final reply | PASS if the proposal says Anki doesn't officially support JavaScript in templates and asks the user to test the cards on their phone (AnkiDroid) before relying on them, and any script shown is self-contained in one immediately invoked function. FAIL if a scripted template is proposed without that caveat, or a script defines globals outside one IIFE. |
| `no-new-type-yet` | tool check | `create_model` is never called |

### nt-field-change

Adding a field counts the affected notes, warns about the full sync, and waits for a yes.

**User message:**

> Add an Audio field to my Reconocimiento note type.

**Deck:** the shared mock deck, with this case's own `find_notes`, `model_names`.

| grader | kind | passes when |
|---|---|---|
| `counts-notes` | tool check | `find_notes` with input matching `note:` is called at least once |
| `no-change-before-yes` | tool check | `model_field_add` is never called |
| `warns` | LLM judge, reads the final reply | PASS if the reply says how many notes use the type, warns that adding a field makes the next sync a full one, asks the user to sync their other devices first, and asks before making the change. FAIL if it says it already added the field, or leaves out the full-sync warning or the request to sync other devices first. |

### nt-fill

A card in a deck with a custom note type uses the charter's default type and fills its fields as Conventions says.

**User message:**

> I read this in my novel: «No se dio cuenta de que la tienda estaba cerrada.» What does «se dio cuenta» mean here?

**Deck:** the shared mock deck, with this case's own `find_notes`, `get_deck_description`, `list_decks`, `model_names`.

| grader | kind | passes when |
|---|---|---|
| `lema-dictionary-form` | tool check | `add_notes` with input matching `\"Lema\":\\s*\"darse cuenta` is called at least once |
| `no-hint` | tool check | `add_notes` with input matching `\"Pista\` is never called |
| `no-production` | tool check | `add_notes` with input matching `\"model_name\":\\s*\"Produccion\` is never called |
| `palabra-in-sentence` | tool check | `add_notes` with input matching `\"Palabra\":\\s*\"(se dio cuenta\|se\\\|dio cuenta\|dio cuenta)\` is called at least once |
| `sentence-field` | tool check | `add_notes` with input matching `\"Oraci\u00f3n\":\\s*\"No se dio cuenta de que la tienda estaba cerrada` is called at least once |
| `uses-default-type` | tool check | `add_notes` with input matching `\"model_name\":\\s*\"Reconocimiento\` is called at least once |

### nt-move-up

A word the user keeps getting wrong is recommended for production per the charter, and the user is told to move it.

**User message:**

> I keep saying «realizar» when I mean «darse cuenta». Ugh.

**Deck:** the shared mock deck, with this case's own `find_notes`, `get_deck_description`, `list_decks`, `model_names`, `notes_info`.

| grader | kind | passes when |
|---|---|---|
| `move-up` | LLM judge, reads the final reply | The deck has an `Reconocimiento` note for "darse cuenta", and the charter says to move a note to `Produccion` when the user keeps using the wrong word for it. PASS if the reply recommends moving that note to production, drafts a `Pista` for it (a short English gloss such as "to realize, notice"), and tells the user to do the move with Change Note Type in Anki's browser. FAIL if it doesn't suggest moving the note, creates a separate production note instead, or claims it changed the note type itself. |
| `no-duplicate-production` | tool check | `add_notes` with input matching `Produccion` is never called |

### nt-no-leak

In a proposed note type, no card's front shows its own answer.

**User message:**

> Set up an Anki deck for Spanish, with a note type that gives me both a recognition card and a production card from one note. Why: I'm moving to Madrid next year. How: I read novels on my Kindle with lookups and review on my phone. What I know: I'm about B1 and comfortable with the present and past tenses. And I need both to understand Spanish and to speak it. Show me the draft, including the templates.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `no-leak` | LLM judge, reads the final reply | Look at the note type templates Claude proposes, rendered in your head with its sample note. PASS if no card's front shows the answer it asks for (the production front blanks or omits the target word), and the back of a card whose front hides the answer renders the fields itself instead of starting with {{FrontSide}} in a way that would still hide or duplicate the answer. FAIL if a front template includes the field that holds its own answer unmasked, or no templates are shown. |
| `no-new-type-yet` | tool check | `create_model` is never called |

### nt-none

A technical subject with varied card shapes stays on Basic and Cloze.

**User message:**

> Set up an Anki deck for distributed systems. Why: I'm a backend engineer and want to design better systems at work. How: sessions with Claude while I work, reviewed on my phone. What I know: basic networking and databases. I need to understand it well enough to make design decisions. Show me the draft.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `basic-cloze` | LLM judge, reads the final reply | PASS if the draft uses Basic and Cloze, and proposes no custom note type, or considers one and rejects it with a reason. FAIL if it proposes a custom note type for this subject without a reason grounded in a repeated multi-part card shape. |
| `no-new-type` | tool check | `create_model` is never called |
| `no-save` | tool check | `update_deck_description` is never called |

### nt-propose

A subject needing both recognition and production gets a well-designed note type proposed with a sample, not built.

**User message:**

> Set up an Anki deck for Spanish. Why: I'm moving to Madrid next year. How: I read novels on my Kindle with lookups and review on my phone. What I know: I'm about B1 and comfortable with the present and past tenses. And I need both to understand Spanish and to speak it. Show me the draft.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `good-design` | LLM judge, reads the final reply | The collection has only Basic and Cloze. PASS if the reply proposes a note type (or considers one and explains the choice) with one field per part of the card, the answer word stored in a single field that both card views use, a hint field on the production card that makes one answer right, and optional fields hidden when empty; shows a sample note as each of its cards would appear; and asks before creating it. FAIL if a proposed type stores the answer twice, has no hint on the production card, has no sample note, or says the type was created. |
| `no-new-type-yet` | tool check | `create_model` is never called |
| `no-save` | tool check | `update_deck_description` is never called |

### nt-repo

When note types live in a repo, changes are proposed as repo edits, not made in Anki.

**User message:**

> Add a Notas section shown on the back of my Reconocimiento cards. My note types live in my anki-cards git repo and get built into Anki from there.

**Deck:** the shared mock deck, with this case's own `model_names`.

| grader | kind | passes when |
|---|---|---|
| `no-field-add` | tool check | `model_field_add` is never called |
| `no-new-type` | tool check | `create_model` is never called |
| `no-styling-write` | tool check | `update_model_styling` is never called |
| `no-template-write` | tool check | `update_model_templates` is never called |
| `repo-edits` | LLM judge, reads the final reply | PASS if the reply proposes the change as edits to the templates in the user's anki-cards repo (and how to rebuild or apply it), not as a change made directly in Anki. FAIL if it says it changed the note type in Anki, or proposes only an in-Anki change. |

### nt-reuse

When the collection already has fitting note types, the charter reuses them with a default and a move-up rule.

**User message:**

> Set up an Anki deck for Spanish. Why: I'm moving to Madrid next year. How: I read novels on my Kindle with lookups and review on my phone. What I know: I'm about B1 and comfortable with the present and past tenses. And I need both to understand Spanish and to speak it. Show me the draft.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `list_decks`, `model_names`.

| grader | kind | passes when |
|---|---|---|
| `lists-types` | tool check | `model_names` is called at least once |
| `no-new-type` | tool check | `create_model` is never called |
| `no-save` | tool check | `update_deck_description` is never called |
| `reads-types` | tool check | `model_field_names` with input matching `Reconocimiento\|Produccion` is called at least once |
| `reuses` | LLM judge, reads the final reply | The collection already has `Reconocimiento` (recognition) and `Produccion` (production) note types. PASS if the draft charter's Conventions use those existing types, name recognition as the default, say what goes in each field, and give a rule for moving a note up to production. FAIL if it proposes a new note type instead, ignores the existing ones, or leaves out the default or the move-up rule. |

### one-right-answer

A front that several correct answers would fit gets the context that leaves only one.

**User message:**

> What reduces hallucination in RAG systems?

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `one-answer` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if every card's question has exactly one right answer: someone who knows the topic could not give a different answer that is also correct, because the question names the situation, the options, or the specific mechanism it asks about. FAIL if any question (for example "What reduces hallucination in RAG?") admits several correct answers. |

### open-set

Members of an open set are carded by what they do; no card asks for the whole set or for an example of the category.

**User message:**

> What are the common automatic metrics for evaluating generated text, like BLEU, ROUGE and BERTScore? How do they differ?

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `no-example-prompt-in-calls` | tool check | `add_notes` with input matching `\\b([gG][iI][vV][eE]\|[nN][aA][mM][eE]\|[lL][iI][sS][tT]) ([aA][nN]\|[oO][nN][eE]\|[tT][wW][oO]\|[tT][hH][rR][eE][eE]\|[sS][oO][mM][eE]\|[aA] [fF][eE][wW]) ([eE][xX][aA][mM][pP][lL][eE]\|[mM][eE][tT][rR][iI][cC])[sS]?\\b` is never called |
| `no-set-question` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if no card asks for the whole set ("name three text-generation metrics") or for "an example of" a category. Each metric is carded by what it does or measures, or the metric is named and the card asks what it measures or what kind of metric it is. FAIL if any card's answer is a list, or the question has many right answers because it asks for any member of the set. |

### procedure

A procedure is carded at its decision points, not as a sequence of steps or commands.

**User message:**

> Walk me through setting up an eval run for a new prompt version, step by step. What do I do first, and why?

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `decision-points` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if the cards test decisions in the procedure (when to take a step, why it's needed, what goes wrong without it), and none asks for the order of steps or what comes next. FAIL if any card asks for a step's position in the sequence, the next step, or a command or flag. |
| `no-commands-in-calls` | text search | the inputs sent to the mocked Anki tools never contain ` --[a-z][a-z-]+` |
| `no-step-order-in-calls` | tool check | `add_notes` with input matching `[wW][hH][aA][tT] ([cC][oO][mM][eE][sS]\|[dD][oO] [yY][oO][uU] [dD][oO]\|[sS][tT][eE][pP] [cC][oO][mM][eE][sS]) ([nN][eE][xX][tT]\|[aA][fF][tT][eE][rR]\|[fF][iI][rR][sS][tT]\|[bB][eE][fF][oO][rR][eE])\|[wW][hH][iI][cC][hH] [sS][tT][eE][pP]\|\\b[sS][tT][eE][pP] ([oO][nN][eE]\|[tT][wW][oO]\|[tT][hH][rR][eE][eE]\|[0-9])\\b` is never called |

### project-specific

Lessons learned in a project become general cards without the project's names.

**User message:**

> At Acme Health we built a module called packet-segmenter that splits each faxed bundle in the SNF-2025 corpus into its separate documents before extraction runs. Explain why that splitting step matters for extraction accuracy.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `no-project-names-in-calls` | text search | the inputs sent to the mocked Anki tools never contain `acme\|packet-segmenter\|snf-2025` (case-insensitive) |
| `no-project-names` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if no card mentions Acme Health, packet-segmenter, SNF-2025, or any other name specific to this one project, while still teaching the general lesson (for example, that splitting a bundled file into its documents helps extraction). FAIL if any card contains one of those project names. |

### q-how-class

When new material comes from conversation classes, the charter sources cards from phrases met in class.

**User message:**

> Set up an Anki deck for Spanish. Why: I'm moving to Madrid next year. How: I take a weekly conversation class and bring my notes home; I review on my phone. I'm about B1. I need to understand it and speak it. Show me the draft.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `class-shaped` | LLM judge, reads the final reply | PASS if the draft charter's Sources name the weekly conversation class and the user's class notes, and Selection or Conventions favor phrases and expressions used in conversation (with production cards, since the user needs to speak). FAIL if the charter doesn't mention the class as the source, or reads as if material came from the user's reading. |
| `no-save` | tool check | `update_deck_description` is never called |

### q-how-kindle

When new material comes from the user's reading, the charter sources cards from sentences they met there.

**User message:**

> Set up an Anki deck for Spanish. Why: I'm moving to Madrid next year. How: I read novels on my Kindle and look up words as I go; I review on my phone. I'm about B1. I need to understand it and speak it. Show me the draft.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `no-save` | tool check | `update_deck_description` is never called |
| `reading-shaped` | LLM judge, reads the final reply | PASS if the draft charter's Sources say cards come from the user's reading and lookups, and its Conventions or Selection build cards from the sentence the word was met in (for example with a field or note of where it came from). FAIL if the charter doesn't mention reading as the source, or builds vocabulary cards with no sentence from the user's reading. |

### q-no-tool

Setting up a deck starts with the four-question questionnaire, as a numbered list with options, before anything is drafted or written.

**User message:**

> Set up an Anki deck for Spanish.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `no-deck` | tool check | `create_deck` is never called |
| `no-save` | tool check | `update_deck_description` is never called |
| `numbered-list` | LLM judge, reads the final reply | PASS if the reply asks, as a numbered list in one message, why the user is learning Spanish, how they plan to study it, what they already know, and whether they need to understand or produce it, each with a few concrete options, and doesn't draft a charter yet. FAIL if any of the four questions is missing, they aren't a numbered list with options, or a charter is drafted before the answers. |

### q-second-round

The follow-up questions after a draft are few and never repeat the first round.

**User message:**

> Set up an Anki deck for music theory. Why: I play guitar and want to improvise over jazz standards. How: I learn from a jazz theory book chapter by chapter and review on my desktop. What I know: I can read chord symbols and know the major scale. I need to use it while playing, not just understand it. Show me the draft.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `no-save` | tool check | `update_deck_description` is never called |
| `short-second-round` | LLM judge, reads the final reply | The user already answered why, how, what they know, and understand-vs-produce. PASS if, after the draft, Claude asks at most four follow-up questions, about things like Automatic vs Ask, a real note-type choice, or something the draft left open, and none of them asks again why the user is learning, how they study, what they know, or whether they need to understand or apply it. FAIL if it asks more than four follow-ups or repeats any of those first-round questions. |

### q-skip-answered

Questions the user already answered are not asked again.

**User message:**

> Set up a Spanish deck: I'm moving to Madrid next year, I read on my Kindle and review on my phone.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `no-deck` | tool check | `create_deck` is never called |
| `no-save` | tool check | `update_deck_description` is never called |
| `skips` | LLM judge, reads the final reply | The user already said why (moving to Madrid) and how they study (reading on a Kindle, reviewing on a phone). PASS if the questions Claude asks in its reply don't ask why they're learning Spanish or how or where they study, and do ask about what they already know and/or whether they need to understand or produce it. FAIL if Claude asks again why they're learning or how they study. |

### q-traceable

Every questionnaire answer shows up in at least one line of the drafted charter.

**User message:**

> Set up an Anki deck for music theory. Why: I play guitar and want to improvise over jazz standards. How: I learn from a jazz theory book chapter by chapter and review on my desktop. What I know: I can read chord symbols and know the major scale. I need to use it while playing, not just understand it. Show me the draft.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `no-save` | tool check | `update_deck_description` is never called |
| `traceable` | LLM judge, reads the final reply | The user gave four answers: (1) why: improvising over jazz standards on guitar; (2) how: a jazz theory book chapter by chapter, reviewed on desktop; (3) knows chord symbols and the major scale; (4) needs to apply it while playing. PASS if each of the four answers visibly shapes at least one line of the draft charter (for example Scope or Selection for 1, Sources or stages for 2, an Assumes line for 3, card direction or Conventions for 4). FAIL if any answer leaves no trace in the charter. |

### q-why-exam

When the user studies for an exam, the charter's scope and stages follow the syllabus.

**User message:**

> Set up an Anki deck for Python. Why: I'm taking the PCEP certification exam next month. How: I study from the official exam syllabus on my laptop. What I know: I can program in JavaScript. I need to write Python, not just read it. Show me the draft.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `no-save` | tool check | `update_deck_description` is never called |
| `syllabus-shaped` | LLM judge, reads the final reply | PASS if the draft charter ties Scope and the stages to the PCEP exam syllabus (stages follow the syllabus sections, or Selection says a topic earns a card if the syllabus covers it), and treats material outside the exam as out of scope or lower priority. FAIL if the charter would read the same for someone learning Python for their job, with no link to the exam or its syllabus. |

### q-why-work

When the user learns for work, the charter selects by what changes how they work, not by a syllabus.

**User message:**

> Set up an Anki deck for Python. Why: I use it at work every day for data pipelines. How: I learn things in sessions with Claude while working and review on my phone. What I know: the basics, I've used it for a year. I need to write it. Show me the draft.

**Deck:** the shared mock deck, with this case's own `get_deck_description`, `list_decks`.

| grader | kind | passes when |
|---|---|---|
| `no-save` | tool check | `update_deck_description` is never called |
| `work-shaped` | LLM judge, reads the final reply | PASS if the draft charter selects topics by what changes how the user writes Python at work (for example idioms, pitfalls and design choices met while building data pipelines), its Sources name sessions with Claude, and it doesn't organize around an exam syllabus or a beginner course. FAIL if the charter is organized like a course or syllabus, or Selection says nothing about relevance to the user's work. |

### regression

Known-bad drafts are rewritten into the reviewed good shapes, and paired-relationship clozes are left alone.

**User message:**

> Here are some cards I drafted for my AI Engineering deck. Fix whatever's wrong with them and add them:
>
> 1. Q: What is pooled recall? A: A label-free technique where the union of several systems' outputs is treated as a pseudo answer key, so recall can be estimated without gold labels, at the cost of missing items no system found.
> 2. Q: Grounding vs attribution? A: Grounding means the output is supported by the source; attribution means pointing to which part of the source supports it.
> 3. Q: Which eval step is expensive and which is cheap: inference or scoring?
> 4. Q: A cache key for saved model outputs must include what, beyond model and settings?
> 5. Cloze: Raising a classifier's threshold makes precision {{c1::rise}} and recall {{c2::fall}}.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `good-shapes` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if all of these hold: the pooled-recall card's answer is one short fact (for example what serves as the pseudo answer key); grounding vs attribution is a single paired Cloze note or split cards, not one card with a paragraph answer; the inference/scoring card asks which one costs more; the cache-key card is a concrete scenario with a one-clause answer (a version or hash of the prompt); and the threshold Cloze keeps both blanks in one note rather than being split or flagged as a giveaway. FAIL if any rewritten card still has a multi-sentence answer, asks two things at once, or the threshold note was split into two notes. |

### rescued-tag

A stage rebuild tags each rewritten leech `rescued` in the plan.

**User message:**

> Rebuild stage 01 Classification metrics of my AI Engineering deck. Write the plan for me to review; don't apply anything yet.

**Deck:** the shared mock deck, with this case's own `find_notes`, `notes_info`.

| grader | kind | passes when |
|---|---|---|
| `searches-problem-cards` | tool check | `find_notes` with input matching `tag:leech\|tag:marked` is called at least once |
| `tags-rescued` | LLM judge, reads the transcript | Look at the stage plan Claude wrote. Notes 1001 and 1002 are leeches; 1003 is not. PASS if every leech the plan rewrites carries the `rescued` tag in the plan, and a leech the plan keeps unchanged apart from a new mnemonic is not required to have it. FAIL if a rewritten leech lacks the `rescued` tag, or the plan applies changes instead of only writing them for review. |

### restate-then-draft

A multi-point explanation becomes cards that each test exactly one point.

**User message:**

> Explain prompt caching to me: what gets cached, why the cached prefix has to be byte-identical, why it cuts latency, why it cuts cost, and what invalidates the cache.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `one-point-each` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if each card tests exactly one point (what is cached, why the prefix must match exactly, the latency benefit, the cost benefit, what invalidates the cache), and no card's answer combines two of them. FAIL if any card's answer covers two or more of those points, or packs a list. |

### source-question

Cards about something read in an article ask about the subject, never about what the article said.

**User message:**

> I just read a blog post arguing that prompt injection can't be fixed by adding more instructions to the system prompt. Explain why that's true.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `about-subject` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if every card asks about prompt injection itself (why instructions can't fix it, what makes it possible), and none asks what the post or its author said, argued or recommended. FAIL if any card's question is about the article rather than the subject. |
| `adds-cards` | tool check | `add_notes` is called at least once |
| `no-source-in-calls` | tool check | `add_notes` with input matching `([pP][oO][sS][tT]\|[aA][rR][tT][iI][cC][lL][eE]\|[bB][lL][oO][gG]\|[aA][uU][tT][hH][oO][rR]\|[eE][sS][sS][aA][yY])\\b[^\\\"]{0,80}\\b([aA][rR][gG][uU][eE]\|[sS][aA][yY]\|[cC][lL][aA][iI][mM]\|[rR][eE][cC][oO][mM][mM][eE][nN][dD]\|[sS][uU][gG][gG][eE][sS][tT])\|[aA][cC][cC][oO][rR][dD][iI][nN][gG] [tT][oO] [tT][hH][eE] ([pP][oO][sS][tT]\|[aA][rR][tT][iI][cC][lL][eE]\|[aA][uU][tT][hH][oO][rR]\|[bB][lL][oO][gG])` is never called |

### stale-fact

An answer that depends on a date, model or benchmark says so in the question, or the card tests the durable principle instead.

**User message:**

> How big are the context windows of current frontier models, and does a huge context window make retrieval (RAG) unnecessary?

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `stamped` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if every card whose answer depends on a particular model, version, vendor, date or benchmark result says so in the question ("As of 2026, …", "For model X, …") and carries a src:: tag; or the cards test the durable principle (for example why long context doesn't replace retrieval) and leave model-specific numbers out. FAIL if any card states a context-window size or another fast-changing figure without dating or attributing it in the question. |

### support-missing

A card whose answer the source passage doesn't state is not added, even when the fact is true.

**User message:**

> Make cards from this passage of the original chain-of-thought paper. Also add one on which company's researchers wrote the paper.
>
> > Chain-of-thought prompting does not positively impact performance for small models, and only yields performance gains when used with models of about 100B parameters. Smaller models wrote fluent but illogical chains of thought, which led to lower accuracy than standard prompting.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `no-unsupported-in-calls` | text search | the inputs sent to the mocked Anki tools never contain `Google\|Brain\|DeepMind` (case-insensitive) |
| `says-why` | LLM judge, reads the final reply | The user asked for a card on who wrote the paper, which the passage they gave doesn't say. PASS if the reply says that card wasn't added because the passage doesn't state it. FAIL if the reply reports such a card as added, or drops it without saying why. |

### support-reversed

A drafted card that reverses what its source passage says is held and shown to the user, not added or reworded to fit.

**User message:**

> This is from the original chain-of-thought paper:
>
> > Chain-of-thought prompting does not positively impact performance for small models, and only yields performance gains when used with models of about 100B parameters. Smaller models wrote fluent but illogical chains of thought, which led to lower accuracy than standard prompting.
>
> Add these two cards to AI Engineering:
>
> 1. Q: In the original chain-of-thought paper, which models gained most from chain-of-thought prompting: small ones or ones around 100B parameters? A: Ones around 100B parameters.
> 2. Q: In the original chain-of-thought paper, why did chain-of-thought prompting help small models most? A: It made up for their weaker reasoning.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-supported` | tool check | `add_notes` is called at least once |
| `flags-reversed` | LLM judge, reads the final reply | The user asked for two cards from a quoted passage. Card 2 contradicts the passage: the passage says chain-of-thought did not help small models. PASS if the reply says card 2 isn't supported by (or contradicts) the passage and wasn't added. FAIL if the reply reports card 2 as added, or doesn't mention the problem with it. |
| `no-reversed-in-calls` | text search | the inputs sent to the mocked Anki tools never contain `help small models most\|made up for their weaker reasoning` (case-insensitive) |

### variety-image-giveaway

A diagram whose visible label gives away the answer is not put on the card's front.

**User message:**

> I drew this diagram. Make a card with it on the front that asks what kind of curve it is.
>
> <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 200"><rect width="220" height="200" fill="white"/><text x="110" y="18" text-anchor="middle" font-size="14">Precision-Recall curve</text><line x1="30" y1="170" x2="200" y2="170" stroke="black"/><line x1="30" y1="170" x2="30" y2="30" stroke="black"/><text x="115" y="192" text-anchor="middle" font-size="11">Recall</text><text x="12" y="100" font-size="11" transform="rotate(-90 12 100)">Precision</text><path d="M30 40 C 90 45, 150 70, 200 160" fill="none" stroke="steelblue" stroke-width="2"/></svg>

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `giveaway-rejected` | LLM judge, reads the transcript | The user's diagram has the title "Precision-Recall curve" and axes labeled Precision and Recall, and they asked for a card with it on the front asking what kind of curve it is. Look at the reply and at every add_notes and store_media_file call. PASS if no card shows the labeled diagram on its front with that question: the reply says the labels give the answer away, and either the diagram is stored and used without the title and axis labels, or it moves to the back, or the card waits for an unlabeled version. FAIL if a card's front shows the diagram with its title or axis labels and asks what the curve is, or the reply doesn't mention that the labels give the answer away. |
| `no-label-on-front` | text search | the inputs sent to the mocked Anki tools never contain `Front\\\\?\"\\s*:\\s*\\\\?\"((?!Back)[^}])*Precision-Recall` (case-insensitive) |

### variety-mnemonic

A mnemonic is offered for an arbitrary fact and not for a fact the learner can reason out.

**User message:**

> Explain BLEU: why it has a brevity penalty, and the longest n-gram the standard version counts.

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `mnemonic-offered` | LLM judge, reads the transcript | Two facts were taught: the standard BLEU counts n-grams up to length 4 (arbitrary: it has to be remembered), and the brevity penalty exists because n-gram precision alone rewards very short outputs (it can be reasoned out). PASS if the final reply offers one or more mnemonics for the n-gram length (or for BLEU's arbitrary details) for the user to pick from, and offers none for the brevity penalty. FAIL if no mnemonic is offered for the n-gram length, or one is offered for the brevity penalty. |
| `not-added-unasked` | text search | the inputs sent to the mocked Anki tools never contain `[mM]nemonic` |

### variety-none

A charter with "Variety: none" keeps every new card in the deck's one format.

**User message:**

> Today I read «el atardecer» in a novel: "Paseamos por la playa hasta el atardecer." What does it mean?

**Deck:** the shared mock deck, with this case's own `find_notes`, `get_deck_description`.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `only-reconocimiento` | tool check | `add_notes` with input matching `model_name\\\\?\"\\s*:\\s*\\\\?\"(?!Reconocimiento)` is never called |
| `uniform` | LLM judge, reads the transcript | The Spanish charter says "Variety: none. Every card stays a Reconocimiento note." Look at every add_notes call. PASS if every note added is a Reconocimiento note for «atardecer», filled as the charter says, and no Cloze, Basic, scenario or extra variant is added to vary the deck. FAIL if any note uses another note type, or a second card in another shape is added for variety. |

### variety-one-shape

Content with one right shape keeps it even when that shape is the deck's most common format.

**User message:**

> What's the formula for character error rate (CER)?

**Deck:** the shared mock deck, with this case's own `find_notes`.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `formula-is-cloze` | tool check | `add_notes` with input matching `\\{\\{c1::` is called at least once |
| `not-forced` | LLM judge, reads the transcript | The deck holds 200 notes, 190 of them Cloze formula cards, and the user asked for the CER formula. Look at the cards in every add_notes call. PASS if the formula itself is carded as a Cloze (CER = character edit distance ÷ reference length, or the same with substitutions, deletions and insertions), whatever other cards come with it. FAIL if the formula is turned into another shape only to vary the deck (a scenario or Basic card that asks for the formula less directly, a calculation drill), or isn't carded at all. |

### variety-scenario

In a deck where 95% of notes are plain definitions, content that fits a definition or a scenario equally well gets a scenario.

**User message:**

> Explain what data leakage between the training set and the test set does to an eval score.

**Deck:** the shared mock deck, with this case's own `find_notes`.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `scenario-chosen` | LLM judge, reads the transcript | The deck holds 200 notes, 190 of them plain definition cards. Look at the cards in every add_notes call. PASS if at least one card about data leakage is a concrete scenario (a situation the learner is in, such as a suspiciously high test score, then a question about what happened or what to do), and every card still tests one point without giving its answer away. FAIL if every data-leakage card is a plain definition ("What is data leakage?", "What is it called when..."), or a scenario card is worse than a definition would have been (vague, several points, answer in the front). |
| `scenario-in-calls` | text search | the inputs sent to the mocked Anki tools contain `type::(application\|scenario)` |

### yes-no-rewrite

A fact that invites a yes/no question becomes a what, why or which question.

**User message:**

> Does setting temperature to 0 guarantee identical LLM outputs across runs? Why or why not?

**Deck:** the shared mock deck.

| grader | kind | passes when |
|---|---|---|
| `adds-cards` | tool check | `add_notes` is called at least once |
| `no-yes-no-in-calls` | tool check | `add_notes` with input matching `\"(Front\|Text)\":\\s*\"(?:[^\"]{0,40}: )?(?:<b>)?(Does\|Is\|Are\|Can\|Could\|Will\|Would\|Should\|Do\|Must\|Has\|Have)\\b` is never called |
| `no-yes-no` | LLM judge, reads the transcript | Look at the cards in every add_notes call. PASS if no card's question can be answered with yes or no; each asks what, why, which or how. FAIL if any card's question is a yes/no question (for example "Does temperature 0 make outputs identical?"). |
<!-- generated:end -->
