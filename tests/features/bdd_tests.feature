Feature: retoracle
    retoracle application

    Scenario: Anonymouns user can see About page
        Given a user
        When I click the About button
        Then I see the About page

    Scenario: Anonymous user can click reTOracle button
        Given a user
        When I click the reTOracle button
        Then I see the page refreshes

