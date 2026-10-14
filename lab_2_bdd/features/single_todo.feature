Feature: Retrieve a single To-Do item
  As a user of the API,
  I want to be able to retrieve a specific to-do item by its ID,
  so that I can view its details.

  Scenario: A to-do item exists
    Given the API has a to-do with id 2 and task "Build a Flask API"
    When the user requests the to-do with id 2
    Then the response status code should be 200
    And the response should contain the details of the to-do with id 2

  Scenario: A to-do item does not exist
    Given the API has a list of to-dos
    When the user requests the to-do with id 99
    Then the response status code should be 404
    And the response should contain a "not found" error message
