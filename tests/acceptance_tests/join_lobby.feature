Feature: A party can be created an joined via a party code
    Scenario Outline: A user wants to create a party
        Given that I am on the index page
        When I press the 'Create New Party' button
        Then a new party is created
        And I join the party as the host.

    Scenario Outline: A user want to join an existing party
        Given that I am on the index page
        And a host has created a party
        And I know the party code
        When I submit the party code
        Then I join the party.

    Scenario Outline: A user types an incorrect party code
        Given that I am on the index page
        When I type in an invalid party code
        Then I am given an error.