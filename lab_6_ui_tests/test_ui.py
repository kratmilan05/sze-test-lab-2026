import unittest
import time
import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

pytestmark = pytest.mark.ui

class TodoUITest(unittest.TestCase):

    def setUp(self):
        """
        Runs before every test case.
        Starts the browser and loads the page.
        """
        # Automatically downloads and sets up chromedriver
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        
        # The full path to the index.html file.
        # Change this if index.html is located elsewhere!
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "index.html"))
        self.driver.get(f"file://{file_path}")

    def tearDown(self):
        """
        Runs after every test case.
        Closes the browser.
        """
        self.driver.quit()

    def test_1_page_load_and_initial_todos(self):
        """
        Tests if the page loads and initial todos are displayed.
        Assumes the Flask app is running and starts with 2 todos.
        """
        print("Test 1: Page Load and Initial Todos")
        # ATTENTION: The AI-generated code might use different selectors!
        # Update the "todo-list" ID if necessary.
        list_selector = (By.ID, "todo-list")
        
        # Wait max 5 seconds for the list element to appear
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(list_selector)
        )

        # Wait for the loader to disappear
        WebDriverWait(self.driver, 5).until(
            EC.invisibility_of_element_located((By.ID, "loader"))
        )
        
        # Wait until the list contains at least 2 elements (from the API)
        # This assumes the <li> elements are direct children of the list.
        WebDriverWait(self.driver, 5).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "#todo-list li")) >= 2
        )
        
        todos = self.driver.find_elements(By.CSS_SELECTOR, "#todo-list li")
        self.assertGreaterEqual(len(todos), 2)
        print("Success: Initial todos loaded.")

    def test_2_add_new_todo(self):
        """
        Tests adding a new todo.
        """
        print("Test 2: Add New Todo")
        # UPDATED Selectors for the new HTML
        input_selector = (By.ID, "todo-input")
        button_selector = (By.ID, "add-todo-btn")
        list_selector = (By.ID, "todo-list")

        # Find the elements
        task_input = self.driver.find_element(*input_selector)
        add_button = self.driver.find_element(*button_selector)
        
        # Get the number of todos before adding
        initial_count = len(self.driver.find_elements(By.CSS_SELECTOR, "#todo-list li"))

        # Add a new todo
        new_task_name = "New test todo"
        task_input.send_keys(new_task_name)

        # --- JAVÍTÁS 1: Race Condition elkerülése ---
        # Várunk, amíg az input mező értéke (value) tényleg a teljes szöveg.
        # Ez megakadályozza, hogy a teszt rákattintson, mielőtt a send_keys befejeződne.
        WebDriverWait(self.driver, 2).until(
            EC.text_to_be_present_in_element_value(input_selector, new_task_name)
        )
        
        # Most már biztonságos várni a gomb engedélyezésére
        WebDriverWait(self.driver, 2).until(
            EC.element_to_be_clickable(button_selector)
        )
        add_button.click()

        # Várunk, amíg az új elem megjelenik a listában (a lista elemszáma megnő)
        WebDriverWait(self.driver, 5).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "#todo-list li")) > initial_count
        )

        # --- JAVÍTÁS 2: A sorbarendezés kezelése ---
        # Nem ellenőrizhetjük a "last-child"-ot, mert a lista rendezve van.
        # Helyette lekérjük az összes teendő szövegét és megnézzük, benne van-e az új.
        all_task_texts = [el.text for el in self.driver.find_elements(By.CSS_SELECTOR, "#todo-list li .task-text")]
        self.assertIn(new_task_name, all_task_texts)
        print("Success: New todo added.")

    def test_3_complete_todo(self):
        """
        Tests marking a todo as "done" (checkbox).
        This test is heavily modified as the HTML uses a clickable div and CSS classes, not a checkbox.
        """
        print("Test 3: Complete Todo")
        # UPDATED: We now look for the clickable div, not a checkbox
        first_todo_li_selector = (By.CSS_SELECTOR, "#todo-list li:first-child")
        toggle_selector = (By.CSS_SELECTOR, "#todo-list li:first-child .toggle-check")
        
        # Wait for the first todo (and the toggle div in it) to appear
        toggle_element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(toggle_selector)
        )
        
        # Find the parent <li> element to check its class
        first_li = self.driver.find_element(*first_todo_li_selector)
        
        # Save the initial state by checking for the 'done' class
        initial_state = "done" in first_li.get_attribute("class")
        
        # Click the toggle element
        toggle_element.click()
        
        # Wait a bit for the API call and DOM update
        time.sleep(1) # Simpler than writing a complex condition for the PUT call

        # Get the element again (the DOM might have refreshed)
        first_li_after = self.driver.find_element(*first_todo_li_selector)
        
        # Check if its state (class) has changed
        final_state = "done" in first_li_after.get_attribute("class")
        
        self.assertNotEqual(initial_state, final_state)
        print(f"Success: Todo state changed (was done: {initial_state}, is done: {final_state}).")

    def test_4_delete_todo(self):
        """
        Tests deleting a todo.
        """
        print("Test 4: Delete Todo")
        # ATTENTION: The selector (e.g., 'delete-btn' class) might change!
        # This test clicks the delete button of the first todo.
        
        list_selector_css = "#todo-list li"
        
        # Wait until there is at least one element in the list
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, list_selector_css))
        )
        
        initial_count = len(self.driver.find_elements(By.CSS_SELECTOR, list_selector_css))
        self.assertGreater(initial_count, 0, "There are no todos in the list before the delete test.")

        # The new HTML uses .delete-btn class, so the original selector is correct.
        # We remove the try/except block as the XPath fallback is no longer valid (button has no text).
        delete_button_selector = (By.CSS_SELECTOR, "#todo-list li:first-child .delete-btn") # Example selector
        
        delete_button = self.driver.find_element(*delete_button_selector)
        
        # We might need to hover to make the button visible, although Selenium often doesn't require this.
        # Let's click it directly.
        delete_button.click()

        # Wait for the element to disappear from the list (list count decreases)
        WebDriverWait(self.driver, 5).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, list_selector_css)) < initial_count
        )

        final_count = len(self.driver.find_elements(By.CSS_SELECTOR, list_selector_css))
        self.assertEqual(final_count, initial_count - 1)
        print("Success: Todo deleted.")


if __name__ == "__main__":
    unittest.main()