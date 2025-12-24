
You can watch a Jira instance and then ask a question to Coauthor by creating a
comment. You can also use Coauthor to update the summary and description of
tickets.

#### Comments

The `jira` watcher enables Coauthor to monitor Jira issues for comments that
require attention, such as questions directed at it.

There are two supported approaches:

- *Legacy (unanswered-comment detection)*: uses a dedicated Jira user
  configured via the environment variables `COAUTHOR_JIRA_USERNAME` and
  `COAUTHOR_JIRA_PASSWORD`. Coauthor uses this username to detect whether it has
  already replied.

- *Rule-based (recommended)*: selects issues using one or more configured JQL
  rules under `workflows[].watch.jira.comments[]`.

  - Selection is done via the rule's `query` (any valid JQL; often label-based).
  - Coauthor will only process an issue if the *last comment* matches one of the
    configured `content_patterns`. This provides "unanswered" semantics without
    relying on a dedicated Jira user.
  - After processing, Coauthor can automatically update issue labels using the
    rule's `add_labels` and `remove_labels`.

To trigger Coauthor, add a comment in Jira that matches one or more configured
content patterns (regular expressions). For example, if `COAUTHOR_JIRA_USERNAME`
is set to `coauthor`, mentioning `@coauthor` in a comment adds a tag like
`[~coauthor]`, which can be matched via regex.

To configure the Jira base URL you can use the environment variable
`COAUTHOR_JIRA_URL` or you can add the URL to the `.coauthor.yml` configuration
file using `workflows[].watch.jira.url` key.

##### Example: rule-based watcher

```yaml
workflows:
  - name: jira
    content_patterns:
      - "@ai: "
    watch:
      jira:
        comments:
          - query: >-
              project = C2 AND component = COAUTHOR
              AND (updated >= -0.35h OR created >= -0.35h)
            add_labels: [coauthor-comments]
        tickets:
          - query: project = C2 AND component = COAUTHOR AND labels in (rfai)
            add_labels: [rfr]
            remove_labels: [rfai]
            assign_to_creator: false
        sleep: 10
    tasks:
      - id: ticket
        type: ai
```

##### Example: legacy watcher

```yaml
workflows:
  - name: jira
    content_patterns:
      - '\[~coauthor\]'
    watch:
      jira:
        url: https://www.example.com/jira/
        query: updated >= -0.35h OR created >= -0.35h
        sleep: 10
    tasks:
      - id: ticket
        type: ai
```

You must also provide system and user message templates in
`.coauthor/templates/jira/system.md` and `.coauthor/templates/jira/user.md`.

#### Updating Tickets

Currently, updates to Jira tickets are limited to two fields: `summary` and
`description`.

To trigger Coauthor to do the work in *rule-based mode*, configure a
`workflows[].watch.jira.tickets[]` rule with a JQL query.

To trigger Coauthor to do the work in *legacy mode*, assign the ticket in Jira
to the dedicated Coauthor user (the `COAUTHOR_JIRA_USERNAME`).
