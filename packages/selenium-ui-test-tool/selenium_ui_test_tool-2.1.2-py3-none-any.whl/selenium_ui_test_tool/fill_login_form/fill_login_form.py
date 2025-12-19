from selenium_ui_test_tool import configure_actions, get_env_var
from selenium_ui_test_tool.fill_input.fill_input import fill_input


def fill_login_form(driver, username_env="LOGIN_USERNAME", password_env="LOGIN_PASSWORD", by="id", btn_by="test", username_selector="username", password_selector="password", button_selector="test"):
    try:
        username = get_env_var(username_env)
        password = get_env_var(password_env)

        fill_input(driver, by, username_selector, username)
        fill_input(driver, by, password_selector, password)

        configure_actions(driver, btn_by, button_selector)

        if configure_actions:
            print("Connexion réussie")

        return True

    except Exception as e:
        print(f"⚠️ Erreur lors du remplissage du formulaire: {e}")
        return False
