Feature: Host ends current active match
    Scenario Outline: Using end and poll-end api calls
        Given the party is currently in a match
        And I am the host of the party
        When I press the 'end match' button
        Then the match ends
        And all gladiators are moved to the status page.