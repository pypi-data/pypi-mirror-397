# {{ title }}

* Status: {{ status }} <!-- proposed, accepted, rejected, deprecated, superseded -->
* Date: {{ date }}
{% if authors %}* Authors: {{ authors | join(', ') }}{% endif %}
{% if supersedes %}* Supersedes: {{ supersedes | join(', ') }}{% endif %}
{% if superseded_by %}* Superseded by: {{ superseded_by }}{% endif %}

## Context and Problem Statement

<!-- What is the issue that we're seeing that is motivating this decision or change? -->

## Decision

<!-- What is the change that we're proposing and/or doing? -->

## Consequences

<!-- What becomes easier or more difficult to do because of this change? -->

### Positive

<!-- What becomes easier or better? -->

### Negative

<!-- What becomes more difficult or worse? -->

## Considered Alternatives

<!-- What other options did we consider? -->

* Option 1: <!-- description -->
* Option 2: <!-- description -->
* Option 3: <!-- description -->

## More Information

<!-- Links, references, etc. -->
