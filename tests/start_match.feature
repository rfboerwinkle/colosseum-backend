Feature: The host can start match
    Scenario Outline: A host wants to start a match
        Given that I am in a party
        And I am the host
        When I press the 'start match' button
        Then the party moves into the coding phase.
